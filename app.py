from flask import Flask, render_template, request, jsonify, Response
import pickle
import numpy as np
import pandas as pd
import io
import os

app = Flask(__name__)

# Load model if exists
MODEL_PATH = os.path.join('model', 'smart_lender_model.pkl')

def load_model():
    if os.path.exists(MODEL_PATH):
        with open(MODEL_PATH, 'rb') as f:
            return pickle.load(f)
    return None

model = load_model()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['GET'])
def predict_page():
    return render_template('predict.html')

@app.route('/api/predict', methods=['POST'])
def predict():
    global model
    try:
        data = request.get_json()

        # Extract and encode features
        gender = 1 if data.get('gender') == 'Male' else 0
        married = 1 if data.get('married') == 'Yes' else 0
        dependents = data.get('dependents', '0')
        dependents = 3 if dependents == '3+' else int(dependents)
        education = 1 if data.get('education') == 'Graduate' else 0
        self_employed = 1 if data.get('self_employed') == 'Yes' else 0
        applicant_income = float(data.get('applicant_income', 0))
        coapplicant_income = float(data.get('coapplicant_income', 0))
        loan_amount = float(data.get('loan_amount', 0))
        loan_term = float(data.get('loan_term', 360))
        credit_history = float(data.get('credit_history', 1))
        property_area = {'Rural': 0, 'Semiurban': 1, 'Urban': 2}.get(data.get('property_area', 'Urban'), 2)

        features = np.array([[gender, married, dependents, education, self_employed,
                               applicant_income, coapplicant_income, loan_amount,
                               loan_term, credit_history, property_area]])

        if model is None:
            model = load_model()

        if model is None:
            # Fallback: rule-based prediction for demo
            score = 0
            if credit_history == 1: score += 40
            if applicant_income > 3000: score += 20
            if loan_amount < 200: score += 15
            if education == 1: score += 10
            if married == 1: score += 5
            if coapplicant_income > 0: score += 10
            approved = score >= 55
            confidence = min(95, score + 20) if approved else max(20, 100 - score - 20)
            return jsonify({
                'approved': approved,
                'confidence': confidence,
                'message': 'Loan Approved! ✓' if approved else 'Loan Not Approved',
                'risk_level': 'Low Risk' if score >= 70 else 'Medium Risk' if score >= 55 else 'High Risk',
                'model_used': 'Rule-Based (train model first)'
            })

        prediction = model.predict(features)[0]
        proba = model.predict_proba(features)[0]
        confidence = round(max(proba) * 100, 1)

        approved = prediction == 1
        risk_level = 'Low Risk' if confidence > 80 else 'Medium Risk' if confidence > 60 else 'High Risk'

        return jsonify({
            'approved': approved,
            'confidence': confidence,
            'message': 'Loan Approved! ✓' if approved else 'Loan Not Approved',
            'risk_level': risk_level,
            'model_used': 'XGBoost (94.7% Train | 81.1% Test)'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/batch_predict', methods=['POST'])
def batch_predict():
    global model
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if not file.filename.endswith('.csv'):
        return jsonify({'error': 'Please upload a CSV file'}), 400

    try:
        df = pd.read_csv(file)
        
        X = pd.DataFrame()
        X['Gender'] = df.get('Gender', pd.Series(['Male']*len(df))).map({'Male': 1, 'Female': 0}).fillna(1)
        X['Married'] = df.get('Married', pd.Series(['No']*len(df))).map({'Yes': 1, 'No': 0}).fillna(0)
        X['Dependents'] = df.get('Dependents', pd.Series(['0']*len(df))).astype(str).replace('3+', '3').replace('nan', '0').astype(float)
        X['Education'] = df.get('Education', pd.Series(['Graduate']*len(df))).map({'Graduate': 1, 'Not Graduate': 0}).fillna(1)
        X['Self_Employed'] = df.get('Self_Employed', pd.Series(['No']*len(df))).map({'Yes': 1, 'No': 0}).fillna(0)
        X['ApplicantIncome'] = pd.to_numeric(df.get('ApplicantIncome', pd.Series([0]*len(df))), errors='coerce').fillna(0)
        X['CoapplicantIncome'] = pd.to_numeric(df.get('CoapplicantIncome', pd.Series([0]*len(df))), errors='coerce').fillna(0)
        X['LoanAmount'] = pd.to_numeric(df.get('LoanAmount', pd.Series([0]*len(df))), errors='coerce').fillna(0)
        X['Loan_Amount_Term'] = pd.to_numeric(df.get('Loan_Amount_Term', pd.Series([360]*len(df))), errors='coerce').fillna(360)
        X['Credit_History'] = pd.to_numeric(df.get('Credit_History', pd.Series([1]*len(df))), errors='coerce').fillna(1)
        X['Property_Area'] = df.get('Property_Area', pd.Series(['Urban']*len(df))).map({'Rural': 0, 'Semiurban': 1, 'Urban': 2}).fillna(2)
        
        features = X.values
        
        if model is None:
            model = load_model()
            if model is None:
                return jsonify({'error': 'Model not trained yet. Please train the model first.'}), 400
                
        predictions = model.predict(features)
        probas = model.predict_proba(features)
        confidences = np.round(np.max(probas, axis=1) * 100, 1)
        
        df['Prediction'] = ['Approved' if p == 1 else 'Rejected' for p in predictions]
        df['Confidence (%)'] = confidences
        df['Risk Level'] = ['Low Risk' if c > 80 else 'Medium Risk' if c > 60 else 'High Risk' for c in confidences]
        
        output = io.StringIO()
        df.to_csv(output, index=False)
        output.seek(0)
        
        return Response(
            output,
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment;filename=batch_predictions.csv'}
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/train')
def train_page():
    return render_template('train.html')

@app.route('/api/train', methods=['POST'])
def train_model():
    try:
        import subprocess
        result = subprocess.run(['python', 'train_model.py'], capture_output=True, text=True, timeout=120)
        global model
        model = load_model()
        if result.returncode == 0:
            return jsonify({'success': True, 'message': 'Model trained successfully!', 'output': result.stdout})
        else:
            return jsonify({'success': False, 'message': result.stderr})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
