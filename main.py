import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# Import components
from components.auth import render_auth_ui
from components.data_upload import render_data_upload
from components.column_management import render_column_management
from components.data_exploration import render_data_exploration
from components.visualization import render_visualization
from components.aggregation import render_data_aggregation
from components.export import render_export

# Import configuration
from config.settings import PAGE_CONFIG, CSS_STYLES

# Set up page configuration
st.set_page_config(**PAGE_CONFIG)

# Apply custom styling
st.markdown(CSS_STYLES, unsafe_allow_html=True)

def main():
    """Main application entry point."""
    st.markdown('<div class="main-header">💰 AI-Powered Financial Data Analysis App</div>', unsafe_allow_html=True)
    
    # Add authentication UI
    render_auth_ui()
    
    # Proceed only if user is logged in
    if 'user_id' not in st.session_state or st.session_state.user_id is None:
        st.info("Please login or create an account to use the application.")
        return
    
    # Create sidebar for navigation 
    with st.sidebar:
        st.markdown('<div class="section-header">Navigation</div>', unsafe_allow_html=True)
        app_mode = st.radio("Choose Mode", 
                          ["Data Upload", 
                           "Column Management",
                           "Data Exploration",
                           "Visualization",
                           "Data Aggregation",
                           "Export Data"])
        
        st.markdown('<div class="section-header">Sample Data</div>', unsafe_allow_html=True)
        sample_data = st.selectbox(
            "Load sample dataset",
            ["None", "Bank Transactions", "Credit Card"]
        )
    
    # Initialize session state variables
    if 'dataframes' not in st.session_state:
        st.session_state.dataframes = {}
    
    if 'combined_df' not in st.session_state:
        st.session_state.combined_df = None
    
    if 'column_mappings' not in st.session_state:
        st.session_state.column_mappings = {}
        
    if 'ai_suggested_mappings' not in st.session_state:
        st.session_state.ai_suggested_mappings = {}
    
    # Render the appropriate component based on selected mode
    if app_mode == "Data Upload":
        render_data_upload(sample_data)
    elif app_mode == "Column Management":
        render_column_management()
    elif app_mode == "Data Exploration":
        render_data_exploration()
    elif app_mode == "Visualization":
        render_visualization()
    elif app_mode == "Data Aggregation":
        render_data_aggregation()
    elif app_mode == "Export Data":
        render_export()

if __name__ == "__main__":
    main()