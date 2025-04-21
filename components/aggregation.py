import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from utils.data_processor import perform_data_aggregation

def render_data_aggregation():
    """Render the data aggregation UI"""
    if not st.session_state.dataframes:
        st.warning("Please upload data in the 'Data Upload' tab first.")
    elif st.session_state.combined_df is None:
        st.warning("Please combine your files in the 'Data Upload' tab first.")
    else:
        df = st.session_state.combined_df
        
        st.markdown('<div class="section-header">Data Aggregation</div>', unsafe_allow_html=True)
        st.write("Aggregate your data based on selected columns and functions")
        
        # Select columns to group by
        categorical_cols = df.select_dtypes(exclude=[np.number]).columns.tolist()
        group_by_cols = st.multiselect(
            "Select columns to group by",
            categorical_cols
        )
        
        # Select columns to aggregate
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        agg_cols = st.multiselect(
            "Select columns to aggregate",
            numeric_cols
        )
        
        # Select aggregation functions
        agg_functions = st.multiselect(
            "Select aggregation functions",
            ["sum", "mean", "median", "min", "max", "count", "std", "var"]
        )
        
        if group_by_cols and agg_cols and agg_functions and st.button("Perform Aggregation"):
            aggregated_df = perform_data_aggregation(df, group_by_cols, agg_cols, agg_functions)
            
            if aggregated_df is not None:
                st.markdown('<div class="section-header">Aggregation Results</div>', unsafe_allow_html=True)
                st.dataframe(aggregated_df, use_container_width=True)
                
                # Visualization of aggregated data
                st.markdown('<div class="section-header">Visualization</div>', unsafe_allow_html=True)
                
                # If we have only one group by column, we can create bar charts
                if len(group_by_cols) == 1:
                    for col in aggregated_df.columns:
                        if col != group_by_cols[0] and pd.api.types.is_numeric_dtype(aggregated_df[col]):
                            fig = px.bar(
                                aggregated_df, 
                                x=group_by_cols[0], 
                                y=col,
                                title=f"{col} by {group_by_cols[0]}",
                                color=col,
                                color_continuous_scale="Viridis"
                            )
                            fig.update_layout(plot_bgcolor='#ffffff', paper_bgcolor='#ffffff')
                            st.plotly_chart(fig, use_container_width=True)
                
                # If we have two group by columns, we can create a heatmap
                elif len(group_by_cols) == 2:
                    # Only for the first aggregated column
                    if len(aggregated_df.columns) > 2:
                        agg_col = [col for col in aggregated_df.columns if col not in group_by_cols][0]
                        
                        # Create pivot table
                        pivot_df = aggregated_df.pivot(
                            index=group_by_cols[0],
                            columns=group_by_cols[1],
                            values=agg_col
                        )
                        
                        fig = px.imshow(
                            pivot_df,
                            title=f"Heatmap of {agg_col} by {group_by_cols[0]} and {group_by_cols[1]}",
                            color_continuous_scale="Viridis"
                        )
                        fig.update_layout(plot_bgcolor='#ffffff', paper_bgcolor='#ffffff')
                        st.plotly_chart(fig, use_container_width=True)
                
                # Export aggregated data
                csv = aggregated_df.to_csv(index=False)
                st.download_button(
                    label="Download Aggregated Data as CSV",
                    data=csv,
                    file_name="aggregated_data.csv",
                    mime="text/csv"
                )