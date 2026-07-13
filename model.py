import pandas as pd
import numpy as np
import pickle
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# ──────────────────────────────────────────────────────────────────────────────
# 1. LOAD DATA
# ──────────────────────────────────────────────────────────────────────────────
print("=" * 60)
print("STEP 1: Loading Dataset")
print("=" * 60)

df = pd.read_csv("train.csv")
print(f"Dataset shape: {df.shape}")

# ──────────────────────────────────────────────────────────────────────────────
# 2. PREPROCESSING & IMPUTATION
# ──────────────────────────────────────────────────────────────────────────────
print("\nSTEP 2: Handling Missing Values (Imputation)")
print("=" * 60)

# Fill categorical missing values with Mode
categorical_cols = ['Gender', 'Married', 'Dependents', 'Self_Employed', 'Credit_History']
for col in categorical_cols:
    mode_val = df[col].mode()[0]
    df[col] = df[col].fillna(mode_val)
    print(f"Imputed categorical '{col}' with Mode: {mode_val}")

# Fill numerical missing values with Mean
numerical_cols = ['LoanAmount', 'Loan_Amount_Term']
for col in numerical_cols:
    mean_val = df[col].mean()
    df[col] = df[col].fillna(mean_val)
    print(f"Imputed numerical '{col}' with Mean: {mean_val:.2f}")

# ──────────────────────────────────────────────────────────────────────────────
# 3. ENCODING CATEGORICAL VARIABLES
# ──────────────────────────────────────────────────────────────────────────────
print("\nSTEP 3: Encoding Categorical Features")
print("=" * 60)

# Define mappings
gender_map = {'Male': 1, 'Female': 0}
married_map = {'Yes': 1, 'No': 0}
dependents_map = {'0': 0, '1': 1, '2': 2, '3+': 3}
education_map = {'Graduate': 1, 'Not Graduate': 0}
self_employed_map = {'Yes': 1, 'No': 0}
property_area_map = {'Rural': 0, 'Semiurban': 1, 'Urban': 2}
loan_status_map = {'Y': 1, 'N': 0}

df['Gender'] = df['Gender'].map(gender_map)
df['Married'] = df['Married'].map(married_map)
df['Dependents'] = df['Dependents'].map(dependents_map).astype(int)
df['Education'] = df['Education'].map(education_map)
df['Self_Employed'] = df['Self_Employed'].map(self_employed_map)
df['Property_Area'] = df['Property_Area'].map(property_area_map)
df['Loan_Status'] = df['Loan_Status'].map(loan_status_map)

# Feature matrix X and target y
features = [
    'Gender', 'Married', 'Dependents', 'Education', 'Self_Employed',
    'ApplicantIncome', 'CoapplicantIncome', 'LoanAmount', 'Loan_Amount_Term',
    'Credit_History', 'Property_Area'
]

X = df[features]
y = df['Loan_Status']

print(f"Feature matrix shape: {X.shape}")
print(f"Target variable class distribution:\n{y.value_counts(normalize=True)}")

# ──────────────────────────────────────────────────────────────────────────────
# 4. SPLIT DATA & SCALE FEATURES
# ──────────────────────────────────────────────────────────────────────────────
print("\nSTEP 4: Splitting & Scaling Data")
print("=" * 60)

# Standard 80/20 train/test split, stratified
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print(f"Train size: {X_train.shape[0]} samples")
print(f"Test size: {X_test.shape[0]} samples")

# ──────────────────────────────────────────────────────────────────────────────
# 5. MODEL TRAINING & COMPARISON
# ──────────────────────────────────────────────────────────────────────────────
print("\nSTEP 5: Training and Evaluating Models")
print("=" * 60)

models = {
    'Decision Tree': DecisionTreeClassifier(max_depth=5, random_state=42),
    'Random Forest': RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42),
    'KNN': KNeighborsClassifier(n_neighbors=5),
    'XGBoost': XGBClassifier(
        n_estimators=50,
        max_depth=3,
        learning_rate=0.1,
        use_label_encoder=False,
        eval_metric='logloss',
        random_state=42
    )
}

best_test_acc = 0
best_model_name = ""
best_model = None

for name, clf in models.items():
    # Fit the model
    clf.fit(X_train_scaled, y_train)
    
    # Predict
    y_train_pred = clf.predict(X_train_scaled)
    y_test_pred = clf.predict(X_test_scaled)
    
    train_acc = accuracy_score(y_train, y_train_pred)
    test_acc = accuracy_score(y_test, y_test_pred)
    
    print(f"\nModel: {name}")
    print(f"  Training Accuracy: {train_acc * 100:.1f}%")
    print(f"  Testing Accuracy:  {test_acc * 100:.1f}%")
    
    if test_acc > best_test_acc:
        best_test_acc = test_acc
        best_model_name = name
        best_model = clf

print(f"\nBest Performing Model on Test Set: {best_model_name} ({best_test_acc * 100:.1f}% accuracy)")

# ──────────────────────────────────────────────────────────────────────────────
# 6. SERIALIZATION
# ──────────────────────────────────────────────────────────────────────────────
print("\nSTEP 6: Saving Best Model and Scaling Artifacts")
print("=" * 60)

# Save XGBoost as the main production model as required
xgb_model = models['XGBoost']
with open('loan_model.pkl', 'wb') as f:
    pickle.dump(xgb_model, f)
print("Saved loan_model.pkl (XGBoost model)")

with open('scaler.pkl', 'wb') as f:
    pickle.dump(scaler, f)
print("Saved scaler.pkl (StandardScaler)")

with open('feature_cols.pkl', 'wb') as f:
    pickle.dump(features, f)
print("Saved feature_cols.pkl (Ordered features list)")

print("\nModel pipeline training complete!")
