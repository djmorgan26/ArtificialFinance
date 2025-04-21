import streamlit as st
import pandas as pd
from utils.data_loader import load_data, load_sample_data
from utils.data_processor import clean_column_names, check_missing_values, handle_missing_values, apply_mappings
from services.ai_service import ai_map_columns
from services.storage_service import get_existing_mappings

def render_data_upload(sample_data):
    """Render the data upload UI"""
    st.markdown('<div class="section-header">Data Upload</div>', unsafe_allow_html=True)
    
    # Handle sample data loading
    if sample_data != "None" and len(st.session_state.dataframes) == 0:
        sample_dfs = load_sample_data(sample_data)
        st.session_state.dataframes.update(sample_dfs)
        st.success(f"Loaded sample {sample_data} data with {len(sample_dfs)} files")
    
    # File upload section
    uploaded_files = st.file_uploader("Upload file(s)", type=["csv", "xlsx", "json"], accept_multiple_files=True)
    
    if uploaded_files:
        for uploaded_file in uploaded_files:
            # Generate a unique ID for this file if it doesn't exist
            file_id = uploaded_file.name.replace(".", "_").replace(" ", "_")
            
            # Only process if this file hasn't been loaded yet
            if file_id not in st.session_state.dataframes:
                file_type = st.radio(f"Select file type for {uploaded_file.name}", 
                                   ["CSV", "Excel", "JSON"], key=f"file_type_{file_id}")
                
                if st.button(f"Load {uploaded_file.name}", key=f"load_{file_id}"):
                    df = load_data(uploaded_file, file_type.lower(), uploaded_file.name)
                    if df is not None:
                        st.session_state.dataframes[file_id] = df
                        
                        # Check for existing mappings from previous uploads
                        existing_mappings = get_existing_mappings(st.session_state.user_id, file_id)
                        
                        if existing_mappings:
                            st.success(f"Found previous column mappings for similar files!")
                            st.session_state.column_mappings[file_id] = existing_mappings
                        else:
                            # Get AI-suggested mappings
                            with st.spinner("AI is analyzing your columns..."):
                                suggested_mappings = ai_map_columns(df, uploaded_file.name)
                                st.session_state.ai_suggested_mappings[file_id] = suggested_mappings
                            
                            st.success(f"Successfully loaded {uploaded_file.name} with {df.shape[0]} rows and {df.shape[1]} columns")
                            st.info("AI has suggested column mappings. Please review them in the Column Management section.")
    
    # Display loaded files
    if st.session_state.dataframes:
        st.markdown('<div class="section-header">Loaded Files</div>', unsafe_allow_html=True)
        
        for file_id, df in st.session_state.dataframes.items():
            with st.expander(f"{file_id} - {df.shape[0]} rows, {df.shape[1]} columns"):
                st.dataframe(df.head(), use_container_width=True)
                
                # Add AI mapping button for each file if not already mapped
                if file_id not in st.session_state.ai_suggested_mappings and file_id not in st.session_state.column_mappings:
                    if st.button(f"Analyze Columns for {file_id}", key=f"analyze_{file_id}"):
                        with st.spinner("AI is analyzing your columns..."):
                            suggested_mappings = ai_map_columns(df, file_id)
                            st.session_state.ai_suggested_mappings[file_id] = suggested_mappings
                        st.success("Column analysis complete! Please review in the Column Management section.")
        
        # Combine files option
        st.markdown('<div class="section-header">Combine Files</div>', unsafe_allow_html=True)
        
        if st.button("Combine All Files"):
            # First, apply any approved mappings to standardize the dataframes
            standardized_dfs = []
            
            for file_id, df in st.session_state.dataframes.items():
                if file_id in st.session_state.column_mappings:
                    # Apply confirmed mappings
                    standardized_df = apply_mappings(df, st.session_state.column_mappings[file_id])
                    standardized_dfs.append(standardized_df)
                else:
                    st.warning(f"Please review and confirm column mappings for {file_id} first.")
                    standardized_dfs = []
                    break
            
            if standardized_dfs:
                combined_df = pd.concat(standardized_dfs, ignore_index=True)
                st.session_state.combined_df = combined_df
                st.success(f"Successfully combined {len(standardized_dfs)} files into one dataset with {combined_df.shape[0]} rows")
        
        # Data preprocessing options
        if st.session_state.combined_df is not None:
            df = st.session_state.combined_df
            
            st.markdown('<div class="section-header">Combined Data Preview</div>', unsafe_allow_html=True)
            st.dataframe(df.head(), use_container_width=True)
            
            st.markdown('<div class="section-header">Data Preprocessing</div>', unsafe_allow_html=True)
            
            preprocessing_options = st.multiselect(
                "Select preprocessing steps",
                ["Clean Column Names", "Drop Duplicates", "Handle Missing Values"]
            )
            
            if "Clean Column Names" in preprocessing_options:
                df = clean_column_names(df)
                st.success("Column names cleaned!")
                
            if "Drop Duplicates" in preprocessing_options:
                original_rows = df.shape[0]
                df = df.drop_duplicates()
                new_rows = df.shape[0]
                st.write(f"Removed {original_rows - new_rows} duplicate rows.")
            
            if "Handle Missing Values" in preprocessing_options:
                missing_df = check_missing_values(df)
                if missing_df.empty:
                    st.success("No missing values found in the dataset!")
                else:
                    st.write("Missing values found:")
                    st.dataframe(missing_df)
                    
                    missing_method = st.selectbox(
                        "Select method to handle missing values",
                        ["Do nothing", "Drop rows", "Fill with mean", "Fill with median", "Fill with zero"]
                    )
                    
                    if missing_method != "Do nothing" and st.button("Apply"):
                        if missing_method == "Drop rows":
                            df = handle_missing_values(df, "drop")
                        elif missing_method == "Fill with mean":
                            df = handle_missing_values(df, "mean")
                        elif missing_method == "Fill with median":
                            df = handle_missing_values(df, "median")
                        elif missing_method == "Fill with zero":
                            df = handle_missing_values(df, "zero")
                        
                        st.success(f"Missing values handled using '{missing_method}'!")
            
            # Save preprocessed data
            if st.button("Save Preprocessing Changes"):
                st.session_state.combined_df = df
                st.success("Changes saved! You can now proceed to data exploration and analysis.")