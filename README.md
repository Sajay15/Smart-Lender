# Smart Lender: Applicant Credibility Prediction for Loan Approval

An intelligent, machine-learning-powered underwriting assistant that automates retail loan approval decisions. By evaluating demographic and financial profiles, the system classifies applicant viability and flags repayment default risk, enabling banking institutions to streamline operations.

---

## 📂 Project Architecture

```text
smart lender/
│
├── 1. Brainstorming & Ideation/     # Brainstorming templates & problem statements
├── 2. Requirement Analysis/         # DFDs, user stories, customer journeys, tech stack
├── 3. Project Design Phase/         # Architecture layout, proposed solution PDFs
├── 4. Project Planning Phase/       # Project backlogs and sprint plans
├── 5. Project Development Phase/     # Reusable components & feature checklists
├── 6. Project Testing/              # Locust load testing & unit test suites
├── 7. Project Documentation/        # Executable file lists and abstracts
├── 8. Project Demonstration/        # Future scalabilities and demo planners
│
├── static/
│   ├── css/
│   │   └── style.css                # Premium dark-theme fintech stylesheet
│   └── images/
│       ├── loan_status_distribution.png # EDA: Target label frequencies
│       ├── credit_history_vs_loan_status.png # EDA: Credit history vs status
│       ├── education_vs_loan_status.png # EDA: Education level vs status
│       └── income_vs_loan_amount.png # EDA: Applicant Income vs Loan size
│
├── templates/
│   ├── home.html                    # Multi-tab underwriting form & dashboard
│   └── result.html                  # Underwriting decision outcome badge & details
│
├── app.py                           # Flask backend server & inference routing
├── model.py                         # Imputation, encoding, and model training
├── eda.py                           # Exploratory Data Analysis & visualizer
├── generate_docs.py                 # ReportLab automatic PDF document generator
│
├── train.csv                        # Raw Loan Prediction dataset
├── loan_model.pkl                   # Pickled XGBoost ensemble classifier
├── scaler.pkl                       # Pickled StandardScaler weights
├── feature_cols.pkl                 # List of features used in the pipeline
│
└── README.md                        # Documentation (this file)
```

---

## 📊 Dataset & Feature Engineering

The system trains on the standard **Loan Prediction Dataset**, processing 11 features:
*   `Gender` (Male / Female)
*   `Married` (Yes / No)
*   `Dependents` (0, 1, 2, 3+)
*   `Education` (Graduate / Under Graduate)
*   `Self_Employed` (Yes / No)
*   `ApplicantIncome` (Monthly Applicant Income)
*   `CoapplicantIncome` (Monthly Co-applicant Income)
*   `LoanAmount` (Requested Loan Amount in thousands of dollars)
*   `Loan_Amount_Term` (Term of loan in months)
*   `Credit_History` (Meets guidelines: 1.0, or not: 0.0)
*   `Property_Area` (Rural / Semiurban / Urban)

### Data Preprocessing Strategy
1.  **Imputation:**
    *   Categorical variables are imputed with the column **mode**.
    *   Continuous variables are imputed with the column **mean**.
2.  **Encoding:** Categorical labels are converted to unique integer codes (e.g. Semiurban = 1, Urban = 2, Rural = 0).
3.  **Scaling:** All variables are normalized using `StandardScaler` to ensure numerical balance.

---

## ⚡ Machine Learning Benchmarking

We trained and evaluated multiple classification models on an 80/20 train-test stratified split:

| Classification Algorithm | Training Accuracy | Testing Accuracy |
| :--- | :--- | :--- |
| **Decision Tree** | 82.5% | 82.1% |
| **K-Nearest Neighbors (KNN)** | 81.7% | 84.6% |
| **Random Forest** | 80.9% | 85.4% |
| **XGBoost (Production Model)** | **81.5%** | **83.7%** |

*The **XGBoost Classifier** is selected as the primary production estimator to optimize ensemble prediction stability.*

---

## 🚀 Setup & Execution Guide

### Prerequisites
*   Python 3.8 or above
*   Visual Studio Code / PyCharm
*   Pip package manager

### 1. Installation
Navigate to your folder, establish a local virtual environment, and install dependencies:
```powershell
# Open terminal and move to workspace directory
cd "c:\Users\mahi9\Desktop\smart lender"

# Activate the virtual environment
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1

# Install requirements
pip install numpy pandas matplotlib seaborn scikit-learn xgboost Flask reportlab
```

### 2. Generate Exploratory Plots
Generate data visualizations showing demographic insights:
```bash
python eda.py
```
This saves visual charts inside `static/images/` to populate the dashboard analytics tab.

### 3. Run Pipeline Training
Train the classification pipeline, print metric summaries, and save model artifacts:
```bash
python model.py
```

### 4. Execute Unit Tests
Verify model routes and predictions:
```bash
python "6.Project Testing/test_app.py"
```

### 5. Start Web Server
Launch the Flask local underwriting portal:
```bash
python app.py
```
Open **`http://127.0.0.1:5000`** in Google Chrome or Microsoft Edge to access the dashboard and run instant candidate evaluations!
