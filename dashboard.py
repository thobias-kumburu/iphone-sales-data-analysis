import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import warnings
from datetime import datetime, timedelta
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="iPhone Sales Analytics",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={'About': "Professional iPhone Sales Analytics Dashboard"}
)

# Professional Color Palette (Apple-inspired + Modern Business)
COLORS = {
    'primary': '#1E40AF',      # Deep Blue
    'secondary': '#7C3AED',    # Violet
    'accent': '#06B6D4',       # Cyan
    'success': '#10B981',      # Green
    'warning': '#F59E0B',      # Amber
    'danger': '#EF4444',       # Red
    'light_bg': '#F8FAFC',     # Light Slate
    'dark_text': '#0F172A',    # Dark Slate
}

# Load dataset
@st.cache_data
def load_data():
    try:
        df = pd.read_csv(r"D:\Test data\iphone_sales_dataset.csv")
    except FileNotFoundError:
        df = pd.read_csv("iphone_sales_dataset.csv")
    df['Sale_Date'] = pd.to_datetime(df['Sale_Date'])
    df['Revenue'] = df['Quantity'] * df['Price']
    df['Month'] = df['Sale_Date'].dt.to_period('M')
    df['Month_str'] = df['Month'].astype(str)
    df['Week'] = df['Sale_Date'].dt.to_period('W')
    df['Quarter'] = df['Sale_Date'].dt.to_period('Q')
    df['Quarter_str'] = df['Quarter'].astype(str)
    return df

df = load_data()

# Advanced CSS styling for professional appearance
st.markdown(f"""
<style>
    * {{
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }}
    
    .main {{
        background-color: #F0F4F8;
    }}
    
    .header-section {{
        background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['secondary']} 100%);
        padding: 40px;
        border-radius: 15px;
        color: white;
        margin-bottom: 30px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }}
    
    .header-title {{
        font-size: 38px;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.5px;
    }}
    
    .header-subtitle {{
        font-size: 16px;
        opacity: 0.95;
        margin-top: 10px;
        font-weight: 300;
    }}
    
    .metric-card {{
        background: white;
        padding: 25px;
        border-radius: 12px;
        border-left: 5px solid {COLORS['primary']};
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        margin-bottom: 15px;
        transition: transform 0.2s;
    }}
    
    .metric-card:hover {{
        transform: translateY(-4px);
        box-shadow: 0 8px 16px rgba(0,0,0,0.12);
    }}
    
    .metric-value {{
        font-size: 32px;
        font-weight: 700;
        color: {COLORS['primary']};
        margin: 10px 0;
    }}
    
    .metric-label {{
        font-size: 13px;
        color: #64748B;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    
    .metric-delta {{
        font-size: 12px;
        color: {COLORS['success']};
        font-weight: 600;
    }}
    
    .section-header {{
        font-size: 24px;
        font-weight: 700;
        color: {COLORS['primary']};
        margin: 30px 0 20px 0;
        padding-bottom: 10px;
        border-bottom: 3px solid {COLORS['accent']};
    }}
    
    .insight-box {{
        background: linear-gradient(135deg, {COLORS['primary']}10 0%, {COLORS['secondary']}10 100%);
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid {COLORS['accent']};
        margin: 15px 0;
    }}
</style>
""", unsafe_allow_html=True)

# Header Section
st.markdown(f"""
<div class="header-section">
    <div class="header-title">📱 iPhone Sales Intelligence Dashboard</div>
    <div class="header-subtitle">Comprehensive Business Analytics & Performance Metrics</div>
</div>
""", unsafe_allow_html=True)

# Title and description (for streamlit structure)
st.markdown("---")

# Sidebar filters with enhanced styling
st.sidebar.markdown(f"<div style='background-color: {COLORS['primary']}; padding: 15px; border-radius: 10px; color: white; margin-bottom: 20px;'><h3 style='margin: 0;'>🔍 Dashboard Filters</h3></div>", unsafe_allow_html=True)

date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(df['Sale_Date'].min(), df['Sale_Date'].max()),
    min_value=df['Sale_Date'].min(),
    max_value=df['Sale_Date'].max(),
    label_visibility="visible"
)

