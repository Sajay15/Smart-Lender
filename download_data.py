import urllib.request
import pandas as pd
import os

urls = [
    "https://raw.githubusercontent.com/shrikant-temburwar/Loan-Prediction-Dataset/master/train.csv",
    "https://raw.githubusercontent.com/dphi-official/Datasets/master/Loan_Prediction/train.csv"
]

target_file = "train.csv"
success = False

for url in urls:
    try:
        print(f"Trying to download from: {url}")
        urllib.request.urlretrieve(url, target_file)
        # Verify columns
        df = pd.read_csv(target_file)
        required_cols = ["ApplicantIncome", "LoanAmount", "Credit_History", "Loan_Status"]
        if all(col in df.columns for col in required_cols):
            print(f"Successfully downloaded and verified dataset from {url}!")
            print(f"Shape: {df.shape}")
            print(f"Columns: {list(df.columns)}")
            success = True
            break
        else:
            print("Dataset downloaded but missing required columns. Retrying other source...")
            os.remove(target_file)
    except Exception as e:
        print(f"Failed to download from {url}: {e}")

if not success:
    print("Could not download dataset from any of the standard URLs.")
    exit(1)
