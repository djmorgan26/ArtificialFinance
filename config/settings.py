# Page configuration
PAGE_CONFIG = {
    "page_title": "AI-Powered Financial Data Analysis App",
    "page_icon": "💰",
    "layout": "wide"
}

# CSS Styles
CSS_STYLES = """
<style>
    body {
        background-color: #ffffff;
        color: #000000;
    }
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1.5rem;
        color: #006400;
    }
    .section-header {
        font-size: 1.8rem;
        font-weight: bold;
        margin-top: 1.2rem;
        color: #006400;
    }
    .stButton>button {
        background-color: #006400;
        color: white;
    }
    .stSelectbox>div>div {
        background-color: #f0fff0;
    }
    .stDataFrame {
        border: 1px solid #006400;
    }
    .css-1d391kg {
        background-color: #f0fff0;
    }
    .sidebar .sidebar-content {
        background-color: #f0fff0;
    }
    .sidebar .sidebar-content .sidebar-section {
        background-color: #f0fff0;
    }
    .confidence-high {
        background-color: #d4edda;
        color: #155724;
        padding: 2px 5px;
        border-radius: 3px;
    }
    .confidence-medium {
        background-color: #fff3cd;
        color: #856404;
        padding: 2px 5px;
        border-radius: 3px;
    }
    .confidence-low {
        background-color: #f8d7da;
        color: #721c24;
        padding: 2px 5px;
        border-radius: 3px;
    }
    .mapping-table {
        width: 100%; 
        border-collapse: collapse;
    }
    .mapping-table th, .mapping-table td {
        padding: 8px;
        text-align: left;
        border-bottom: 1px solid #ddd;
    }
</style>
"""

# Standard financial categories
STANDARD_CATEGORIES = ["transaction_date", "amount", "description", "category", "account", "ignore"]

# API Configuration (in production use environment variables)
API_KEYS = {
    "openai": "your-openai-api-key",  # Replace with actual key or use st.secrets
    "huggingface": "your-huggingface-api-key"  # Replace with actual key or use st.secrets
}