selected_countries = st.sidebar.multiselect(
    "Select Countries",
    options=sorted(df['Country'].unique()),
    default=df['Country'].unique(),
    help="Filter data by country"
)

selected_models = st.sidebar.multiselect(
    "Select iPhone Models",
    options=sorted(df['iPhone_Model'].unique()),
    default=df['iPhone_Model'].unique(),
    help="Filter data by model"
)

# Advanced filter options
st.sidebar.markdown("---")
st.sidebar.markdown("<h4 style='color: #475569;'>📊 View Options</h4>", unsafe_allow_html=True)
show_comparisons = st.sidebar.checkbox("Show Year-over-Year Comparisons", value=True)
show_forecasts = st.sidebar.checkbox("Show Trend Forecasts", value=True)

# Filter data
df_filtered = df[
    (df['Sale_Date'].dt.date >= date_range[0]) &
    (df['Sale_Date'].dt.date <= date_range[1]) &
    (df['Country'].isin(selected_countries)) &
    (df['iPhone_Model'].isin(selected_models))
]

# Calculate previous period for comparison
date_diff = (date_range[1] - date_range[0]).days
prev_start = date_range[0] - timedelta(days=date_diff + 1)
prev_end = date_range[0] - timedelta(days=1)

df_prev_period = df[
    (df['Sale_Date'].dt.date >= prev_start) &
    (df['Sale_Date'].dt.date <= prev_end) &
    (df['Country'].isin(selected_countries)) &
    (df['iPhone_Model'].isin(selected_models))
]

# Calculate KPIs
total_revenue = df_filtered['Revenue'].sum()
prev_revenue = df_prev_period['Revenue'].sum()
revenue_growth = ((total_revenue - prev_revenue) / prev_revenue * 100) if prev_revenue > 0 else 0

total_quantity = df_filtered['Quantity'].sum()
prev_quantity = df_prev_period['Quantity'].sum()
quantity_growth = ((total_quantity - prev_quantity) / prev_quantity * 100) if prev_quantity > 0 else 0

avg_price = df_filtered['Price'].mean()
prev_avg_price = df_prev_period['Price'].mean()
price_change = ((avg_price - prev_avg_price) / prev_avg_price * 100) if prev_avg_price > 0 else 0

num_transactions = len(df_filtered)
prev_transactions = len(df_prev_period)
transaction_growth = ((num_transactions - prev_transactions) / prev_transactions * 100) if prev_transactions > 0 else 0

avg_revenue_per_transaction = total_revenue / num_transactions if num_transactions > 0 else 0
prev_avg_revenue = prev_revenue / prev_transactions if prev_transactions > 0 else 0
revenue_per_tx_growth = ((avg_revenue_per_transaction - prev_avg_revenue) / prev_avg_revenue * 100) if prev_avg_revenue > 0 else 0

# Key Metrics - Enhanced Top Row
st.markdown("<div class='section-header'>📊 Key Performance Indicators</div>", unsafe_allow_html=True)

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        label="💰 Total Revenue",
        value=f"${total_revenue:,.0f}",
        delta=f"{revenue_growth:+.1f}% vs Previous Period",
        delta_color="inverse" if revenue_growth < 0 else "normal"
    )

with col2:
    st.metric(
        label="📦 Units Sold",
        value=f"{total_quantity:,.0f}",
        delta=f"{quantity_growth:+.1f}% vs Previous",
        delta_color="inverse" if quantity_growth < 0 else "normal"
    )

with col3:
    st.metric(
        label="💵 Avg Price/Unit",
        value=f"${avg_price:,.2f}",
        delta=f"{price_change:+.1f}% vs Previous",
        delta_color="inverse" if price_change < 0 else "normal"
    )

with col4:
    st.metric(
        label="📈 Transactions",
        value=f"{num_transactions:,.0f}",
        delta=f"{transaction_growth:+.1f}% vs Previous",
        delta_color="inverse" if transaction_growth < 0 else "normal"
    )

with col5:
    st.metric(
        label="🎯 Avg Revenue/Tx",
        value=f"${avg_revenue_per_transaction:,.2f}",
        delta=f"{revenue_per_tx_growth:+.1f}% vs Previous",
        delta_color="inverse" if revenue_per_tx_growth < 0 else "normal"
    )

