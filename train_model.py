"""
Smart Lender - Model Training Script
Trains Decision Tree, Random Forest, KNN, and XGBoost classifiers
Saves the best model (XGBoost) for Flask deployment
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import pickle
import os
import warnings
warnings.filterwarnings('ignore')

print("=" * 60)
print("   SMART LENDER - Model Training Pipeline")
print("=" * 60)

# ─────────────────────────────────────────────
# 1. LOAD OR GENERATE DATASET
# ─────────────────────────────────────────────
DATA_PATH = os.path.join('data', 'loan_data.csv')

def generate_synthetic_data(n=614):
    """Generate a realistic synthetic loan dataset (mirrors Kaggle LoanPrediction)"""
    np.random.seed(42)
    gender = np.random.choice(['Male', 'Female'], n, p=[0.81, 0.19])
    married = np.random.choice(['Yes', 'No'], n, p=[0.65, 0.35])
    dependents = np.random.choice(['0', '1', '2', '3+'], n, p=[0.57, 0.17, 0.16, 0.10])
    education = np.random.choice(['Graduate', 'Not Graduate'], n, p=[0.78, 0.22])
    self_employed = np.random.choice(['Yes', 'No'], n, p=[0.14, 0.86])
    applicant_income = np.random.lognormal(8.1, 0.6, n).astype(int)
    coapplicant_income = np.where(np.random.rand(n) > 0.35, np.random.lognormal(7.5, 0.7, n), 0).astype(int)
    loan_amount = np.random.lognormal(4.9, 0.5, n).astype(int)
    loan_term = np.random.choice([12, 36, 60, 84, 120, 180, 240, 300, 360, 480], n,
                                  p=[0.01, 0.02, 0.03, 0.03, 0.04, 0.05, 0.04, 0.05, 0.69, 0.04])
    credit_history = np.random.choice([1.0, 0.0], n, p=[0.84, 0.16])
    property_area = np.random.choice(['Urban', 'Semiurban', 'Rural'], n, p=[0.38, 0.38, 0.24])

    # Loan status based on realistic rules
    score = (
        (credit_history == 1) * 0.45 +
        (applicant_income > 4000) * 0.15 +
        (loan_amount < 150) * 0.10 +
        (education == 'Graduate') * 0.10 +
        (married == 'Yes') * 0.08 +
        (coapplicant_income > 0) * 0.07 +
        (property_area == 'Semiurban') * 0.05
    )
    noise = np.random.normal(0, 0.08, n)
    loan_status = (score + noise > 0.40).astype(int)

    df = pd.DataFrame({
        'Loan_ID': [f'LP{str(i).zfill(6)}' for i in range(n)],
        'Gender': gender, 'Married': married, 'Dependents': dependents,
        'Education': education, 'Self_Employed': self_employed,
        'ApplicantIncome': applicant_income, 'CoapplicantIncome': coapplicant_income,
        'LoanAmount': loan_amount, 'Loan_Amount_Term': loan_term,
        'Credit_History': credit_history, 'Property_Area': property_area,
        'Loan_Status': np.where(loan_status == 1, 'Y', 'N')
    })
    return df

if os.path.exists(DATA_PATH):
    print(f"\n[1] Loading dataset from {DATA_PATH}")
    df = pd.read_csv(DATA_PATH)
else:
    print("\n[1] Dataset not found — generating synthetic data (614 rows)...")
    df = generate_synthetic_data(614)
    df.to_csv(DATA_PATH, index=False)
    print(f"    Saved to {DATA_PATH}")

print(f"    Shape: {df.shape}")
print(f"    Columns: {list(df.columns)}")
print(f"\n    Loan Status distribution:\n{df['Loan_Status'].value_counts().to_string()}")

# ─────────────────────────────────────────────
# 2. EDA VISUALIZATIONS
# ─────────────────────────────────────────────
print("\n[2] Generating EDA visualizations...")

os.makedirs('static/images', exist_ok=True)

fig, axes = plt.subplots(2, 3, figsize=(16, 10))
fig.suptitle('Smart Lender – Exploratory Data Analysis', fontsize=16, fontweight='bold', y=1.01)

# Loan Status
sns.countplot(x='Loan_Status', data=df, ax=axes[0, 0],
              palette=['#EF4444', '#10B981'])
axes[0, 0].set_title('Loan Status Distribution')
axes[0, 0].set_xlabel('Loan Status')

# Credit History vs Loan Status
ct = pd.crosstab(df['Credit_History'], df['Loan_Status'])
ct.plot(kind='bar', ax=axes[0, 1], color=['#EF4444', '#10B981'], rot=0)
axes[0, 1].set_title('Credit History vs Loan Status')
axes[0, 1].set_xlabel('Credit History')

# Education vs Loan Status
ct2 = pd.crosstab(df['Education'], df['Loan_Status'])
ct2.plot(kind='bar', ax=axes[0, 2], color=['#EF4444', '#10B981'], rot=0)
axes[0, 2].set_title('Education vs Loan Status')

# Applicant Income distribution
df['ApplicantIncome'].plot(kind='hist', bins=30, ax=axes[1, 0], color='#6366F1', edgecolor='white')
axes[1, 0].set_title('Applicant Income Distribution')
axes[1, 0].set_xlabel('Income')

# Loan Amount distribution
df['LoanAmount'].plot(kind='hist', bins=30, ax=axes[1, 1], color='#8B5CF6', edgecolor='white')
axes[1, 1].set_title('Loan Amount Distribution')
axes[1, 1].set_xlabel('Loan Amount (thousands)')

# Property Area
sns.countplot(x='Property_Area', hue='Loan_Status', data=df, ax=axes[1, 2],
              palette=['#EF4444', '#10B981'])
axes[1, 2].set_title('Property Area vs Loan Status')

plt.tight_layout()
plt.savefig('static/images/eda_plots.png', dpi=120, bbox_inches='tight')
plt.close()
print("    Saved: static/images/eda_plots.png")

# ─────────────────────────────────────────────
# 3. PREPROCESSING
# ─────────────────────────────────────────────
print("\n[3] Preprocessing data...")

df_clean = df.copy()

# Drop Loan_ID
if 'Loan_ID' in df_clean.columns:
    df_clean.drop('Loan_ID', axis=1, inplace=True)

# Fill missing values
num_cols = ['LoanAmount', 'Loan_Amount_Term', 'Credit_History']
cat_cols = ['Gender', 'Married', 'Dependents', 'Self_Employed']

for col in num_cols:
    if col in df_clean.columns:
        df_clean[col].fillna(df_clean[col].mean(), inplace=True)

for col in cat_cols:
    if col in df_clean.columns:
        df_clean[col].fillna(df_clean[col].mode()[0], inplace=True)

print(f"    Missing values after fill: {df_clean.isnull().sum().sum()}")

# Encode categoricals
le = LabelEncoder()
encode_cols = ['Gender', 'Married', 'Dependents', 'Education', 'Self_Employed', 'Property_Area', 'Loan_Status']
for col in encode_cols:
    if col in df_clean.columns:
        df_clean[col] = le.fit_transform(df_clean[col].astype(str))

print(f"    Final shape: {df_clean.shape}")

# ─────────────────────────────────────────────
# 4. TRAIN / TEST SPLIT
# ─────────────────────────────────────────────
X = df_clean.drop('Loan_Status', axis=1)
y = df_clean['Loan_Status']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
print(f"\n[4] Train: {X_train.shape[0]} | Test: {X_test.shape[0]}")

# ─────────────────────────────────────────────
# 5. TRAIN MODELS
# ─────────────────────────────────────────────
print("\n[5] Training classification models...\n")

results = {}

# Decision Tree
dt = DecisionTreeClassifier(max_depth=5, random_state=42)
dt.fit(X_train, y_train)
results['Decision Tree'] = {
    'model': dt,
    'train_acc': round(accuracy_score(y_train, dt.predict(X_train)) * 100, 1),
    'test_acc': round(accuracy_score(y_test, dt.predict(X_test)) * 100, 1)
}
print(f"  Decision Tree   -> Train: {results['Decision Tree']['train_acc']}%  Test: {results['Decision Tree']['test_acc']}%")

# Random Forest
rf = RandomForestClassifier(n_estimators=100, max_depth=6, random_state=42)
rf.fit(X_train, y_train)
results['Random Forest'] = {
    'model': rf,
    'train_acc': round(accuracy_score(y_train, rf.predict(X_train)) * 100, 1),
    'test_acc': round(accuracy_score(y_test, rf.predict(X_test)) * 100, 1)
}
print(f"  Random Forest   -> Train: {results['Random Forest']['train_acc']}%  Test: {results['Random Forest']['test_acc']}%")

# KNN
knn = KNeighborsClassifier(n_neighbors=5)
knn.fit(X_train, y_train)
results['KNN'] = {
    'model': knn,
    'train_acc': round(accuracy_score(y_train, knn.predict(X_train)) * 100, 1),
    'test_acc': round(accuracy_score(y_test, knn.predict(X_test)) * 100, 1)
}
print(f"  KNN             -> Train: {results['KNN']['train_acc']}%  Test: {results['KNN']['test_acc']}%")

# XGBoost
try:
    from xgboost import XGBClassifier
    xgb = XGBClassifier(n_estimators=200, max_depth=4, learning_rate=0.1,
                         use_label_encoder=False, eval_metric='logloss', random_state=42)
    xgb.fit(X_train, y_train)
    results['XGBoost'] = {
        'model': xgb,
        'train_acc': round(accuracy_score(y_train, xgb.predict(X_train)) * 100, 1),
        'test_acc': round(accuracy_score(y_test, xgb.predict(X_test)) * 100, 1)
    }
    print(f"  XGBoost         -> Train: {results['XGBoost']['train_acc']}%  Test: {results['XGBoost']['test_acc']}%")
    best_model_name = 'XGBoost'
    best_model = xgb
except ImportError:
    print("  XGBoost not installed — using Random Forest as best model.")
    best_model_name = 'Random Forest'
    best_model = rf

# ─────────────────────────────────────────────
# 6. MODEL COMPARISON CHART
# ─────────────────────────────────────────────
print("\n[6] Generating model comparison chart...")

names = list(results.keys())
train_accs = [results[n]['train_acc'] for n in names]
test_accs = [results[n]['test_acc'] for n in names]

x = np.arange(len(names))
width = 0.35

fig, ax = plt.subplots(figsize=(10, 6))
bars1 = ax.bar(x - width/2, train_accs, width, label='Train Accuracy', color='#6366F1', alpha=0.9)
bars2 = ax.bar(x + width/2, test_accs, width, label='Test Accuracy', color='#10B981', alpha=0.9)

ax.set_title('Model Accuracy Comparison', fontsize=14, fontweight='bold')
ax.set_ylabel('Accuracy (%)')
ax.set_ylim(50, 105)
ax.set_xticks(x)
ax.set_xticklabels(names)
ax.legend()
ax.grid(axis='y', alpha=0.3)

for bar in bars1:
    ax.annotate(f'{bar.get_height():.1f}%', xy=(bar.get_x() + bar.get_width()/2, bar.get_height()),
                xytext=(0, 3), textcoords='offset points', ha='center', fontsize=10)
for bar in bars2:
    ax.annotate(f'{bar.get_height():.1f}%', xy=(bar.get_x() + bar.get_width()/2, bar.get_height()),
                xytext=(0, 3), textcoords='offset points', ha='center', fontsize=10)

plt.tight_layout()
plt.savefig('static/images/model_comparison.png', dpi=120, bbox_inches='tight')
plt.close()
print("    Saved: static/images/model_comparison.png")

# Confusion Matrix for best model
cm = confusion_matrix(y_test, best_model.predict(X_test))
fig, ax = plt.subplots(figsize=(6, 5))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax,
            xticklabels=['Rejected', 'Approved'], yticklabels=['Rejected', 'Approved'])
ax.set_title(f'{best_model_name} – Confusion Matrix', fontsize=13, fontweight='bold')
ax.set_ylabel('Actual')
ax.set_xlabel('Predicted')
plt.tight_layout()
plt.savefig('static/images/confusion_matrix.png', dpi=120, bbox_inches='tight')
plt.close()
print("    Saved: static/images/confusion_matrix.png")

# ─────────────────────────────────────────────
# 7. SAVE BEST MODEL
# ─────────────────────────────────────────────
os.makedirs('model', exist_ok=True)
with open('model/smart_lender_model.pkl', 'wb') as f:
    pickle.dump(best_model, f)
print(f"\n[7] Best model ({best_model_name}) saved -> model/smart_lender_model.pkl")

print("\n" + "=" * 60)
print("   Training Complete!")
print(f"   Best Model : {best_model_name}")
best_test = results[best_model_name]['test_acc']
best_train = results[best_model_name]['train_acc']
print(f"   Train Acc  : {best_train}%")
print(f"   Test Acc   : {best_test}%")
print("=" * 60)
