import streamlit as st
import pandas as pd
from services.ai_service import ai_map_columns
from services.storage_service import save_column_mappings, update_column_mappings
from utils.data_processor import apply_mappings
from config.settings import STANDARD_CATEGORIES
from datetime import datetime

def mapping_review_ui(file_id, df, suggested_mappings):
    """
    Render the UI for reviewing and potentially overriding AI-suggested mappings
    
    Args:
        file_id: Identifier for the file
        df: DataFrame being mapped
        suggested_mappings: AI-generated mapping suggestions
    
    Returns:
        Dictionary with final mappings after user review
    """
    st.markdown('<div class="section-header">AI-Suggested Column Mappings</div>', unsafe_allow_html=True)
    st.write("Please review the AI-suggested mappings and make any necessary corrections.")
    
    # Prepare data for the mapping table
    mapping_data = []
    final_mappings = {}
    
    for mapping in suggested_mappings["column_mappings"]:
        original_col = mapping["original_column"]
        suggested_mapping = mapping["mapped_to"]
        confidence = mapping["confidence"]
        explanation = mapping["explanation"]
        
        # Create a unique key for this column's selectbox
        selectbox_key = f"mapping_{file_id}_{original_col}"
        
        # Set up color coding based on confidence
        if confidence == "high":
            confidence_html = f'<span class="confidence-high">HIGH</span>'
        elif confidence == "medium":
            confidence_html = f'<span class="confidence-medium">MEDIUM</span>'
        else:
            confidence_html = f'<span class="confidence-low">LOW</span>'
        
        mapping_data.append({
            "Original Column": original_col,
            "Sample Data": ", ".join(str(x) for x in df[original_col].dropna().head(2).tolist()),
            "AI Suggestion": suggested_mapping,
            "Confidence": confidence_html,
            "Explanation": explanation,
            "Map To": st.selectbox(
                f"Map '{original_col}' to:",
                STANDARD_CATEGORIES,
                index=STANDARD_CATEGORIES.index(suggested_mapping) if suggested_mapping in STANDARD_CATEGORIES else 0,
                key=selectbox_key
            )
        })
        
        # Store the final mapping (either AI-suggested or user-overridden)
        final_mappings[original_col] = mapping_data[-1]["Map To"]
    
    # Display the mapping table with HTML for colored confidence levels
    st.write("Review and finalize column mappings:")
    
    # Custom HTML display for the mapping table
    html_table = '<table class="mapping-table">'
    html_table += "<tr><th>Original Column</th><th>Sample Data</th><th>AI Suggestion</th><th>Confidence</th><th>Explanation</th><th>Map To</th></tr>"
    
    for item in mapping_data:
        html_table += f"<tr>"
        html_table += f"<td>{item['Original Column']}</td>"
        html_table += f"<td>{item['Sample Data']}</td>"
        html_table += f"<td>{item['AI Suggestion']}</td>"
        html_table += f"<td>{item['Confidence']}</td>"
        html_table += f"<td>{item['Explanation']}</td>"
        html_table += f"<td>{item['Map To']}</td>"
        html_table += "</tr>"
    
    html_table += "</table>"
    st.markdown(html_table, unsafe_allow_html=True)
    
    # Show the original user selections (these are already captured in the session state via the selectboxes)
    st.write("\nFinal mappings after your review:")
    final_mapping_df = pd.DataFrame([{"Original": k, "Mapped To": v} for k, v in final_mappings.items()])
    st.dataframe(final_mapping_df)
    
    if st.button("Confirm Mappings"):
        # Store the mappings in Firestore for this user
        success = save_column_mappings(st.session_state.user_id, file_id, final_mappings)
        if success:
            st.success("Mappings saved! These will be remembered for similar files in the future.")
        
        return final_mappings
    
    return None

def render_column_management():
    """Render the column management UI"""
    if not st.session_state.dataframes:
        st.warning("Please upload data in the 'Data Upload' tab first.")
    else:
        st.markdown('<div class="section-header">AI-Assisted Column Mapping</div>', unsafe_allow_html=True)
        
        # Let user select which file to manage
        file_options = list(st.session_state.dataframes.keys())
        selected_file = st.selectbox("Select file to manage", file_options)
        
        if selected_file:
            df = st.session_state.dataframes[selected_file]
            
            # Handle AI mapping review if available
            if selected_file in st.session_state.ai_suggested_mappings and selected_file not in st.session_state.column_mappings:
                suggested_mappings = st.session_state.ai_suggested_mappings[selected_file]
                final_mappings = mapping_review_ui(selected_file, df, suggested_mappings)
                
                if final_mappings:
                    st.session_state.column_mappings[selected_file] = final_mappings
                    
            # Display and allow editing of existing mappings
            elif selected_file in st.session_state.column_mappings:
                existing_mappings = st.session_state.column_mappings[selected_file]
                
                st.markdown('<div class="section-header">Current Column Mappings</div>', unsafe_allow_html=True)
                st.write("These mappings have been saved for this file. You can modify them if needed.")
                
                updated_mappings = {}
                
                # Create editing interface for existing mappings
                for orig_col, mapped_to in existing_mappings.items():
                    if orig_col in df.columns:  # Only show mappings for columns that exist
                        new_mapping = st.selectbox(
                            f"Map '{orig_col}' to:",
                            STANDARD_CATEGORIES,
                            index=STANDARD_CATEGORIES.index(mapped_to) if mapped_to in STANDARD_CATEGORIES else 0,
                            key=f"edit_mapping_{selected_file}_{orig_col}"
                        )
                        updated_mappings[orig_col] = new_mapping
                
                if st.button("Update Mappings"):
                    st.session_state.column_mappings[selected_file] = updated_mappings
                    
                    # Update in database
                    success = update_column_mappings(st.session_state.user_id, selected_file, updated_mappings)
                    if success:
                        st.success("Mappings updated successfully!")
            
            # If no mappings yet, prompt user to run AI analysis
            elif selected_file not in st.session_state.ai_suggested_mappings:
                st.info("No column mappings for this file yet. Run AI analysis to get suggestions.")
                if st.button("Run AI Analysis"):
                    with st.spinner("AI is analyzing your columns..."):
                        suggested_mappings = ai_map_columns(df, selected_file)
                        st.session_state.ai_suggested_mappings[selected_file] = suggested_mappings
                    st.success("Analysis complete! Please review the suggested mappings.")
                    st.experimental_rerun()
            
            # Preview of transformed data with current mappings
            if selected_file in st.session_state.column_mappings:
                st.markdown('<div class="section-header">Preview Transformed Data</div>', unsafe_allow_html=True)
                
                # Apply mappings to get standardized data
                standardized_df = apply_mappings(df, st.session_state.column_mappings[selected_file])
                
                st.dataframe(standardized_df.head(), use_container_width=True)
                
                # Option to apply transformation
                if st.button("Apply Transformation"):
                    st.session_state.dataframes[selected_file] = standardized_df
                    st.success("Transformation applied! The file now uses standardized column names.")