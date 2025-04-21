import streamlit as st
import pandas as pd
import plotly.express as px
from utils.visualization import create_dashboard_overview, plot_univariate_analysis, plot_monthly_trends, plot_category_spending

def display_dashboard(df):
    """Display basic dashboard for the dataset"""
    st.markdown('<div class="section-header">Dataset Overview</div>', unsafe_allow_html=True)
    
    # Dataset overview
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Rows", f"{df.shape[0]:,}")
    col2.metric("Columns", df.shape[1])
    col3.metric("Missing Values", f"{df.isnull().sum().sum():,}")
    col4.metric("Duplicated Rows", f"{df.duplicated().sum():,}")
    
    # Create visualizations
    fig, dtypes = create_dashboard_overview(df)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="section-header">Data Types</div>', unsafe_allow_html=True)
        st.dataframe(dtypes)
    
    with col2:
        st.markdown('<div class="section-header">Memory Usage</div>', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)

def render_data_exploration():
    """Render the data exploration UI"""
    if not st.session_state.dataframes:
        st.warning("Please upload data in the 'Data Upload' tab first.")
    elif st.session_state.combined_df is None:
        st.warning("Please combine your files in the 'Data Upload' tab first.")
    else:
        df = st.session_state.combined_df
        
        # Display the dashboard overview
        display_dashboard(df)
        
        # Column details
        st.markdown('<div class="section-header">Column Details</div>', unsafe_allow_html=True)
        
        # Get column statistics
        col_stats = pd.DataFrame({
            'Column': df.columns,
            'Type': df.dtypes,
            'Non-Null Count': df.count(),
            'Null Count': df.isnull().sum(),
            'Unique Values': [df[col].nunique() for col in df.columns]
        })
        
        st.dataframe(col_stats, use_container_width=True)
        
        # Source file statistics (if available)
        if '_source_file' in df.columns:
            st.markdown('<div class="section-header">Source File Statistics</div>', unsafe_allow_html=True)
            source_counts = df['_source_file'].value_counts().reset_index()
            source_counts.columns = ['Source File', 'Count']
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.dataframe(source_counts, use_container_width=True)
            
            with col2:
                fig = px.pie(source_counts, values='Count', names='Source File',
                           title="Data Distribution by Source File",
                           color_discrete_sequence=px.colors.sequential.Greens)
                st.plotly_chart(fig, use_container_width=True)
        
        # Financial insights section
        if all(col in df.columns for col in ['transaction_date', 'amount']):
            st.markdown('<div class="section-header">Financial Insights</div>', unsafe_allow_html=True)
            
            # Monthly spending/income trends
            st.subheader("Monthly Spending and Income Trends")
            
            # Plot monthly trends
            fig = plot_monthly_trends(df)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
            
            # Category analysis if category column exists
            if 'category' in df.columns:
                st.subheader("Spending by Category")
                
                # Plot category spending
                fig = plot_category_spending(df)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
            
            # AI-generated financial insights
            st.subheader("Financial Health Assessment")
            
            # Calculate some basic statistics
            total_income = df[df['amount'] > 0]['amount'].sum()
            total_expenses = df[df['amount'] < 0]['amount'].sum().abs()
            savings_rate = ((total_income - total_expenses) / total_income) * 100 if total_income > 0 else 0
            
            # Display basic insights
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Income", f"${total_income:.2f}")
            col2.metric("Total Expenses", f"${total_expenses:.2f}")
            col3.metric("Savings Rate", f"{savings_rate:.1f}%")
            
            # Generate some insights based on savings rate
            if savings_rate >= 20:
                st.success("Great job! Your savings rate is excellent. You're saving a significant portion of your income.")
            elif savings_rate >= 10:
                st.info("You're on the right track with your savings rate, but there might be room for improvement.")
            else:
                st.warning("Your savings rate is lower than recommended. Consider reviewing your expenses to increase savings.")
        
        # Univariate analysis
        st.markdown('<div class="section-header">Univariate Analysis</div>', unsafe_allow_html=True)
        selected_column = st.selectbox("Select column to analyze", df.columns)
        
        if selected_column:
            fig = plot_univariate_analysis(df, selected_column)
            st.plotly_chart(fig, use_container_width=True)