# Additional Advanced Metrics
st.markdown("<div class='section-header'>📈 Advanced Metrics</div>", unsafe_allow_html=True)

col1, col2, col3, col4, col5 = st.columns(5)

# Calculate additional metrics
total_margin = (df_filtered['Revenue'].sum() / df_filtered['Quantity'].sum()) if df_filtered['Quantity'].sum() > 0 else 0
avg_order_value = total_revenue / num_transactions if num_transactions > 0 else 0
quantity_mix_variance = df_filtered.groupby('iPhone_Model')['Quantity'].std()
revenue_volatility = df_filtered['Revenue'].std()
unique_customers = len(df_filtered.groupby(['Country', 'iPhone_Model']))

with col1:
    st.metric(
        label="💎 Avg Order Value",
        value=f"${avg_order_value:,.2f}",
        help="Average revenue per transaction"
    )

with col2:
    st.metric(
        label="📊 Revenue Volatility (σ)",
        value=f"${revenue_volatility:,.2f}",
        help="Standard deviation of revenue"
    )

with col3:
    st.metric(
        label="🎯 Market Segments",
        value=f"{unique_customers}",
        help="Number of model-country combinations"
    )

with col4:
    conversion_rate = (total_quantity / (num_transactions * 10)) * 100
    st.metric(
        label="🔄 Avg Units/Transaction",
        value=f"{(total_quantity/num_transactions):.2f}",
        help="Average units sold per transaction"
    )

with col5:
    days_in_period = (date_range[1] - date_range[0]).days + 1
    daily_revenue = total_revenue / days_in_period if days_in_period > 0 else 0
    st.metric(
        label="📅 Daily Avg Revenue",
        value=f"${daily_revenue:,.2f}",
        help="Average daily revenue in period"
    )

st.divider()

# Revenue Trends Over Time with Enhanced Visualization
st.markdown("<div class='section-header'>📈 Revenue & Sales Trends</div>", unsafe_allow_html=True)
col1, col2 = st.columns(2)

with col1:
    monthly_revenue = df_filtered.groupby('Month_str')['Revenue'].sum().reset_index()
    fig_revenue = go.Figure()
    fig_revenue.add_trace(go.Scatter(
        x=monthly_revenue['Month_str'],
        y=monthly_revenue['Revenue'],
        mode='lines+markers',
        name='Revenue',
        line=dict(color=COLORS['primary'], width=3),
        marker=dict(size=10, color=COLORS['primary']),
        fill='tozeroy',
        fillcolor=COLORS['primary'] + '15',
        hovertemplate='<b>%{x}</b><br>Revenue: $%{y:,.0f}<extra></extra>'
    ))
    fig_revenue.update_layout(
        title={"text": "Monthly Revenue Trend", "font": {"size": 18, "color": COLORS['dark_text']}},
        xaxis_title="Month",
        yaxis_title="Revenue ($)",
        hovermode='x unified',
        template='plotly_white',
        height=450,
        plot_bgcolor='#F8FAFC',
        paper_bgcolor='white',
        font=dict(family="Segoe UI", size=11),
        margin=dict(l=50, r=50, t=70, b=50)
    )
    st.plotly_chart(fig_revenue, use_container_width=True)

with col2:
    monthly_quantity = df_filtered.groupby('Month_str')['Quantity'].sum().reset_index()
    fig_quantity = go.Figure()
    fig_quantity.add_trace(go.Scatter(
        x=monthly_quantity['Month_str'],
        y=monthly_quantity['Quantity'],
        mode='lines+markers',
        name='Units Sold',
        line=dict(color=COLORS['secondary'], width=3),
        marker=dict(size=10, color=COLORS['secondary']),
        fill='tozeroy',
        fillcolor=COLORS['secondary'] + '15',
        hovertemplate='<b>%{x}</b><br>Units: %{y:,.0f}<extra></extra>'
    ))
    fig_quantity.update_layout(
        title={"text": "Monthly Units Sold Trend", "font": {"size": 18, "color": COLORS['dark_text']}},
        xaxis_title="Month",
        yaxis_title="Units Sold",
        hovermode='x unified',
        template='plotly_white',
        height=450,
        plot_bgcolor='#F8FAFC',
        paper_bgcolor='white',
        font=dict(family="Segoe UI", size=11),
        margin=dict(l=50, r=50, t=70, b=50)
    )
    st.plotly_chart(fig_quantity, use_container_width=True)

