import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from utils.visualization import plot_bivariate_analysis, plot_monthly_trends

def render_visualization():
    """Render the visualization UI"""
    if not st.session_state.dataframes:
        st.warning("Please upload data in the 'Data Upload' tab first.")
    elif st.session_state.combined_df is None:
        st.warning("Please combine your files in the 'Data Upload' tab first.")
    else:
        df = st.session_state.combined_df
        
        st.markdown('<div class="section-header">Data Visualization</div>', unsafe_allow_html=True)
        
        viz_type = st.selectbox(
            "Select visualization type", 
            ["Bivariate Analysis", "Correlation Heatmap", "Scatter Matrix", "Time Series (if applicable)"]
        )
        
        if viz_type == "Bivariate Analysis":
            col1, col2 = st.columns(2)
            
            with col1:
                x_column = st.selectbox("Select X-axis column", df.columns, key="x_col")
            
            with col2:
                # Filter out the already selected column
                available_cols = [col for col in df.columns if col != x_column]
                y_column = st.selectbox("Select Y-axis column", available_cols, key="y_col")
            
            # Perform bivariate analysis
            if x_column and y_column:
                fig, correlation = plot_bivariate_analysis(df, x_column, y_column)
                
                if correlation is not None:
                    st.metric("Correlation coefficient", f"{correlation:.4f}")
                
                st.plotly_chart(fig, use_container_width=True)
        
        elif viz_type == "Correlation Heatmap":
            # Select numeric columns for correlation
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            
            if len(numeric_cols) >= 2:
                selected_cols = st.multiselect(
                    "Select columns for correlation",
                    numeric_cols,
                    default=numeric_cols[:min(5, len(numeric_cols))]
                )
                
                if len(selected_cols) >= 2:
                    # Calculate correlation matrix
                    corr = df[selected_cols].corr()
                    
                    # Display correlation matrix as heatmap
                    fig = px.imshow(
                        corr,
                        text_auto=True,
                        color_continuous_scale="Viridis",
                        zmin=-1, zmax=1,
                        title="Correlation Matrix"
                    )
                    fig.update_layout(height=600, plot_bgcolor='#ffffff', paper_bgcolor='#ffffff')
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("Please select at least 2 columns for correlation")
            else:
                st.warning("Correlation heatmap requires at least 2 numeric columns")
        
        elif viz_type == "Scatter Matrix":
            # Select numeric columns for scatter matrix
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            
            if len(numeric_cols) >= 2:
                selected_cols = st.multiselect(
                    "Select columns for scatter matrix",
                    numeric_cols,
                    default=numeric_cols[:min(4, len(numeric_cols))]
                )
                
                color_by = st.selectbox("Color by (optional)", 
                                      ["None"] + df.columns.tolist())
                
                if len(selected_cols) >= 2:
                    # Create scatter matrix
                    if color_by != "None":
                        fig = px.scatter_matrix(
                            df, 
                            dimensions=selected_cols,
                            color=color_by,
                            title="Scatter Matrix",
                            color_discrete_sequence=px.colors.sequential.Greens if pd.api.types.is_numeric_dtype(df[color_by]) else px.colors.qualitative.Set3
                        )
                    else:
                        fig = px.scatter_matrix(
                            df, 
                            dimensions=selected_cols,
                            title="Scatter Matrix",
                            color_discrete_sequence=['#006400']
                        )
                    
                    fig.update_layout(height=800, plot_bgcolor='#ffffff', paper_bgcolor='#ffffff')
                    fig.update_traces(diagonal_visible=False)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("Please select at least 2 columns for scatter matrix")
            else:
                st.warning("Scatter matrix requires at least 2 numeric columns")
        
        elif viz_type == "Time Series (if applicable)":
            # Check for datetime columns
            datetime_cols = []
            for col in df.columns:
                if pd.api.types.is_datetime64_dtype(df[col]):
                    datetime_cols.append(col)
                else:
                    try:
                        # Try to convert to datetime
                        pd.to_datetime(df[col])
                        datetime_cols.append(col)
                    except:
                        pass
            
            if datetime_cols:
                date_col = st.selectbox("Select date column", datetime_cols)
                
                # Select numeric column for time series
                numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
                
                if numeric_cols:
                    value_col = st.selectbox("Select value column", numeric_cols)
                    
                    # Convert to datetime if not already
                    if not pd.api.types.is_datetime64_dtype(df[date_col]):
                        try:
                            temp_df = df.copy()
                            temp_df[date_col] = pd.to_datetime(temp_df[date_col])
                            
                            # Create time series plot
                            fig = px.line(temp_df.sort_values(by=date_col), x=date_col, y=value_col,
                                        title=f"{value_col} over time", color_discrete_sequence=['#006400'])
                            
                            # Add optional grouping
                            group_by = st.selectbox("Group by (optional)", 
                                                  ["None"] + [col for col in df.columns if col != date_col and col != value_col])
                            
                            if group_by != "None":
                                fig = px.line(temp_df.sort_values(by=date_col), x=date_col, y=value_col, 
                                            color=group_by, title=f"{value_col} over time grouped by {group_by}",
                                            color_discrete_sequence=px.colors.sequential.Greens_r)
                            
                            fig.update_layout(plot_bgcolor='#ffffff', paper_bgcolor='#ffffff')
                            st.plotly_chart(fig, use_container_width=True)
                        except Exception as e:
                            st.error(f"Could not convert {date_col} to datetime: {str(e)}")
                else:
                    st.warning("Time series visualization requires at least one numeric column")
            else:
                st.warning("No date/time columns detected. Please convert a column to datetime in Column Management.")