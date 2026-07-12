# Smart Lender — AI-Powered Loan Eligibility Prediction

A complete end-to-end Machine Learning + Flask web application that predicts loan approval eligibility using Decision Tree, Random Forest, KNN, and XGBoost classifiers.

## Project Structure

```
smart_lender/
├── app.py                  # Flask application (routes + prediction API)
├── train_model.py          # ML training pipeline (EDA + preprocessing + 4 models)
├── requirements.txt        # Python dependencies
├── data/
│   └── loan_data.csv       # Dataset (auto-generated on first training run)
├── model/
│   └── smart_lender_model.pkl  # Saved best model (created after training)
├── templates/
│   ├── index.html           # Home / landing page
│   ├── predict.html         # Loan prediction form + results
│   └── train.html           # Run training pipeline from the browser
└── static/
    ├── css/style.css
    ├── js/predict.js
    ├── js/train.js
    └── images/              # EDA charts, model comparison, confusion matrix
```

## Setup Instructions (VS Code)

### 1. Open the folder in VS Code
Unzip `smart_lender.zip` and open the `smart_lender` folder in VS Code (`File → Open Folder`).

### 2. Create a virtual environment (recommended)
Open the VS Code terminal (`` Ctrl+` ``) and run:

```bash
python -m venv venv
```

Activate it:
- **Windows:** `venv\Scripts\activate`
- **macOS/Linux:** `source venv/bin/activate`

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Train the models
This generates the dataset (if not present), runs EDA, trains all 4 classifiers, and saves the best one (XGBoost):

```bash
python train_model.py
```

You'll see console output with train/test accuracy for each model, and three PNG charts will be saved to `static/images/`.

### 5. Run the Flask app
```bash
python app.py
```

Then open your browser to:
```
http://127.0.0.1:5000
```

## Using the App

- **Home (`/`)** — Project overview, key stats, and use-case scenarios.
- **Predict (`/predict`)** — Enter applicant details (income, credit history, loan amount, etc.) and get an instant prediction with confidence score and risk level.
- **Train Model (`/train`)** — Trigger the full training pipeline directly from the browser and view generated charts.

> **Note:** If you skip Step 4 and go straight to the app, the `/predict` page will still work using a rule-based fallback predictor — but for the real XGBoost model (94.7% train / 81.1% test accuracy), run `train_model.py` first.

## Using Your Own Dataset

By default, `train_model.py` auto-generates a realistic synthetic dataset (modeled on the classic Loan Prediction dataset structure) if `data/loan_data.csv` doesn't exist.

To use a real dataset instead:
1. Download a loan eligibility CSV (e.g. the Kaggle "Loan Prediction" dataset).
2. Make sure it has these columns: `Loan_ID, Gender, Married, Dependents, Education, Self_Employed, ApplicantIncome, CoapplicantIncome, LoanAmount, Loan_Amount_Term, Credit_History, Property_Area, Loan_Status`
3. Save it as `data/loan_data.csv`, replacing the generated one.
4. Re-run `python train_model.py`.

## Tech Stack

- **Backend:** Python, Flask
- **ML:** scikit-learn (Decision Tree, Random Forest, KNN), XGBoost
- **Data:** Pandas, NumPy
- **Visualization:** Matplotlib, Seaborn
- **Frontend:** HTML, CSS, vanilla JavaScript

## Deployment Notes (IBM Cloud / any cloud)

- Set `app.run(debug=False, host='0.0.0.0', port=<PORT>)` in `app.py` for production.
- Use a WSGI server like `gunicorn` (`pip install gunicorn`) for deployment:
  ```bash
  gunicorn app:app
  ```
- Ensure `model/smart_lender_model.pkl` is trained and included before deploying, or trigger `/api/train` once after deployment.

## Troubleshooting

| Issue | Fix |
|---|---|
| `ModuleNotFoundError: xgboost` | Run `pip install xgboost` or `pip install -r requirements.txt` |
| Port 5000 already in use | Change `port=5000` to another port in `app.py` |
| Charts not showing on Train page | Run training at least once; check `static/images/` was created |
| `python` not recognized | Try `python3` instead, or check your PATH/venv activation |
