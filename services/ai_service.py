import pandas as pd
import json
import requests
import streamlit as st
from config.settings import API_KEYS

def ai_map_columns(df, file_name):
    """
    Use AI to intelligently map columns based on their names and data patterns
    
    Args:
        df: DataFrame to analyze
        file_name: Name of the source file for context
        
    Returns:
        Dictionary with suggested mappings, confidence levels, and explanations
    """
    # Get sample data and column info
    sample_data = df.head(5).to_dict(orient="records")
    column_info = []
    
    for col in df.columns:
        col_type = str(df[col].dtype)
        unique_count = df[col].nunique()
        null_count = df[col].isnull().sum()
        sample_values = df[col].dropna().head(5).tolist()
        
        column_info.append({
            "name": col,
            "type": col_type,
            "unique_values": unique_count,
            "null_count": null_count,
            "sample_values": sample_values
        })
    
    # Prepare the request to OpenAI API
    prompt = f"""
    Analyze these columns from a financial data file named '{file_name}':
    
    {json.dumps(column_info, indent=2)}
    
    Sample records:
    {json.dumps(sample_data, indent=2)}
    
    Map these columns to standard financial categories:
    1. transaction_date: Date of the transaction
    2. amount: Transaction amount (positive for income, negative for expenses)
    3. description: Transaction description or merchant name
    4. category: Transaction category or type
    5. account: Account information
    
    For each column, provide:
    1. The standard category it should map to
    2. Confidence level (high, medium, low)
    3. A brief explanation
    
    Return the results as a JSON object like:
    {{
        "column_mappings": [
            {{
                "original_column": "original name",
                "mapped_to": "standard category",
                "confidence": "high/medium/low",
                "explanation": "brief explanation"
            }}
        ]
    }}
    """
    
    # This would be your actual API call to OpenAI or other AI service
    try:
        # Uncomment in production
        # response = requests.post(
        #     "https://api.openai.com/v1/chat/completions",
        #     headers={
        #         "Authorization": f"Bearer {API_KEYS['openai']}",
        #         "Content-Type": "application/json"
        #     },
        #     json={
        #         "model": "gpt-3.5-turbo",
        #         "messages": [{"role": "user", "content": prompt}],
        #         "temperature": 0.2
        #     }
        # )
        # result = response.json()["choices"][0]["message"]["content"]
        # parsed_result = json.loads(result)
        # return parsed_result
        
        # For demo, use a mock response
        return mock_ai_mapping_response(df)
    except Exception as e:
        st.error(f"AI mapping error: {str(e)}")
        # Fallback to simple pattern matching if AI fails
        return mock_ai_mapping_response(df)

def mock_ai_mapping_response(df):
    """
    Generate a mock AI mapping response based on column names and data types.
    This is used when the AI API is not available or for demonstration.
    
    Args:
        df: DataFrame to analyze
        
    Returns:
        Dictionary with mock mapping suggestions
    """
    mock_response = {
        "column_mappings": []
    }
    
    # Generate mappings based on common patterns
    for col in df.columns:
        mapping = {"original_column": col}
        
        col_lower = col.lower()
        if any(date_term in col_lower for date_term in ["date", "time", "day"]):
            mapping["mapped_to"] = "transaction_date"
            mapping["confidence"] = "high" if "date" in col_lower else "medium"
            mapping["explanation"] = "Column name suggests it contains date information"
        
        elif any(amount_term in col_lower for amount_term in ["amount", "sum", "cost", "price", "charge", "debit", "credit"]):
            mapping["mapped_to"] = "amount"
            mapping["confidence"] = "high" if "amount" in col_lower else "medium"
            mapping["explanation"] = "Column name suggests it contains monetary values"
        
        elif any(desc_term in col_lower for desc_term in ["desc", "description", "merchant", "vendor", "detail", "narrative", "memo", "payee"]):
            mapping["mapped_to"] = "description"
            mapping["confidence"] = "high" if "desc" in col_lower else "medium"
            mapping["explanation"] = "Column name suggests it contains transaction descriptions"
        
        elif any(cat_term in col_lower for cat_term in ["cat", "category", "type", "expense", "code", "class"]):
            mapping["mapped_to"] = "category"
            mapping["confidence"] = "high" if "category" in col_lower else "medium"
            mapping["explanation"] = "Column name suggests it contains categorization information"
        
        elif any(acct_term in col_lower for acct_term in ["account", "acc", "card", "bank"]):
            mapping["mapped_to"] = "account"
            mapping["confidence"] = "high" if "account" in col_lower else "medium"
            mapping["explanation"] = "Column name suggests it contains account information"
        
        else:
            # If nothing matches, make a guess based on data types
            if pd.api.types.is_datetime64_dtype(df[col]) or "date" in str(df[col].dtype):
                mapping["mapped_to"] = "transaction_date"
                mapping["confidence"] = "medium"
                mapping["explanation"] = "Column contains date data"
            elif pd.api.types.is_numeric_dtype(df[col]):
                mapping["mapped_to"] = "amount"
                mapping["confidence"] = "low"
                mapping["explanation"] = "Column contains numeric values that may represent amounts"
            else:
                mapping["mapped_to"] = "description"
                mapping["confidence"] = "low"
                mapping["explanation"] = "Best guess based on text content"
                
        mock_response["column_mappings"].append(mapping)
    
    return mock_response

def generate_financial_insights(df):
    """
    Generate AI-driven financial insights based on the data
    
    Args:
        df: Financial DataFrame to analyze
        
    Returns:
        Dictionary with insights and recommendations
    """
    # This would be implemented with calls to the OpenAI API
    # For now, returning simple mock insights
    
    insights = {
        "summary": {
            "total_income": df[df['amount'] > 0]['amount'].sum() if 'amount' in df.columns else 0,
            "total_expenses": df[df['amount'] < 0]['amount'].sum().abs() if 'amount' in df.columns else 0,
        },
        "recommendations": [
            "Consider tracking your expenses by category to identify areas where you can save.",
            "Set up automatic transfers to a savings account on payday."
        ],
        "patterns": [
            "Regular monthly expenses account for 65% of your spending.",
            "Your dining expenses increased by 15% in the last month."
        ]
    }
    
    return insights