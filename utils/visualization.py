import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

def create_dashboard_overview(df):
    """Create dashboard overview visualization"""
    # Data types
    dtypes = df.dtypes.value_counts().reset_index()
    dtypes.columns = ['Data Type', 'Count']
    
    # Memory usage
    memory_usage = df.memory_usage(deep=True)
    memory_usage = pd.DataFrame({
        'Column': ['Index'] + list(df.columns),
        'Memory (MB)': [memory_usage['Index'] / (1024 * 1024)] + [memory_usage[col] / (1024 * 1024) for col in df.columns]
    })
    memory_usage = memory_usage.sort_values('Memory (MB)', ascending=False)
    
    # Create memory usage bar chart
    fig = px.bar(memory_usage, y='Column', x='Memory (MB)', orientation='h',
               color='Memory (MB)', color_continuous_scale='Viridis')
    fig.update_layout(height=400, plot_bgcolor='#ffffff', paper_bgcolor='#ffffff')
    
    return fig, dtypes

def plot_univariate_analysis(df, column):
    """Create univariate analysis visualization"""
    if pd.api.types.is_numeric_dtype(df[column]):
        # For numeric columns, create histogram and box plot
        fig = make_subplots(rows=2, cols=1, 
                          subplot_titles=("Histogram", "Box Plot"),
                          vertical_spacing=0.15)
        
        # Histogram
        fig.add_trace(
            go.Histogram(x=df[column], name='Histogram', marker_color='#006400'),
            row=1, col=1
        )
        
        # Box plot
        fig.add_trace(
            go.Box(x=df[column], name='Box Plot', marker_color='#006400'),
            row=2, col=1
        )
        
        fig.update_layout(height=500, showlegend=False, plot_bgcolor='#ffffff', paper_bgcolor='#ffffff')
        return fig
    else:
        # For categorical columns, create bar chart
        value_counts = df[column].value_counts().reset_index().head(20)
        value_counts.columns = [column, 'Count']
        
        fig = px.bar(value_counts, x=column, y='Count',
                   title=f"Top 20 values for {column}", color='Count',
                   color_continuous_scale='Viridis')
        fig.update_layout(height=500, plot_bgcolor='#ffffff', paper_bgcolor='#ffffff')
        return fig

def plot_bivariate_analysis(df, x_col, y_col):
    """Create bivariate analysis visualization"""
    x_is_numeric = pd.api.types.is_numeric_dtype(df[x_col])
    y_is_numeric = pd.api.types.is_numeric_dtype(df[y_col])
    
    if x_is_numeric and y_is_numeric:
        # For two numeric columns, create scatter plot with trend line
        fig = px.scatter(df, x=x_col, y=y_col, trendline="ols",
                      title=f"{x_col} vs {y_col}",
                      color_discrete_sequence=['#006400'])
        fig.update_traces(line=dict(color='#000000'))
        fig.update_layout(plot_bgcolor='#ffffff', paper_bgcolor='#ffffff')
        return fig, df[[x_col, y_col]].corr().iloc[0, 1]
        
    elif x_is_numeric and not y_is_numeric:
        # For numeric vs categorical, create box plot
        fig = px.box(df, x=y_col, y=x_col, title=f"Distribution of {x_col} by {y_col}",
                   color=y_col, color_discrete_sequence=px.colors.sequential.Greens)
        fig.update_layout(height=500, plot_bgcolor='#ffffff', paper_bgcolor='#ffffff')
        return fig, None
        
    elif not x_is_numeric and y_is_numeric:
        # For categorical vs numeric, create box plot
        fig = px.box(df, x=x_col, y=y_col, title=f"Distribution of {y_col} by {x_col}",
                   color=x_col, color_discrete_sequence=px.colors.sequential.Greens)
        fig.update_layout(height=500, plot_bgcolor='#ffffff', paper_bgcolor='#ffffff')
        return fig, None
        
    else:
        # For two categorical columns, create heatmap
        contingency_table = pd.crosstab(df[x_col], df[y_col])
        fig = px.imshow(contingency_table, text_auto=True,
                       title=f"Contingency table: {x_col} vs {y_col}",
                       color_continuous_scale='Viridis')
        fig.update_layout(height=600, plot_bgcolor='#ffffff', paper_bgcolor='#ffffff')
        return fig, None

def plot_monthly_trends(df):
    """Create monthly trends visualization"""
    # Ensure required columns exist
    if 'transaction_date' not in df.columns or 'amount' not in df.columns:
        return None
    
    # Create month column
    df['month'] = pd.to_datetime(df['transaction_date']).dt.strftime('%Y-%m')
    
    # Split into income and expenses based on amount sign
    monthly_data = df.groupby('month').agg({
        'amount': [
            ('Total', 'sum'),
            ('Income', lambda x: x[x > 0].sum()),
            ('Expenses', lambda x: x[x < 0].sum().abs())
        ]
    }).reset_index()
    
    # Flatten the multi-level columns
    monthly_data.columns = ['Month', 'Total', 'Income', 'Expenses']
    
    # Plot the monthly trends
    fig = go.Figure()
    fig.add_trace(go.Bar(x=monthly_data['Month'], y=monthly_data['Income'], 
                       name='Income', marker_color='#006400'))
    fig.add_trace(go.Bar(x=monthly_data['Month'], y=monthly_data['Expenses'], 
                       name='Expenses', marker_color='#d32f2f'))
    fig.add_trace(go.Scatter(x=monthly_data['Month'], y=monthly_data['Total'], 
                           mode='lines+markers', name='Net', marker_color='#1976d2'))
    
    fig.update_layout(title="Monthly Income and Expenses",
                    xaxis_title="Month",
                    yaxis_title="Amount",
                    barmode='group',
                    plot_bgcolor='#ffffff',
                    paper_bgcolor='#ffffff')
    
    return fig

def plot_category_spending(df):
    """Create category spending visualization"""
    # Ensure required columns exist
    if 'category' not in df.columns or 'amount' not in df.columns:
        return None
    
    # Calculate total spending by category
    category_spending = df[df['amount'] < 0].groupby('category')['amount'].sum().abs().reset_index()
    category_spending = category_spending.sort_values('amount', ascending=False)
    
    # Plot category spending
    fig = px.pie(category_spending, values='amount', names='category',
               title="Spending Distribution by Category",
               color_discrete_sequence=px.colors.sequential.Greens)
    
    return fig