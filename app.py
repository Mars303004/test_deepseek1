import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import base64
from io import BytesIO

# Konfigurasi Warna
COLOR_PRIMARY = "#b42020"
COLOR_SECONDARY = "#0057c8"
COLOR_BACKGROUND = "#FFFFFF"

# Fungsi Helper
def create_gauge(value, title, min_val, max_val, reference=None):
    delta = {'reference': reference, 'increasing': {'color': COLOR_PRIMARY}} if reference else None
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta" if reference else "gauge+number",
        value=value,
        title={'text': title},
        delta=delta,
        gauge={
            'axis': {'range': [min_val, max_val]},
            'bar': {'color': COLOR_PRIMARY},
            'steps': [
                {'range': [min_val, max_val*0.6], 'color': "#f0f0f0"},
                {'range': [max_val*0.6, max_val], 'color': "#d3d3d3"}
            ]
    }))
    fig.update_layout(margin=dict(t=50, b=10))
    return fig

def style_metric(value, prev_value):
    color = COLOR_PRIMARY if value >= prev_value else COLOR_SECONDARY
    arrow = "↑" if value >= prev_value else "↓"
    return f"""
    <div style="text-align:center">
        <h1 style="color:{color};font-size:36px;margin:0">{value}</h1>
        <p style="color:{color};font-size:16px;margin:0">{arrow} {abs(value-prev_value)} vs Jan</p>
    </div>
    """

# Proses Data
def process_data(df):
    # Filter bulan
    df_feb = df[df['Month'].str.contains('Feb-25')]
    df_jan = df[df['Month'].str.contains('Jan-25')]
    
    # Hitung KPI
    for df_temp in [df_feb, df_jan]:
        df_temp['Usage'] = (df_temp['Expense'] / df_temp['Budget']) * 100
        df_temp['Target vs Real'] = (df_temp['Realization'] / df_temp['Target']) * 100
    
    return df_feb, df_jan

# Layout Dashboard
st.set_page_config(
    page_title="Performance Dashboard",
    layout="wide",
    page_icon="📊",
    initial_sidebar_state="expanded"
)

# Sidebar
with st.sidebar:
    st.header("Upload Data")
    uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])
    
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        df_feb, df_jan = process_data(df)
        st.session_state.df_feb = df_feb
        st.session_state.df_jan = df_jan
        
    st.header("Export")
    if st.button("Export to PDF"):
        st.warning("Fitur dalam pengembangan")

# Main Content
st.title("BU1 Performance Dashboard - Februari 2025")

if 'df_feb' not in st.session_state:
    st.warning("Silakan upload data CSV terlebih dahulu")
    st.stop()

# Tab Perspektif
perspective = st.radio(
    "Pilih Perspektif:",
    ["Financial", "Customer", "Quality", "Employee"],
    horizontal=True,
    key="perspective"
)

# Financial Perspective
if perspective == "Financial":
    st.subheader("Financial Performance")
    subdiv = st.selectbox("Pilih Subdiv", ["Subdiv 1", "Subdiv 2", "Subdiv 3"])
    
    # Filter Data
    data_feb = st.session_state.df_feb[
        (st.session_state.df_feb['Perspective'] == 'Financial') & 
        (st.session_state.df_feb['Subdiv'] == subdiv)
    ]
    
    data_jan = st.session_state.df_jan[
        (st.session_state.df_jan['Perspective'] == 'Financial') & 
        (st.session_state.df_jan['Subdiv'] == subdiv)
    ]
    
    # Layout Metric
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Budget vs Expense
        fig = px.bar(data_feb, 
                    x='Budget', 
                    y='Expense',
                    title="Budget vs Expense",
                    color_discrete_sequence=[COLOR_PRIMARY, COLOR_SECONDARY])
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Usage Gauge
        usage_feb = data_feb['Usage'].values[0]
        usage_jan = data_jan['Usage'].values[0]
        fig = create_gauge(usage_feb, "Usage (%)", 0, 100, usage_jan)
        st.plotly_chart(fig, use_container_width=True)
    
    with col3:
        # Scorecards
        st.markdown(style_metric(data_feb['Profit'].values[0], data_jan['Profit'].values[0]), 
                   unsafe_allow_html=True)
        st.markdown("***")
        st.markdown(style_metric(data_feb['Revenue'].values[0], data_jan['Revenue'].values[0]), 
                   unsafe_allow_html=True)

