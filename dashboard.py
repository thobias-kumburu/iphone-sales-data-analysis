import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(page_title="iPhone Sales Dashboard", layout="wide", initial_sidebar_state="expanded")

# Load dataset
@st.cache_data
def load_data():
    # Try to load from local path first, then from current directory
    try:
        df = pd.read_csv(r"D:\Test data\iphone_sales_dataset.csv")
    except FileNotFoundError:
        df = pd.read_csv("iphone_sales_dataset.csv")
    df['Sale_Date'] = pd.to_datetime(df['Sale_Date'])
    df['Revenue'] = df['Quantity'] * df['Price']
    df['Month'] = df['Sale_Date'].dt.to_period('M')
    df['Month_str'] = df['Month'].astype(str)
    df['Week'] = df['Sale_Date'].dt.to_period('W')
    return df

df = load_data()

# Custom CSS styling
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin: 10px 0;
    }
    .metric-value {
        font-size: 32px;
        font-weight: bold;
        margin: 10px 0;
    }
    .metric-label {
        font-size: 14px;
        opacity: 0.9;
    }
</style>
""", unsafe_allow_html=True)

# Title and description
st.title("📱 iPhone Sales Performance Dashboard")
st.markdown("### Real-time Business Intelligence & Trend Analysis")

# Sidebar filters
st.sidebar.header("🔍 Filters")
date_range = st.sidebar.date_input("Select Date Range", 
                                    value=(df['Sale_Date'].min(), df['Sale_Date'].max()),
                                    min_value=df['Sale_Date'].min(),
                                    max_value=df['Sale_Date'].max())

selected_countries = st.sidebar.multiselect("Select Countries", 
                                            options=df['Country'].unique(),
                                            default=df['Country'].unique())

selected_models = st.sidebar.multiselect("Select iPhone Models",
                                         options=df['iPhone_Model'].unique(),
                                         default=df['iPhone_Model'].unique())

# Filter data
df_filtered = df[
    (df['Sale_Date'].dt.date >= date_range[0]) &
    (df['Sale_Date'].dt.date <= date_range[1]) &
    (df['Country'].isin(selected_countries)) &
    (df['iPhone_Model'].isin(selected_models))
]

# Key Metrics - Top Row
st.markdown("## 📊 Key Performance Indicators")
col1, col2, col3, col4, col5 = st.columns(5)

total_revenue = df_filtered['Revenue'].sum()
total_quantity = df_filtered['Quantity'].sum()
avg_price = df_filtered['Price'].mean()
num_transactions = len(df_filtered)
avg_revenue_per_transaction = total_revenue / num_transactions if num_transactions > 0 else 0

with col1:
    st.metric("Total Revenue", f"${total_revenue:,.0f}", delta="Current Period")

with col2:
    st.metric("Total Units Sold", f"{total_quantity:,.0f}", delta="Current Period")

with col3:
    st.metric("Avg Price", f"${avg_price:,.2f}", delta="Per Unit")

with col4:
    st.metric("Transactions", f"{num_transactions:,.0f}", delta="Count")

with col5:
    st.metric("Avg Revenue/Transaction", f"${avg_revenue_per_transaction:,.2f}", delta="Per Sale")

st.divider()

# Revenue Trends Over Time
st.markdown("## 📈 Revenue & Sales Trends")
col1, col2 = st.columns(2)

with col1:
    monthly_revenue = df_filtered.groupby('Month_str')['Revenue'].sum().reset_index()
    fig_revenue = go.Figure()
    fig_revenue.add_trace(go.Scatter(
        x=monthly_revenue['Month_str'],
        y=monthly_revenue['Revenue'],
        mode='lines+markers',
        name='Revenue',
        line=dict(color='#667eea', width=3),
        marker=dict(size=8)
    ))
    fig_revenue.update_layout(
        title="Monthly Revenue Trend",
        xaxis_title="Month",
        yaxis_title="Revenue ($)",
        hovermode='x unified',
        template='plotly_white',
        height=400
    )
    st.plotly_chart(fig_revenue, use_container_width=True)

with col2:
    monthly_quantity = df_filtered.groupby('Month_str')['Quantity'].sum().reset_index()
    fig_quantity = go.Figure()
    fig_quantity.add_trace(go.Scatter(
        x=monthly_quantity['Month_str'],
        y=monthly_quantity['Quantity'],
        mode='lines+markers',
        name='Quantity',
        line=dict(color='#764ba2', width=3),
        marker=dict(size=8)
    ))
    fig_quantity.update_layout(
        title="Monthly Units Sold Trend",
        xaxis_title="Month",
        yaxis_title="Units Sold",
        hovermode='x unified',
        template='plotly_white',
        height=400
    )
    st.plotly_chart(fig_quantity, use_container_width=True)

st.divider()

# Sales by Category
st.markdown("## 🎯 Sales Performance by Category")
col1, col2 = st.columns(2)

with col1:
    model_sales = df_filtered.groupby('iPhone_Model').agg({
        'Quantity': 'sum',
        'Revenue': 'sum'
    }).sort_values('Revenue', ascending=True)
    
    fig_model = go.Figure()
    fig_model.add_trace(go.Bar(
        y=model_sales.index,
        x=model_sales['Revenue'],
        orientation='h',
        name='Revenue',
        marker=dict(color='#667eea')
    ))
    fig_model.update_layout(
        title="Revenue by iPhone Model",
        xaxis_title="Revenue ($)",
        yaxis_title="Model",
        template='plotly_white',
        height=400,
        showlegend=False
    )
    st.plotly_chart(fig_model, use_container_width=True)

with col2:
    country_sales = df_filtered.groupby('Country').agg({
        'Quantity': 'sum',
        'Revenue': 'sum'
    }).sort_values('Revenue', ascending=True)
    
    fig_country = go.Figure()
    fig_country.add_trace(go.Bar(
        y=country_sales.index,
        x=country_sales['Revenue'],
        orientation='h',
        name='Revenue',
        marker=dict(color='#764ba2')
    ))
    fig_country.update_layout(
        title="Revenue by Country",
        xaxis_title="Revenue ($)",
        yaxis_title="Country",
        template='plotly_white',
        height=400,
        showlegend=False
    )
    st.plotly_chart(fig_country, use_container_width=True)

st.divider()

# Model vs Country Analysis
st.markdown("## 🌍 Model Performance by Country")
model_country = df_filtered.pivot_table(
    values='Revenue',
    index='iPhone_Model',
    columns='Country',
    aggfunc='sum',
    fill_value=0
)

fig_heatmap = go.Figure(data=go.Heatmap(
    z=model_country.values,
    x=model_country.columns,
    y=model_country.index,
    colorscale='Viridis',
    text=model_country.values,
    texttemplate='$%{text:,.0f}',
    textfont={"size": 10},
))
fig_heatmap.update_layout(
    title="Revenue Heatmap: iPhone Models by Country",
    xaxis_title="Country",
    yaxis_title="iPhone Model",
    height=400
)
st.plotly_chart(fig_heatmap, use_container_width=True)

st.divider()

# Variance Analysis
st.markdown("## 📉 Variance Analysis (Market Volatility)")
col1, col2 = st.columns(2)

with col1:
    variance_model = df_filtered.groupby('iPhone_Model')['Revenue'].var().sort_values(ascending=False)
    fig_var_model = go.Figure()
    fig_var_model.add_trace(go.Bar(
        x=variance_model.index,
        y=variance_model.values,
        marker=dict(color='#d62728')
    ))
    fig_var_model.update_layout(
        title="Revenue Variance by iPhone Model",
        xaxis_title="Model",
        yaxis_title="Variance",
        template='plotly_white',
        height=400,
        showlegend=False,
        xaxis_tickangle=-45
    )
    st.plotly_chart(fig_var_model, use_container_width=True)

with col2:
    variance_country = df_filtered.groupby('Country')['Revenue'].var().sort_values(ascending=False)
    fig_var_country = go.Figure()
    fig_var_country.add_trace(go.Bar(
        x=variance_country.index,
        y=variance_country.values,
        marker=dict(color='#ff7f0e')
    ))
    fig_var_country.update_layout(
        title="Revenue Variance by Country",
        xaxis_title="Country",
        yaxis_title="Variance",
        template='plotly_white',
        height=400,
        showlegend=False,
        xaxis_tickangle=-45
    )
    st.plotly_chart(fig_var_country, use_container_width=True)

st.divider()

# Market Share
st.markdown("## 🥧 Market Share Analysis")
col1, col2 = st.columns(2)

with col1:
    model_share = df_filtered.groupby('iPhone_Model')['Revenue'].sum()
    fig_pie_model = go.Figure(data=[go.Pie(
        labels=model_share.index,
        values=model_share.values,
        hovertemplate='<b>%{label}</b><br>Revenue: $%{value:,.0f}<br>Share: %{percent}',
    )])
    fig_pie_model.update_layout(
        title="Market Share by iPhone Model",
        height=400
    )
    st.plotly_chart(fig_pie_model, use_container_width=True)

with col2:
    country_share = df_filtered.groupby('Country')['Revenue'].sum()
    fig_pie_country = go.Figure(data=[go.Pie(
        labels=country_share.index,
        values=country_share.values,
        hovertemplate='<b>%{label}</b><br>Revenue: $%{value:,.0f}<br>Share: %{percent}',
    )])
    fig_pie_country.update_layout(
        title="Market Share by Country",
        height=400
    )
    st.plotly_chart(fig_pie_country, use_container_width=True)

st.divider()

# Business Insights & Recommendations
st.markdown("## 💡 Business Insights & Recommendations")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🎯 Top Performers")
    best_model = df_filtered.groupby('iPhone_Model')['Revenue'].sum().idxmax()
    best_model_rev = df_filtered.groupby('iPhone_Model')['Revenue'].sum().max()
    best_country = df_filtered.groupby('Country')['Revenue'].sum().idxmax()
    best_country_rev = df_filtered.groupby('Country')['Revenue'].sum().max()
    
    st.write(f"**Best Performing Model:** {best_model}")
    st.write(f"Revenue: ${best_model_rev:,.0f}")
    st.write(f"\n**Top Market:** {best_country}")
    st.write(f"Revenue: ${best_country_rev:,.0f}")

with col2:
    st.markdown("### 📋 Key Recommendations")
    st.write("""
    1. **Focus on High-Variance Markets:** Stabilize revenue in countries with high variance through consistent pricing and marketing
    2. **Model Optimization:** Increase inventory for top-performing models
    3. **Geographic Expansion:** Target underperforming countries with localized campaigns
    4. **Trend Analysis:** Capitalize on upward revenue trends with strategic promotions
    5. **Inventory Management:** Align stock levels with quarterly demand patterns
    """)

st.divider()

# Data Table
st.markdown("## 📊 Detailed Data View")
if st.checkbox("Show raw data"):
    st.dataframe(
        df_filtered[['Sale_Date', 'Country', 'iPhone_Model', 'Quantity', 'Price', 'Revenue']].sort_values('Sale_Date', ascending=False),
        use_container_width=True
    )

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; font-size: 12px;'>
    Dashboard Last Updated: 2026 | Data Period: iPhone Sales Analysis
</div>
""", unsafe_allow_html=True)
