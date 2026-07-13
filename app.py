from flask import Flask, render_template, request
import pickle
import numpy as np
import pandas as pd
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_path(filename):
    return os.path.join(BASE_DIR, filename)

# Load trained artifacts
with open(get_path('loan_model.pkl'), 'rb') as f:
    model = pickle.load(f)

with open(get_path('scaler.pkl'), 'rb') as f:
    scaler = pickle.load(f)

with open(get_path('feature_cols.pkl'), 'rb') as f:
    FEATURE_COLS = pickle.load(f)

print(f"Loaded loan model. Features required: {FEATURE_COLS}")

@app.route('/')
def home():
    # Renders the main dashboard with form, analytics, and overview tabs
    return render_template('home.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Extract fields from form
        gender = int(request.form['gender'])
        married = int(request.form['married'])
        dependents = int(request.form['dependents'])
        education = int(request.form['education'])
        self_employed = int(request.form['self_employed'])
        applicant_income = float(request.form['applicant_income'])
        coapplicant_income = float(request.form['coapplicant_income'])
        loan_amount_raw = float(request.form['loan_amount'])
        loan_amount_term = float(request.form['loan_amount_term'])
        credit_history = float(request.form['credit_history'])
        property_area = int(request.form['property_area'])

        # Preprocess LoanAmount (the model was trained on LoanAmount in thousands)
        loan_amount_thousands = loan_amount_raw / 1000.0

        # Build feature DataFrame matching model.py column order and names
        features_dict = {
            'Gender': [gender],
            'Married': [married],
            'Dependents': [dependents],
            'Education': [education],
            'Self_Employed': [self_employed],
            'ApplicantIncome': [applicant_income],
            'CoapplicantIncome': [coapplicant_income],
            'LoanAmount': [loan_amount_thousands],
            'Loan_Amount_Term': [loan_amount_term],
            'Credit_History': [credit_history],
            'Property_Area': [property_area]
        }
        
        features_df = pd.DataFrame(features_dict)[FEATURE_COLS]
        
        # Scale features
        features_scaled = scaler.transform(features_df)
        
        # Run inference
        prediction = model.predict(features_scaled)[0]  # 1 = Y (Approved), 0 = N (Rejected)
        probabilities = model.predict_proba(features_scaled)[0]
        
        prob_approved = round(probabilities[1] * 100, 1)
        prob_rejected = round(probabilities[0] * 100, 1)
        
        result = 'APPROVED' if prediction == 1 else 'REJECTED'
        color = 'green' if prediction == 1 else 'red'
        
        # Format values for readability in results page
        details = {
            'gender': 'Male' if gender == 1 else 'Female',
            'married': 'Yes' if married == 1 else 'No',
            'dependents': '3+' if dependents == 3 else str(dependents),
            'education': 'Graduate' if education == 1 else 'Not Graduate',
            'self_employed': 'Yes' if self_employed == 1 else 'No',
            'applicant_income': f"${applicant_income:,.2f}",
            'coapplicant_income': f"${coapplicant_income:,.2f}",
            'loan_amount': f"${loan_amount_raw:,.2f}",
            'loan_amount_term': f"{int(loan_amount_term)} Months ({int(loan_amount_term/12)} Years)" if loan_amount_term % 12 == 0 else f"{int(loan_amount_term)} Months",
            'credit_history': 'Meets Guidelines (Good)' if credit_history == 1.0 else 'Does Not Meet Guidelines (Poor)',
            'property_area': 'Rural' if property_area == 0 else 'Semiurban' if property_area == 1 else 'Urban',
            'prob_approved': prob_approved,
            'prob_rejected': prob_rejected
        }
        
        return render_template('result.html', result=result, color=color, details=details)
        
    except Exception as e:
        return (
            f'<div style="color:red; font-family:sans-serif; padding:2rem; background:#111827; height:100vh;">'
            f'<h3>Error Processing Underwriting Request</h3><p>{str(e)}</p></div>'
        )

if __name__ == '__main__':
    app.run(debug=True)