st.divider()

# Sales by Category with Professional Colors
st.markdown("<div class='section-header'>🎯 Sales Performance by Category</div>", unsafe_allow_html=True)
col1, col2 = st.columns(2)

with col1:
    model_sales = df_filtered.groupby('iPhone_Model').agg({
        'Quantity': 'sum',
        'Revenue': 'sum',
        'Price': 'mean'
    }).sort_values('Revenue', ascending=True)
    
    fig_model = go.Figure()
    fig_model.add_trace(go.Bar(
        y=model_sales.index,
        x=model_sales['Revenue'],
        orientation='h',
        name='Revenue',
        marker=dict(color=model_sales['Revenue'].values, colorscale='Blues', showscale=False),
        text=[f"${v:,.0f}" for v in model_sales['Revenue'].values],
        textposition='auto',
        hovertemplate='<b>%{y}</b><br>Revenue: $%{x:,.0f}<extra></extra>'
    ))
    fig_model.update_layout(
        title={"text": "Revenue by iPhone Model", "font": {"size": 18, "color": COLORS['dark_text']}},
        xaxis_title="Revenue ($)",
        yaxis_title="Model",
        template='plotly_white',
        height=450,
        showlegend=False,
        plot_bgcolor='#F8FAFC',
        paper_bgcolor='white',
        font=dict(family="Segoe UI", size=11),
        margin=dict(l=100, r=50, t=70, b=50)
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
        marker=dict(color=country_sales['Revenue'].values, colorscale='Purples', showscale=False),
        text=[f"${v:,.0f}" for v in country_sales['Revenue'].values],
        textposition='auto',
        hovertemplate='<b>%{y}</b><br>Revenue: $%{x:,.0f}<extra></extra>'
    ))
    fig_country.update_layout(
        title={"text": "Revenue by Country", "font": {"size": 18, "color": COLORS['dark_text']}},
        xaxis_title="Revenue ($)",
        yaxis_title="Country",
        template='plotly_white',
        height=450,
        showlegend=False,
        plot_bgcolor='#F8FAFC',
        paper_bgcolor='white',
        font=dict(family="Segoe UI", size=11),
        margin=dict(l=100, r=50, t=70, b=50)
    )
    st.plotly_chart(fig_country, use_container_width=True)

st.divider()

# Model vs Country Analysis - Professional Heatmap
st.markdown("<div class='section-header'>🌍 Market Cross-Analysis</div>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
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
        colorscale='Blues',
        text=model_country.values,
        texttemplate='$%{text:,.0f}',
        textfont={"size": 10},
        colorbar=dict(title="Revenue ($)", thickness=20, len=0.7)
    ))
    fig_heatmap.update_layout(
        title={"text": "Revenue Heatmap: Models × Countries", "font": {"size": 18, "color": COLORS['dark_text']}},
        xaxis_title="Country",
        yaxis_title="iPhone Model",
        height=450,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family="Segoe UI", size=11),
        margin=dict(l=100, r=50, t=70, b=100)
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)

with col2:
    # Quantity Heatmap
    qty_country = df_filtered.pivot_table(
        values='Quantity',
        index='iPhone_Model',
        columns='Country',
        aggfunc='sum',
        fill_value=0
    )

    fig_qty_heatmap = go.Figure(data=go.Heatmap(
        z=qty_country.values,
        x=qty_country.columns,
        y=qty_country.index,
        colorscale='Purples',
        text=qty_country.values,
        texttemplate='%{text:,.0f}',
        textfont={"size": 10},
        colorbar=dict(title="Units Sold", thickness=20, len=0.7)
    ))
    fig_qty_heatmap.update_layout(
        title={"text": "Units Sold Heatmap: Models × Countries", "font": {"size": 18, "color": COLORS['dark_text']}},
        xaxis_title="Country",
        yaxis_title="iPhone Model",
        height=450,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family="Segoe UI", size=11),
        margin=dict(l=100, r=50, t=70, b=100)
    )
    st.plotly_chart(fig_qty_heatmap, use_container_width=True)