# Customer Perspective
elif perspective == "Customer":
    st.subheader("Customer Performance")
    produk = st.selectbox("Pilih Produk", ["PRODUK 1", "PRODUK 2", "PRODUK 3"])
    
    # Filter Data
    data_feb = st.session_state.df_feb[
        (st.session_state.df_feb['Perspective'] == 'Customer n Service') & 
        (st.session_state.df_feb['Produk'] == produk)
    ]
    
    data_jan = st.session_state.df_jan[
        (st.session_state.df_jan['Perspective'] == 'Customer n Service') & 
        (st.session_state.df_jan['Produk'] == produk)
    ]
    
    # Layout
    col1, col2 = st.columns(2)
    
    with col1:
        # Donut Chart
        fig = px.pie(data_feb, 
                    names='Produk', 
                    values='Number of customer',
                    hole=0.5,
                    title="Customer Distribution",
                    color_discrete_sequence=[COLOR_PRIMARY, COLOR_SECONDARY])
        st.plotly_chart(fig, use_container_width=True)
        
        # Tabel Historis
        st.write("Customer Satisfaction History")
        st.dataframe(pd.concat([data_jan, data_feb])[['Month', 'Customer satisfaction']], 
                    hide_index=True)
    
    with col2:
        # Gauge Satisfaction
        sat_feb = data_feb['Customer satisfaction'].values[0]
        sat_jan = data_jan['Customer satisfaction'].values[0]
        fig = create_gauge(sat_feb, "Satisfaction (Avg)", 0, 5, sat_jan)
        st.plotly_chart(fig, use_container_width=True)
        
        # Line Chart Comparison
        fig = px.line(
            pd.concat([data_jan, data_feb]),
            x='Month',
            y='Customer satisfaction',
            markers=True,
            title="Trend Satisfaction",
            color_discrete_sequence=[COLOR_PRIMARY]
        )
        st.plotly_chart(fig, use_container_width=True)

# Quality Perspective
elif perspective == "Quality":
    st.subheader("Quality Performance")
    subdiv = st.selectbox("Pilih Subdiv", ["Subdiv 1", "Subdiv 2", "Subdiv 3"])
    
    # Filter Data
    data_feb = st.session_state.df_feb[
        (st.session_state.df_feb['Perspective'] == 'Quality') & 
        (st.session_state.df_feb['Subdiv'] == subdiv)
    ]
    
    data_jan = st.session_state.df_jan[
        (st.session_state.df_jan['Perspective'] == 'Quality') & 
        (st.session_state.df_jan['Subdiv'] == subdiv)
    ]
    
    # Layout
    col1, col2 = st.columns(2)
    
    with col1:
        # Bar Chart
        fig = px.bar(data_feb,
                    x=['Target', 'Realization'],
                    y=[data_feb['Target'].values[0], data_feb['Realization'].values[0]],
                    title="Target vs Realization",
                    color_discrete_sequence=[COLOR_PRIMARY, COLOR_SECONDARY])
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Gauge
        velocity_feb = data_feb['Velocity'].values[0]
        velocity_jan = data_jan['Velocity'].values[0]
        fig = create_gauge(velocity_feb, "Velocity (%)", 0, 100, velocity_jan)
        st.plotly_chart(fig, use_container_width=True)
        
        quality_feb = data_feb['Quality'].values[0]
        quality_jan = data_jan['Quality'].values[0]
        fig = create_gauge(quality_feb, "Quality (%)", 0, 100, quality_jan)
        st.plotly_chart(fig, use_container_width=True)

# Employee Perspective
else:
    st.subheader("Employee Performance")
    subdiv = st.selectbox("Pilih Subdiv", ["Subdiv 1", "Subdiv 2", "Subdiv 3"])
    
    # Filter Data
    data_feb = st.session_state.df_feb[
        (st.session_state.df_feb['Perspective'] == 'Employee') & 
        (st.session_state.df_feb['Subdiv'] == subdiv)
    ]
    
    # Layout
    col1, col2 = st.columns(2)
    
    with col1:
        # Donut Chart
        current_mp = data_feb['Current MP'].values[0]
        needed_mp = data_feb['Needed MP'].values[0]
        fig = px.pie(
            values=[current_mp, needed_mp - current_mp],
            names=['Current MP', 'Kekurangan'],
            hole=0.5,
            title="Manpower Status",
            color_discrete_sequence=[COLOR_PRIMARY, COLOR_SECONDARY]
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Scorecards
        st.markdown(f"<h1 style='text-align:center;color:{COLOR_PRIMARY};'>{data_feb['Competency'].values[0]}%</h1>", 
                   unsafe_allow_html=True)
        st.markdown("<p style='text-align:center'>Average Competency</p>", 
                   unsafe_allow_html=True)
        
        st.markdown("***")
        
        st.markdown(f"<h1 style='text-align:center;color:{COLOR_SECONDARY};'>{data_feb['Turnover ratio'].values[0]}%</h1>", 
                   unsafe_allow_html=True)
        st.markdown("<p style='text-align:center'>Turnover Ratio</p>", 
                   unsafe_allow_html=True)

# Catatan Implementasi
st.sidebar.markdown("---")
with st.sidebar.expander("Catatan Implementasi"):
    st.markdown("""
    **Fitur yang sudah diimplementasikan:**
    1. Sistem upload CSV
    2. Visualisasi interaktif 4 perspektif
    3. Perbandingan bulan Januari-Februari
    4. Responsive layout
    5. Branding warna sesuai permintaan
    6. Filter Subdiv/Produk
    
    **Fitur dalam pengembangan:**
    - Ekspor PDF
    - Tampilan tab lainnya
    - Sistem alert otomatis
    """)
