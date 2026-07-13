import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Create directories for static assets
os.makedirs(os.path.join("static", "images"), exist_ok=True)

print("=" * 60)
print("RUNNING EDA PIPELINE")
print("=" * 60)

# Load dataset
df = pd.read_csv("train.csv")

# Fill missing values for plotting
df['Gender'] = df['Gender'].fillna(df['Gender'].mode()[0])
df['Married'] = df['Married'].fillna(df['Married'].mode()[0])
df['Dependents'] = df['Dependents'].fillna(df['Dependents'].mode()[0])
df['Self_Employed'] = df['Self_Employed'].fillna(df['Self_Employed'].mode()[0])
df['Credit_History'] = df['Credit_History'].fillna(df['Credit_History'].mode()[0])
df['LoanAmount'] = df['LoanAmount'].fillna(df['LoanAmount'].mean())
df['Loan_Amount_Term'] = df['Loan_Amount_Term'].fillna(df['Loan_Amount_Term'].mean())

# Set styling
sns.set_theme(style="whitegrid")
plt.rcParams.update({
    'figure.facecolor': '#111827',
    'axes.facecolor': '#111827',
    'text.color': '#f3f4f6',
    'axes.labelcolor': '#9ca3af',
    'xtick.color': '#9ca3af',
    'ytick.color': '#9ca3af',
    'grid.color': '#374151',
    'axes.edgecolor': '#374151'
})

# 1. Target Class Distribution Chart
plt.figure(figsize=(6, 5))
ax = sns.countplot(x='Loan_Status', data=df, palette=['#ef4444', '#10b981'])
plt.title('Loan Approval Status (Y: Yes / N: No)', fontsize=14, pad=15)
plt.xlabel('Loan Status', fontsize=12)
plt.ylabel('Count', fontsize=12)
# Add percentage labels
total = len(df)
for p in ax.patches:
    percentage = '{:.1f}%'.format(100 * p.get_height()/total)
    x = p.get_x() + p.get_width() / 2 - 0.15
    y = p.get_height() + 10
    ax.annotate(percentage, (x, y), fontsize=10, weight='bold', color='#f3f4f6')
plt.tight_layout()
plt.savefig(os.path.join("static", "images", "loan_status_distribution.png"), dpi=150)
plt.close()
print("[OK] Generated loan_status_distribution.png")

# 2. Credit History vs Loan Status Chart
plt.figure(figsize=(6, 5))
sns.countplot(x='Credit_History', hue='Loan_Status', data=df, palette=['#ef4444', '#10b981'])
plt.title('Credit History vs Loan Status', fontsize=14, pad=15)
plt.xlabel('Credit History Meets Guidelines (1: Yes / 0: No)', fontsize=12)
plt.ylabel('Count', fontsize=12)
plt.legend(title='Approved?', labels=['No (N)', 'Yes (Y)'], facecolor='#1f2937', edgecolor='#374151')
plt.tight_layout()
plt.savefig(os.path.join("static", "images", "credit_history_vs_loan_status.png"), dpi=150)
plt.close()
print("[OK] Generated credit_history_vs_loan_status.png")

# 3. Education vs Loan Status Chart
plt.figure(figsize=(6, 5))
sns.countplot(x='Education', hue='Loan_Status', data=df, palette=['#ef4444', '#10b981'])
plt.title('Education Level vs Loan Status', fontsize=14, pad=15)
plt.xlabel('Applicant Education', fontsize=12)
plt.ylabel('Count', fontsize=12)
plt.legend(title='Approved?', labels=['No (N)', 'Yes (Y)'], facecolor='#1f2937', edgecolor='#374151')
plt.tight_layout()
plt.savefig(os.path.join("static", "images", "education_vs_loan_status.png"), dpi=150)
plt.close()
print("[OK] Generated education_vs_loan_status.png")

# 4. Income vs Loan Amount scatter (joint relationship)
plt.figure(figsize=(7, 5))
# Clip extreme outliers to keep the chart readable
plot_df = df[(df['ApplicantIncome'] < 20000) & (df['LoanAmount'] < 400)].copy()
sns.scatterplot(
    x='ApplicantIncome', 
    y='LoanAmount', 
    hue='Loan_Status', 
    data=plot_df, 
    palette=['#ef4444', '#10b981'],
    alpha=0.8
)
plt.title('Applicant Income vs Loan Amount (Outliers Clipped)', fontsize=14, pad=15)
plt.xlabel('Applicant Income ($)', fontsize=12)
plt.ylabel('Loan Amount (in Thousands)', fontsize=12)
plt.legend(title='Approved?', labels=['No (N)', 'Yes (Y)'], facecolor='#1f2937', edgecolor='#374151')
plt.tight_layout()
plt.savefig(os.path.join("static", "images", "income_vs_loan_amount.png"), dpi=150)
plt.close()
print("[OK] Generated income_vs_loan_amount.png")

print("\nEDA chart generation complete!")