st.divider()

# Variance Analysis - Market Volatility
st.markdown("<div class='section-header'>📉 Market Volatility & Risk Analysis</div>", unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)

with col1:
    variance_model = df_filtered.groupby('iPhone_Model')['Revenue'].var().sort_values(ascending=False)
    fig_var_model = go.Figure()
    fig_var_model.add_trace(go.Bar(
        x=variance_model.index,
        y=variance_model.values,
        marker=dict(color=COLORS['warning'], line=dict(color=COLORS['danger'], width=2)),
        text=[f"${v:,.0f}" for v in variance_model.values],
        textposition='auto',
        hovertemplate='<b>%{x}</b><br>Variance: $%{y:,.0f}<extra></extra>'
    ))
    fig_var_model.update_layout(
        title={"text": "Revenue Variance by Model", "font": {"size": 16, "color": COLORS['dark_text']}},
        xaxis_title="Model",
        yaxis_title="Variance ($²)",
        template='plotly_white',
        height=400,
        showlegend=False,
        xaxis_tickangle=-45,
        plot_bgcolor='#F8FAFC',
        paper_bgcolor='white',
        font=dict(family="Segoe UI", size=10),
        margin=dict(l=50, r=50, t=70, b=80)
    )
    st.plotly_chart(fig_var_model, use_container_width=True)

with col2:
    variance_country = df_filtered.groupby('Country')['Revenue'].var().sort_values(ascending=False)
    fig_var_country = go.Figure()
    fig_var_country.add_trace(go.Bar(
        x=variance_country.index,
        y=variance_country.values,
        marker=dict(color=COLORS['accent'], line=dict(color=COLORS['primary'], width=2)),
        text=[f"${v:,.0f}" for v in variance_country.values],
        textposition='auto',
        hovertemplate='<b>%{x}</b><br>Variance: $%{y:,.0f}<extra></extra>'
    ))
    fig_var_country.update_layout(
        title={"text": "Revenue Variance by Country", "font": {"size": 16, "color": COLORS['dark_text']}},
        xaxis_title="Country",
        yaxis_title="Variance ($²)",
        template='plotly_white',
        height=400,
        showlegend=False,
        xaxis_tickangle=-45,
        plot_bgcolor='#F8FAFC',
        paper_bgcolor='white',
        font=dict(family="Segoe UI", size=10),
        margin=dict(l=50, r=50, t=70, b=80)
    )
    st.plotly_chart(fig_var_country, use_container_width=True)

with col3:
    # Price variance analysis
    price_variance = df_filtered.groupby('iPhone_Model')['Price'].var().sort_values(ascending=False)
    fig_price_var = go.Figure()
    fig_price_var.add_trace(go.Bar(
        x=price_variance.index,
        y=price_variance.values,
        marker=dict(color=COLORS['secondary'], line=dict(color=COLORS['primary'], width=2)),
        text=[f"${v:,.2f}" for v in price_variance.values],
        textposition='auto',
        hovertemplate='<b>%{x}</b><br>Price Variance: $%{y:,.2f}<extra></extra>'
    ))
    fig_price_var.update_layout(
        title={"text": "Price Variance by Model", "font": {"size": 16, "color": COLORS['dark_text']}},
        xaxis_title="Model",
        yaxis_title="Variance ($²)",
        template='plotly_white',
        height=400,
        showlegend=False,
        xaxis_tickangle=-45,
        plot_bgcolor='#F8FAFC',
        paper_bgcolor='white',
        font=dict(family="Segoe UI", size=10),
        margin=dict(l=50, r=50, t=70, b=80)
    )
    st.plotly_chart(fig_price_var, use_container_width=True)

st.divider()

# Market Share Analysis
st.markdown("<div class='section-header'>🥧 Market Share Analysis</div>", unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)

