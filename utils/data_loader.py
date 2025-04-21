import pandas as pd
import streamlit as st
import numpy as np
from datetime import datetime, timedelta

def load_data(file_path, file_type="csv", file_name=None):
    """Load data from a file and return it as a pandas DataFrame."""
    try:
        if file_type == "csv":
            # Try to detect separator
            if isinstance(file_path, str):
                with open(file_path, 'r') as f:
                    sample = f.read(5000)
            else:
                sample = file_path.getvalue()[:5000].decode('utf-8')
            
            if ',' in sample:
                sep = ','
            elif ';' in sample:
                sep = ';'
            elif '\t' in sample:
                sep = '\t'
            else:
                sep = None
                
            df = pd.read_csv(file_path, sep=sep)
        elif file_type == "excel":
            df = pd.read_excel(file_path)
        elif file_type == "json":
            df = pd.read_json(file_path)
        else:
            st.error(f"Unsupported file type: {file_type}")
            return None
        
        # Add source column to identify the file
        if file_name:
            df['_source_file'] = file_name
            
        return df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

def load_sample_data(sample_type):
    """Load sample data for demonstration"""
    if sample_type == "Bank Transactions":
        return create_sample_bank_data()
    elif sample_type == "Credit Card":
        return create_sample_credit_card_data()
    return {}

def create_sample_bank_data():
    """Create sample bank transaction data"""
    # Create sample bank transaction data
    dates = pd.date_range(start='2023-01-01', end='2023-03-31')
    
    # Bank 1 transactions
    np.random.seed(42)
    bank1_data = {
        'Date': np.random.choice(dates, 100),
        'Amount': np.random.uniform(-2000, 5000, 100).round(2),
        'Description': np.random.choice(['Salary', 'Groceries', 'Rent', 'Utilities', 'Entertainment', 'Transfer'], 100),
        'Category': np.random.choice(['Income', 'Expense', 'Transfer'], 100),
        'Account': 'Checking'
    }
    bank1_df = pd.DataFrame(bank1_data)
    
    # Bank 2 transactions
    np.random.seed(43)
    bank2_data = {
        'TransactionDate': np.random.choice(dates, 80),
        'TransactionAmount': np.random.uniform(-1500, 3000, 80).round(2),
        'Merchant': np.random.choice(['Paycheck', 'Supermarket', 'Housing', 'Bills', 'Dining', 'Transfer'], 80),
        'Type': np.random.choice(['Credit', 'Debit', 'Transfer'], 80),
        'AccountType': 'Savings'
    }
    bank2_df = pd.DataFrame(bank2_data)
    
    return {'bank1': bank1_df, 'bank2': bank2_df}

def create_sample_credit_card_data():
    """Create sample credit card data"""
    dates = pd.date_range(start='2023-01-01', end='2023-06-30')
    
    # Credit card 1
    np.random.seed(44)
    cc1_data = {
        'Transaction_Date': np.random.choice(dates, 150),
        'Amount': np.random.uniform(-500, 1000, 150).round(2),
        'Merchant_Name': np.random.choice(['Restaurant', 'Gas Station', 'Online Shopping', 'Grocery Store', 'Utility', 'Subscription'], 150),
        'Category': np.random.choice(['Food', 'Transportation', 'Shopping', 'Groceries', 'Bills', 'Entertainment'], 150),
        'Card_Type': 'Visa'
    }
    cc1_df = pd.DataFrame(cc1_data)
    
    # Credit card 2
    np.random.seed(45)
    cc2_data = {
        'Date': np.random.choice(dates, 120),
        'Charge': np.random.uniform(-600, 800, 120).round(2),
        'Vendor': np.random.choice(['Dining', 'Travel', 'Retail', 'Supermarket', 'Service', 'Digital'], 120),
        'Expense_Type': np.random.choice(['Dining', 'Travel', 'Shopping', 'Groceries', 'Utilities', 'Subscription'], 120),
        'Card': 'Mastercard'
    }
    cc2_df = pd.DataFrame(cc2_data)
    
    return {'cc1': cc1_df, 'cc2': cc2_df}