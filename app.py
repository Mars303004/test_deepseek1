import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO

# Konfigurasi Warna dan Font
COLOR_PRIMARY = "#b42020"
COLOR_SECONDARY = "#0057c8"
COLOR_FONT = "#0057c8"
COLOR_BACKGROUND = "#FFFFFF"
COLOR_SCORECARD = "#f5f5f5"

# Fungsi Helper dengan revisi warna panah
def create_gauge(value, title, min_val, max_val, reference=None):
    delta_color = COLOR_SECONDARY if value >= reference else COLOR_PRIMARY if reference else None
    delta = {'reference': reference, 'increasing.color': '#00ff00', 'decreasing.color': '#ff0000'} if reference else None
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta" if reference else "gauge+number",
        value=value,
        title={'text': title, 'font': {'color': COLOR_FONT}},
        delta=delta,
        gauge={
            'axis': {'range': [min_val, max_val], 'tickcolor': COLOR_FONT},
            'bar': {'color': COLOR_PRIMARY},
            'steps': [
                {'range': [min_val, max_val*0.6], 'color': "#f0f0f0"},
                {'range': [max_val*0.6, max_val], 'color': "#d3d3d3"}
            ]
    }))
    fig.update_layout(margin=dict(t=50, b=10), font={'color': COLOR_FONT})
    return fig

def style_metric(value, prev_value):
    color = '#00ff00' if value >= prev_value else '#ff0000'
    arrow = "↑" if value >= prev_value else "↓"
    return f"""
    <div style="background-color:{COLOR_SCORECARD}; padding:20px; border-radius:10px; text-align:center">
        <h3 style="color:{COLOR_FONT};margin:0">{value}</h3>
        <p style="color:{color};margin:0">{arrow} {abs(value-prev_value)} vs prev</p>
    </div>
    """

# Proses Data dengan filter bulan
def process_data(df, selected_month):
    df['Month'] = pd.to_datetime(df['Month'], format='%b-%y')
    df_month = df[df['Month'] == selected_month]
    prev_month = df_month['Month'].iloc[0] - pd.DateOffset(months=1)
    df_prev = df[df['Month'] == prev_month]
    
    # Hitung KPI
    for df_temp in [df_month, df_prev]:
        df_temp['Usage'] = (df_temp['Expense'] / df_temp['Budget']) * 100
        df_temp['Target vs Real'] = (df_temp['Realization'] / df_temp['Target']) * 100
    
    return df_month, df_prev

# Layout Dashboard
st.set_page_config(
    page_title="Performance Dashboard",
    layout="wide",
    page_icon="📊",
    initial_sidebar_state="expanded"
)

# Sidebar dengan filter bulan
with st.sidebar:
    st.header("Upload Data")
    uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])
    
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        df['Month'] = pd.to_datetime(df['Month'], format='%b-%y')
        months = df['Month'].dt.strftime('%b-%y').unique()
        selected_month = st.selectbox("Pilih Bulan", options=months, index=len(months)-1)
        
        if st.button("Apply Filter"):
            selected_date = pd.to_datetime(selected_month, format='%b-%y')
            df_month, df_prev = process_data(df, selected_date)
            st.session_state.df_month = df_month
            st.session_state.df_prev = df_prev

# Main Content
st.title("BU1 Performance Dashboard")
st.markdown(f"<style>.stApp {{ background-color: {COLOR_BACKGROUND}; }}</style>", unsafe_allow_html=True)

if 'df_month' not in st.session_state:
    st.warning("Silakan upload data CSV terlebih dahulu")
    st.stop()

# Tab Perspektif
perspective = st.radio(
    "Pilih Perspektif:",
    ["Financial", "Customer", "Quality", "Employee"],
    horizontal=True,
    key="perspective"
)

# Financial Perspective - Revisi tab subdiv
if perspective == "Financial":
    st.subheader("Financial Performance")
    subdiv_tabs = st.tabs(["Subdiv 1", "Subdiv 2", "Subdiv 3"])
    
    for i, subdiv in enumerate(["Subdiv 1", "Subdiv 2", "Subdiv 3"]):
        with subdiv_tabs[i]:
            data_month = st.session_state.df_month[
                (st.session_state.df_month['Perspective'] == 'Financial') & 
                (st.session_state.df_month['Subdiv'] == subdiv)
            ]
            
            data_prev = st.session_state.df_prev[
                (st.session_state.df_prev['Perspective'] == 'Financial') & 
                (st.session_state.df_prev['Subdiv'] == subdiv)
            ]
            
            col1, col2, col3 = st.columns(3)
            with col1:
                fig = px.bar(data_month, 
                            x=['Budget', 'Expense'],
                            y=[data_month['Budget'].values[0], data_month['Expense'].values[0]],
                            title=f"Budget vs Expense - {subdiv}",
                            color_discrete_sequence=[COLOR_PRIMARY, COLOR_SECONDARY])
                st.plotly_chart(fig, use_container_width=True)

# Quality Perspective - Perbaikan error
elif perspective == "Quality":
    st.subheader("Quality Performance")
    subdiv_tabs = st.tabs(["Subdiv 1", "Subdiv 2", "Subdiv 3"])
    
    for i, subdiv in enumerate(["Subdiv 1", "Subdiv 2", "Subdiv 3"]):
        with subdiv_tabs[i]:
            data_month = st.session_state.df_month[
                (st.session_state.df_month['Perspective'] == 'Quality') & 
                (st.session_state.df_month['Subdiv'] == subdiv)
            ]
            
            data_prev = st.session_state.df_prev[
                (st.session_state.df_prev['Perspective'] == 'Quality') & 
                (st.session_state.df_prev['Subdiv'] == subdiv)
            ]
            
            # Perbaikan plot bar
            melted_df = pd.DataFrame({
                'Metric': ['Target', 'Realization'],
                'Value': [data_month['Target'].values[0], data_month['Realization'].values[0]]
            })
            
            col1, col2 = st.columns(2)
            with col1:
                fig = px.bar(melted_df,
                            x='Metric',
                            y='Value',
                            title=f"Target vs Realization - {subdiv}",
                            color='Metric',
                            color_discrete_map={
                                'Target': COLOR_PRIMARY,
                                'Realization': COLOR_SECONDARY
                            })
                st.plotly_chart(fig, use_container_width=True)

# Revisi untuk bagian lainnya...