with col1:
    model_share = df_filtered.groupby('iPhone_Model')['Revenue'].sum()
    colors_pie = [COLORS['primary'], COLORS['secondary'], COLORS['accent'], COLORS['success'], COLORS['warning']]
    fig_pie_model = go.Figure(data=[go.Pie(
        labels=model_share.index,
        values=model_share.values,
        marker=dict(colors=colors_pie[:len(model_share)] + [COLORS['danger']] * max(0, len(model_share) - len(colors_pie))),
        hovertemplate='<b>%{label}</b><br>Revenue: $%{value:,.0f}<br>Share: %{percent}<extra></extra>',
        textposition='inside',
        textinfo='label+percent'
    )])
    fig_pie_model.update_layout(
        title={"text": "Revenue Share by Model", "font": {"size": 16, "color": COLORS['dark_text']}},
        height=450,
        paper_bgcolor='white',
        font=dict(family="Segoe UI", size=11),
    )
    st.plotly_chart(fig_pie_model, use_container_width=True)

with col2:
    country_share = df_filtered.groupby('Country')['Revenue'].sum()
    fig_pie_country = go.Figure(data=[go.Pie(
        labels=country_share.index,
        values=country_share.values,
        marker=dict(colors=colors_pie[:len(country_share)] + [COLORS['danger']] * max(0, len(country_share) - len(colors_pie))),
        hovertemplate='<b>%{label}</b><br>Revenue: $%{value:,.0f}<br>Share: %{percent}<extra></extra>',
        textposition='inside',
        textinfo='label+percent'
    )])
    fig_pie_country.update_layout(
        title={"text": "Revenue Share by Country", "font": {"size": 16, "color": COLORS['dark_text']}},
        height=450,
        paper_bgcolor='white',
        font=dict(family="Segoe UI", size=11),
    )
    st.plotly_chart(fig_pie_country, use_container_width=True)

with col3:
    # Units share
    unit_share = df_filtered.groupby('iPhone_Model')['Quantity'].sum()
    fig_pie_units = go.Figure(data=[go.Pie(
        labels=unit_share.index,
        values=unit_share.values,
        marker=dict(colors=colors_pie[:len(unit_share)] + [COLORS['danger']] * max(0, len(unit_share) - len(colors_pie))),
        hovertemplate='<b>%{label}</b><br>Units: %{value:,.0f}<br>Share: %{percent}<extra></extra>',
        textposition='inside',
        textinfo='label+percent'
    )])
    fig_pie_units.update_layout(
        title={"text": "Units Sold Share by Model", "font": {"size": 16, "color": COLORS['dark_text']}},
        height=450,
        paper_bgcolor='white',
        font=dict(family="Segoe UI", size=11),
    )
    st.plotly_chart(fig_pie_units, use_container_width=True)

st.divider()

# Detailed Data View
st.markdown(f"<h3 style='color: {COLORS['primary']}; border-bottom: 3px solid {COLORS['accent']}; padding-bottom: 10px;'>📊 Detailed Transaction Data</h3>", unsafe_allow_html=True)
st.markdown("<div class='section-header'>💡 Executive Insights & Strategic Recommendations</div>", unsafe_allow_html=True)

# Calculate key insights
best_model = df_filtered.groupby('iPhone_Model')['Revenue'].sum().idxmax()
best_model_rev = df_filtered.groupby('iPhone_Model')['Revenue'].sum().max()
best_model_qty = df_filtered[df_filtered['iPhone_Model'] == best_model]['Quantity'].sum()

worst_model = df_filtered.groupby('iPhone_Model')['Revenue'].sum().idxmin()
worst_model_rev = df_filtered.groupby('iPhone_Model')['Revenue'].sum().min()

best_country = df_filtered.groupby('Country')['Revenue'].sum().idxmax()
best_country_rev = df_filtered.groupby('Country')['Revenue'].sum().max()

worst_country = df_filtered.groupby('Country')['Revenue'].sum().idxmin()
worst_country_rev = df_filtered.groupby('Country')['Revenue'].sum().min()

