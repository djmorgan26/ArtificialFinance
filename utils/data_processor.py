import pandas as pd
import numpy as np
import streamlit as st
from sklearn.impute import SimpleImputer

def clean_column_names(df):
    """Clean column names by replacing spaces with underscores and converting to lowercase"""
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')', '')
    return df

def rename_columns(df, name_mapping):
    """Rename columns based on mapping"""
    return df.rename(columns=name_mapping)

def check_missing_values(df):
    """Check for missing values in the DataFrame"""
    missing = df.isnull().sum()
    missing_percent = (missing / len(df)) * 100
    missing_df = pd.DataFrame({
        'Missing Values': missing,
        'Percentage': missing_percent
    })
    return missing_df[missing_df['Missing Values'] > 0]

def handle_missing_values(df, method="drop"):
    """Handle missing values in the DataFrame"""
    if method == "drop":
        return df.dropna()
    elif method == "mean":
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            imputer = SimpleImputer(strategy='mean')
            df[numeric_cols] = imputer.fit_transform(df[numeric_cols])
        return df
    elif method == "median":
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            imputer = SimpleImputer(strategy='median')
            df[numeric_cols] = imputer.fit_transform(df[numeric_cols])
        return df
    elif method == "zero":
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            df[numeric_cols] = df[numeric_cols].fillna(0)
        return df
    else:
        return df

def apply_mappings(df, mappings):
    """
    Apply confirmed mappings to the dataframe and standardize data
    
    Args:
        df: Original DataFrame
        mappings: Dictionary mapping original columns to standard columns
    
    Returns:
        Standardized DataFrame with renamed columns and proper data types
    """
    # Create a copy of the original dataframe
    standardized_df = df.copy()
    
    # Create a reverse mapping (standard -> original)
    reverse_mappings = {}
    for orig_col, std_col in mappings.items():
        if std_col != "ignore":  # Skip columns marked as "ignore"
            if std_col in reverse_mappings:
                reverse_mappings[std_col].append(orig_col)
            else:
                reverse_mappings[std_col] = [orig_col]
    
    # Process each standard column
    for std_col, orig_cols in reverse_mappings.items():
        if std_col == "transaction_date":
            # Handle date columns
            for orig_col in orig_cols:
                try:
                    standardized_df[orig_col] = pd.to_datetime(standardized_df[orig_col])
                except:
                    st.warning(f"Could not convert '{orig_col}' to date format. Please check the data.")
        
        elif std_col == "amount":
            # Handle amount columns
            for orig_col in orig_cols:
                if not pd.api.types.is_numeric_dtype(standardized_df[orig_col]):
                    # Try to convert non-numeric to numeric
                    try:
                        standardized_df[orig_col] = standardized_df[orig_col].str.replace('[$,]', '', regex=True).astype(float)
                    except:
                        st.warning(f"Could not convert '{orig_col}' to numeric format. Please check the data.")
    
    # Rename columns based on mappings
    rename_dict = {orig: std for orig, std in mappings.items() if std != "ignore"}
    standardized_df = standardized_df.rename(columns=rename_dict)
    
    # Drop ignored columns
    ignored_cols = [col for col, mapping in mappings.items() if mapping == "ignore"]
    if ignored_cols:
        standardized_df = standardized_df.drop(columns=ignored_cols)
    
    return standardized_df

def perform_data_aggregation(df, group_by_cols, agg_cols, agg_functions):
    """
    Perform data aggregation based on user selections
    
    Args:
        df: DataFrame to aggregate
        group_by_cols: Columns to group by
        agg_cols: Columns to aggregate
        agg_functions: Aggregation functions to apply
        
    Returns:
        Aggregated DataFrame
    """
    if not group_by_cols or not agg_cols or not agg_functions:
        st.warning("Please select at least one column to group by, one column to aggregate, and one aggregation function")
        return None
    
    # Create aggregation dictionary
    agg_dict = {}
    for col in agg_cols:
        agg_dict[col] = agg_functions
    
    # Perform aggregation
    try:
        result = df.groupby(group_by_cols).agg(agg_dict)
        
        # Flatten multi-level column names if needed
        if isinstance(result.columns, pd.MultiIndex):
            result.columns = [f"{col[0]}_{col[1]}" for col in result.columns]
        
        # Reset index for better display
        result = result.reset_index()
        return result
    except Exception as e:
        st.error(f"Error during aggregation: {str(e)}")
        return None

def calculate_financial_metrics(df):
    """
    Calculate key financial metrics from transaction data
    
    Args:
        df: DataFrame with financial transactions
        
    Returns:
        Dictionary with calculated metrics
    """
    metrics = {}
    
    # Check if required columns exist
    if 'amount' not in df.columns:
        return {"error": "Required column 'amount' not found"}
    
    # Calculate basic metrics
    metrics["total_income"] = df[df['amount'] > 0]['amount'].sum()
    metrics["total_expenses"] = df[df['amount'] < 0]['amount'].sum().abs()
    metrics["net_cashflow"] = metrics["total_income"] - metrics["total_expenses"]
    
    if metrics["total_income"] > 0:
        metrics["savings_rate"] = (metrics["net_cashflow"] / metrics["total_income"]) * 100
    else:
        metrics["savings_rate"] = 0
    
    # Category analysis if category column exists
    if 'category' in df.columns:
        category_expenses = df[df['amount'] < 0].groupby('category')['amount'].sum().abs().sort_values(ascending=False)
        metrics["top_expense_categories"] = category_expenses.head(5).to_dict()
    
    # Time-based analysis if transaction_date column exists
    if 'transaction_date' in df.columns:
        df['month'] = pd.to_datetime(df['transaction_date']).dt.strftime('%Y-%m')
        monthly_summary = df.groupby('month').agg({
            'amount': [
                ('total', 'sum'),
                ('income', lambda x: x[x > 0].sum()),
                ('expenses', lambda x: x[x < 0].sum().abs())
            ]
        })
        # Flatten multi-level columns
        monthly_summary.columns = ['_'.join(col).strip() for col in monthly_summary.columns.values]
        metrics["monthly_summary"] = monthly_summary.to_dict()
    
    return metrics

def identify_recurring_transactions(df, min_occurrences=2):
    """
    Identify recurring transactions in the data
    
    Args:
        df: DataFrame with financial transactions
        min_occurrences: Minimum number of occurrences to be considered recurring
        
    Returns:
        DataFrame with recurring transactions
    """
    if 'description' not in df.columns or 'amount' not in df.columns:
        return pd.DataFrame()
    
    # Group by description and calculate stats
    recurring = df.groupby('description').agg({
        'amount': ['count', 'mean', 'std'],
        'transaction_date': ['min', 'max'] if 'transaction_date' in df.columns else ['count', 'count']
    })
    
    # Flatten multi-level columns
    recurring.columns = ['_'.join(col).strip() for col in recurring.columns.values]
    
    # Filter for recurring transactions
    recurring = recurring[recurring['amount_count'] >= min_occurrences]
    
    # Sort by frequency
    recurring = recurring.sort_values('amount_count', ascending=False).reset_index()
    
    return recurring

def export_data(df, format="csv"):
    """
    Prepare data for export in various formats
    
    Args:
        df: DataFrame to export
        format: Export format (csv, excel, json)
        
    Returns:
        Data in the specified format
    """
    if format == "csv":
        return df.to_csv(index=False)
    elif format == "excel":
        import io
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="Data")
        return output.getvalue()
    elif format == "json":
        return df.to_json(orient="records")
    else:
        raise ValueError(f"Unsupported export format: {format}")