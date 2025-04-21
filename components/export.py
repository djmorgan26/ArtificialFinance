import streamlit as st
import io
from utils.data_processor import export_data

def render_export():
    """Render the export UI"""
    if not st.session_state.dataframes:
        st.warning("Please upload data in the 'Data Upload' tab first.")
    elif st.session_state.combined_df is None:
        st.warning("Please combine your files in the 'Data Upload' tab first.")
    else:
        df = st.session_state.combined_df
        
        st.markdown('<div class="section-header">Export Data</div>', unsafe_allow_html=True)
        
        # Show data summary
        st.write(f"Dataset shape: {df.shape[0]} rows, {df.shape[1]} columns")
        st.dataframe(df.head(), use_container_width=True)
        
        # Select export format
        export_format = st.radio("Select export format", ["CSV", "Excel", "JSON"])
        
        if export_format == "CSV":
            csv_data = export_data(df, "csv")
            st.download_button(
                label="Download as CSV",
                data=csv_data,
                file_name="processed_data.csv",
                mime="text/csv"
            )
        elif export_format == "Excel":
            try:
                excel_data = export_data(df, "excel")
                st.download_button(
                    label="Download as Excel",
                    data=excel_data,
                    file_name="processed_data.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            except ImportError:
                st.error("Excel export requires the xlsxwriter package. Please install it or choose another format.")
        else:  # JSON
            json_data = export_data(df, "json")
            st.download_button(
                label="Download as JSON",
                data=json_data,
                file_name="processed_data.json",
                mime="application/json"
            )
        
        # Option to reset all data
        if st.button("Reset All Data"):
            st.session_state.dataframes = {}
            st.session_state.combined_df = None
            st.session_state.column_mappings = {}
            st.session_state.ai_suggested_mappings = {}
            st.success("All data has been reset. You can now upload new files.")
            st.experimental_rerun()