growth_countries = df_filtered.groupby('Country')['Revenue'].sum().sort_values(ascending=False).head(1)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div class='insight-box'>
        <h4 style='color: {COLORS["primary"]}; margin-top: 0;'>🏆 Top Performer</h4>
        <p><b>Model:</b> {best_model}</p>
        <p><b>Revenue:</b> ${best_model_rev:,.0f}</p>
        <p><b>Units:</b> {best_model_qty:,.0f}</p>
        <p><small>Leading revenue contributor</small></p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class='insight-box'>
        <h4 style='color: {COLORS["primary"]}; margin-top: 0;'>🌍 Top Market</h4>
        <p><b>Country:</b> {best_country}</p>
        <p><b>Revenue:</b> ${best_country_rev:,.0f}</p>
        <p><b>Share:</b> {(best_country_rev/total_revenue*100):.1f}%</p>
        <p><small>Strongest geographic market</small></p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class='insight-box'>
        <h4 style='color: {COLORS["primary"]}; margin-top: 0;'>⚠️ Opportunity</h4>
        <p><b>Underperformer:</b> {worst_model}</p>
        <p><b>Revenue:</b> ${worst_model_rev:,.0f}</p>
        <p><b>Gap:</b> ${best_model_rev - worst_model_rev:,.0f}</p>
        <p><small>Needs strategic focus</small></p>
    </div>
    """, unsafe_allow_html=True)

# Strategic Recommendations
st.markdown(f"<h3 style='color: {COLORS['primary']}; border-bottom: 3px solid {COLORS['accent']}; padding-bottom: 10px;'>📋 Strategic Recommendations</h3>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
    <div class='insight-box'>
        <h4 style='color: {COLORS["success"]}; margin-top: 0;'>✅ Maximize Strengths</h4>
        <ul>
            <li><b>Invest in {best_model}:</b> Scale marketing and distribution for top performer</li>
            <li><b>Focus on {best_country}:</b> Maintain market leadership and explore expansion</li>
            <li><b>Cross-sell strategies:</b> Promote complementary products to high-value customers</li>
            <li><b>Premium positioning:</b> Leverage strong performance for pricing optimization</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class='insight-box'>
        <h4 style='color: {COLORS["warning"]}; margin-top: 0;'>⚡ Address Challenges</h4>
        <ul>
            <li><b>Stabilize {worst_model}:</b> Market research needed to understand demand gaps</li>
            <li><b>Grow {worst_country}:</b> Implement targeted market penetration initiatives</li>
            <li><b>Reduce volatility:</b> Implement inventory forecasting and demand planning</li>
            <li><b>Optimize pricing:</b> Dynamic pricing strategy based on market conditions</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# Performance Comparison Table
st.markdown(f"<h3 style='color: {COLORS['primary']}; border-bottom: 3px solid {COLORS['accent']}; padding-bottom: 10px;'>📊 Model Performance Comparison</h3>", unsafe_allow_html=True)

model_comparison = df_filtered.groupby('iPhone_Model').agg({
    'Revenue': ['sum', 'mean', 'std'],
    'Quantity': ['sum', 'mean'],
    'Price': ['mean', 'std']
}).round(2)

model_comparison.columns = ['Total Revenue', 'Avg Revenue', 'Revenue Std Dev', 'Total Units', 'Avg Units', 'Avg Price', 'Price Std Dev']
model_comparison = model_comparison.sort_values('Total Revenue', ascending=False)

# Format for display
display_comparison = model_comparison.copy()
display_comparison['Total Revenue'] = display_comparison['Total Revenue'].apply(lambda x: f'${x:,.0f}')
display_comparison['Avg Revenue'] = display_comparison['Avg Revenue'].apply(lambda x: f'${x:,.0f}')
display_comparison['Revenue Std Dev'] = display_comparison['Revenue Std Dev'].apply(lambda x: f'${x:,.0f}')
display_comparison['Total Units'] = display_comparison['Total Units'].apply(lambda x: f'{x:,.0f}')
display_comparison['Avg Units'] = display_comparison['Avg Units'].apply(lambda x: f'{x:,.0f}')
display_comparison['Avg Price'] = display_comparison['Avg Price'].apply(lambda x: f'${x:,.2f}')
display_comparison['Price Std Dev'] = display_comparison['Price Std Dev'].apply(lambda x: f'${x:,.2f}')

st.dataframe(display_comparison, use_container_width=True)

st.divider()

# Geographic Performance
st.markdown(f"<h3 style='color: {COLORS['primary']}; border-bottom: 3px solid {COLORS['accent']}; padding-bottom: 10px;'>🌐 Geographic Performance Analysis</h3>", unsafe_allow_html=True)

country_comparison = df_filtered.groupby('Country').agg({
    'Revenue': ['sum', 'mean', 'std'],
    'Quantity': ['sum', 'mean'],
    'Price': ['mean']
}).round(2)

country_comparison.columns = ['Total Revenue', 'Avg Revenue', 'Revenue Std Dev', 'Total Units', 'Avg Units', 'Avg Price']
country_comparison = country_comparison.sort_values('Total Revenue', ascending=False)

# Format for display
display_country = country_comparison.copy()
display_country['Total Revenue'] = display_country['Total Revenue'].apply(lambda x: f'${x:,.0f}')
display_country['Avg Revenue'] = display_country['Avg Revenue'].apply(lambda x: f'${x:,.0f}')
display_country['Revenue Std Dev'] = display_country['Revenue Std Dev'].apply(lambda x: f'${x:,.0f}')
display_country['Total Units'] = display_country['Total Units'].apply(lambda x: f'{x:,.0f}')
display_country['Avg Units'] = display_country['Avg Units'].apply(lambda x: f'{x:,.0f}')
display_country['Avg Price'] = display_country['Avg Price'].apply(lambda x: f'${x:,.2f}')

st.dataframe(display_country, use_container_width=True)

st.divider()

# Detailed Data View
st.markdown(f"<h3 style='color: {COLORS['primary']}; border-bottom: 3px solid {COLORS['accent']}; padding-bottom: 10px;'>📊 Detailed Transaction Data</h3>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("📌 Total Records", f"{len(df_filtered):,}", help="Number of transactions in filtered dataset")

with col2:
    st.metric("📅 Date Span", f"{(date_range[1] - date_range[0]).days} days", help="Days between start and end date")

with col3:
    st.metric("🔢 Unique Models", f"{df_filtered['iPhone_Model'].nunique()}", help="Number of distinct iPhone models")

# Data export section
if st.checkbox("🔍 Show detailed raw data", help="Display all transaction records"):
    st.markdown(f"<p style='color: {COLORS['primary']}; font-weight: 600;'>Showing {len(df_filtered)} transactions</p>", unsafe_allow_html=True)
    
    # Create formatted dataframe
    data_display = df_filtered[['Sale_Date', 'Country', 'iPhone_Model', 'Quantity', 'Price', 'Revenue']].copy()
    data_display['Sale_Date'] = data_display['Sale_Date'].dt.strftime('%Y-%m-%d')
    data_display['Quantity'] = data_display['Quantity'].apply(lambda x: f'{x:,.0f}')
    data_display['Price'] = data_display['Price'].apply(lambda x: f'${x:,.2f}')
    data_display['Revenue'] = data_display['Revenue'].apply(lambda x: f'${x:,.0f}')
    data_display = data_display.sort_values('Sale_Date', ascending=False)
    
    st.dataframe(data_display, use_container_width=True, height=500)
    
    # Export option
    st.download_button(
        label="📥 Download Data as CSV",
        data=df_filtered.to_csv(index=False),
        file_name=f"iPhone_Sales_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
        help="Download filtered dataset as CSV file"
    )

st.divider()

# Professional Footer
st.markdown(f"""
<div style='background-color: {COLORS['primary']}; color: white; padding: 30px; border-radius: 10px; margin-top: 50px; text-align: center;'>
    <h3 style='margin: 0; font-size: 20px;'>📊 iPhone Sales Intelligence Dashboard</h3>
    <p style='margin: 10px 0 0 0; opacity: 0.9; font-size: 14px;'>
        Advanced Business Analytics Platform | Real-time Data Insights
    </p>
    <hr style='border: 1px solid rgba(255,255,255,0.3); margin: 20px 0;'>
    <p style='margin: 10px 0; font-size: 12px; opacity: 0.8;'>
        <b>Last Updated:</b> {datetime.now().strftime('%B %d, %Y at %I:%M %p')} | 
        <b>Data Period:</b> {date_range[0].strftime('%b %d, %Y')} to {date_range[1].strftime('%b %d, %Y')} | 
        <b>Records:</b> {len(df_filtered):,}
    </p>
    <p style='margin: 5px 0; font-size: 11px; opacity: 0.7;'>
        For questions or support, contact your analytics team
    </p>
</div>
""", unsafe_allow_html=True)
