"""
LogSentinel Dashboard
=====================
Streamlit + Plotly dashboard for log analysis.
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json

# API URL
API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="LogSentinel",
    page_icon="🛡️",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem 0;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .threat-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
    }
    .safe-card {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
    }
</style>
""", unsafe_allow_html=True)


def main():
    # Header
    st.markdown('<h1 class="main-header">🛡️ LogSentinel</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #666;">AI-Powered Intelligent Web Log Analyzer</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/shield.png", width=80)
        st.title("Upload Log File")
        uploaded_file = st.file_uploader(
            "Choose a log file",
            type=['log', 'txt', 'csv', 'json'],
            help="Upload Apache, Nginx, JSON, CSV, or custom log files"
        )
        
        st.markdown("---")
        st.markdown("### Supported Formats")
        st.markdown("""
        - ✅ Apache Combined/CLF
        - ✅ Nginx
        - ✅ JSON/JSONL
        - ✅ CSV
        - ✅ Custom (AI-assisted)
        """)
    
    # Main content
    if uploaded_file is not None:
        # Analyze button
        if st.button("🔍 Analyze Log File", type="primary", use_container_width=True):
            analyze_file(uploaded_file)
    else:
        show_welcome()


def show_welcome():
    """Show welcome screen."""
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### 📊 Analytics
        - Traffic patterns
        - Peak hours
        - Popular URLs
        - Status codes
        """)
    
    with col2:
        st.markdown("""
        ### 🔒 Security
        - SQL injection
        - XSS attacks
        - Brute force
        - Vulnerability scanners
        """)
    
    with col3:
        st.markdown("""
        ### 🤖 ML Detection
        - Isolation Forest
        - Anomaly detection
        - Behavioral analysis
        - Risk scoring
        """)
    
    st.markdown("---")
    st.info("👆 Upload a log file to start analysis")


def analyze_file(uploaded_file):
    """Analyze uploaded file."""
    
    with st.spinner("🔄 Analyzing log file..."):
        try:
            # Send to API
            files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
            response = requests.post(f"{API_URL}/analyze", files=files)
            
            if response.status_code == 200:
                data = response.json()
                show_results(data)
            else:
                st.error(f"❌ Error: {response.text}")
                
        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to API. Make sure the server is running: `python run.py`")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")


def show_results(data):
    """Show analysis results."""
    
    # File Info
    file_info = data.get('file_info', {})
    format_info = data.get('format_detected', {})
    
    st.success(f"✅ Analysis complete for **{file_info.get('file_name', 'unknown')}**")
    
    # Format Detection
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Format", format_info.get('name', 'unknown'))
    with col2:
        confidence = format_info.get('confidence', 0)
        st.metric("Confidence", f"{confidence:.0%}")
    with col3:
        is_known = format_info.get('is_known', False)
        st.metric("Type", "Known" if is_known else "AI-Assisted")
    
    st.markdown("---")
    
    # Risk Score Section
    show_risk_score(data.get('risk_score', {}))
    
    st.markdown("---")
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Traffic", "🔒 Security", "🤖 ML Anomalies", "📋 Details"])
    
    with tab1:
        show_traffic(data.get('traffic', {}))
    
    with tab2:
        show_security(data.get('security', {}))
    
    with tab3:
        show_ml_anomalies(data.get('ml_anomalies', {}))
    
    with tab4:
        show_details(data)


def show_risk_score(risk_data):
    """Show risk score."""
    
    st.markdown("### 🎯 Risk Assessment")
    
    score = risk_data.get('total_risk_score', 0)
    level = risk_data.get('risk_level', 'LOW')
    recommendation = risk_data.get('recommendation', '')
    components = risk_data.get('components', {})
    
    # Risk gauge
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Gauge chart
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=score,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Risk Score", 'font': {'size': 24}},
            delta={'reference': 50},
            gauge={
                'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                'bar': {'color': "darkblue"},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, 30], 'color': '#4CAF50'},
                    {'range': [30, 60], 'color': '#FFC107'},
                    {'range': [60, 80], 'color': '#FF9800'},
                    {'range': [80, 100], 'color': '#F44336'}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': score
                }
            }
        ))
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Risk level
        colors = {
            'LOW': '#4CAF50',
            'MEDIUM': '#FFC107', 
            'HIGH': '#FF9800',
            'CRITICAL': '#F44336'
        }
        
        st.markdown(f"""
        <div style="background: {colors.get(level, '#gray')}; padding: 20px; border-radius: 10px; color: white;">
            <h2 style="margin:0;">Risk Level: {level}</h2>
            <p style="margin:10px 0 0 0;">{recommendation}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("")
        
        # Components
        st.markdown("**Risk Components:**")
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.metric("Rule Score", f"{components.get('rule_score', 0)}/40")
        with col_b:
            st.metric("ML Score", f"{components.get('ml_score', 0)}/30")
        with col_c:
            st.metric("Behavior Score", f"{components.get('behavior_score', 0)}/30")


def show_traffic(traffic_data):
    """Show traffic analytics."""
    
    st.markdown("### 📈 Traffic Overview")
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Requests", traffic_data.get('total_requests', 0))
    with col2:
        st.metric("Unique IPs", traffic_data.get('unique_ips', 0))
    with col3:
        peak_hours = traffic_data.get('peak_hours', {})
        peak = list(peak_hours.keys())[0] if peak_hours else "N/A"
        st.metric("Peak Hour", peak)
    with col4:
        st.metric("Status", "✅ Active")
    
    st.markdown("---")
    
    # Hourly distribution
    hourly = traffic_data.get('requests_per_hour', {})
    if hourly:
        st.markdown("#### ⏰ Hourly Distribution")
        
        df_hourly = pd.DataFrame({
            'Hour': [f"{h}:00" for h in sorted(hourly.keys())],
            'Requests': [hourly[h] for h in sorted(hourly.keys())]
        })
        
        fig = px.bar(
            df_hourly, 
            x='Hour', 
            y='Requests',
            color='Requests',
            color_continuous_scale='Viridis'
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Daily distribution
    daily = traffic_data.get('requests_per_day', {})
    if daily:
        st.markdown("#### 📅 Daily Distribution")
        
        df_daily = pd.DataFrame({
            'Day': list(daily.keys()),
            'Requests': list(daily.values())
        })
        
        fig = px.pie(
            df_daily,
            values='Requests',
            names='Day',
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)


def show_security(security_data):
    """Show security threats."""
    
    st.markdown("### 🚨 Security Threats")
    
    total_threats = security_data.get('total_threats', 0)
    
    if total_threats == 0:
        st.success("✅ No security threats detected!")
        return
    
    st.warning(f"⚠️ {total_threats} threats detected!")
    
    # Threat summary
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        sql_count = len(security_data.get('sql_injection', []))
        st.metric("💉 SQL Injection", sql_count)
    
    with col2:
        xss_count = len(security_data.get('xss', []))
        st.metric("📜 XSS", xss_count)
    
    with col3:
        traversal_count = len(security_data.get('path_traversal', []))
        st.metric("📁 Path Traversal", traversal_count)
    
    with col4:
        brute_count = len(security_data.get('brute_force', []))
        st.metric("🔐 Brute Force", brute_count)
    
    with col5:
        scanner_count = len(security_data.get('scanners', []))
        st.metric("🔍 Scanners", scanner_count)
    
    st.markdown("---")
    
    # Threat details
    col_sql, col_xss = st.columns(2)
    
    with col_sql:
        st.markdown("#### 💉 SQL Injection Attempts")
        sql_attempts = security_data.get('sql_injection', [])
        if sql_attempts:
            df_sql = pd.DataFrame(sql_attempts[:10])
            st.dataframe(df_sql, use_container_width=True)
        else:
            st.info("No SQL injection attempts detected")
    
    with col_xss:
        st.markdown("#### 📜 XSS Attempts")
        xss_attempts = security_data.get('xss', [])
        if xss_attempts:
            df_xss = pd.DataFrame(xss_attempts[:10])
            st.dataframe(df_xss, use_container_width=True)
        else:
            st.info("No XSS attempts detected")
    
    # Brute force
    st.markdown("#### 🔐 Brute Force Attempts")
    brute_force = security_data.get('brute_force', [])
    if brute_force:
        df_brute = pd.DataFrame(brute_force)
        st.dataframe(df_brute, use_container_width=True)
    else:
        st.info("No brute force attempts detected")
    
    # Suspicious IPs
    st.markdown("#### ⚠️ Suspicious IPs")
    suspicious = security_data.get('suspicious_ips', [])
    if suspicious:
        df_suspicious = pd.DataFrame(suspicious)
        st.dataframe(df_suspicious, use_container_width=True)
    else:
        st.info("No suspicious IPs detected")


def show_ml_anomalies(ml_data):
    """Show ML anomaly detection results."""
    
    st.markdown("### 🤖 ML Anomaly Detection")
    
    total_anomalies = ml_data.get('total_anomalies', 0)
    anomaly_pct = ml_data.get('anomaly_percentage', 0)
    model_info = ml_data.get('model_info', {})
    
    # Metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Anomalies", total_anomalies)
    
    with col2:
        st.metric("Anomaly Rate", f"{anomaly_pct:.1f}%")
    
    with col3:
        st.metric("Model Type", model_info.get('type', 'N/A'))
    
    st.markdown("---")
    
    # Model info
    st.markdown("#### 📊 Model Information")
    
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.metric("Trained On", f"{model_info.get('trained_on', 0)} samples")
    with col_b:
        st.metric("Contamination", model_info.get('contamination', 'N/A'))
    with col_c:
        st.metric("Features", model_info.get('features', 0))
    
    st.markdown("---")
    
    # Anomaly chart
    if total_anomalies > 0:
        st.markdown("#### 🎯 Anomaly Distribution")
        
        normal_count = model_info.get('trained_on', 0) - total_anomalies
        
        fig = px.pie(
            values=[normal_count, total_anomalies],
            names=['Normal', 'Anomaly'],
            color_discrete_sequence=['#4CAF50', '#F44336']
        )
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    # Top anomalies
    top_anomalies = ml_data.get('top_anomalies', [])
    if top_anomalies:
        st.markdown("#### 🚨 Top Anomalies")
        df_anomalies = pd.DataFrame(top_anomalies)
        st.dataframe(df_anomalies, use_container_width=True)
    else:
        st.success("✅ No anomalies detected!")


def show_details(data):
    """Show detailed information."""
    
    st.markdown("### 📋 Detailed Information")
    
    # Parsing stats
    st.markdown("#### 📊 Parsing Statistics")
    parsing_stats = data.get('parsing_stats', {})
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Lines", parsing_stats.get('total_lines', 0))
    with col2:
        st.metric("Parsed Lines", parsing_stats.get('parsed_lines', 0))
    with col3:
        st.metric("Failed Lines", parsing_stats.get('failed_lines', 0))
    
    st.markdown("---")
    
    # Raw JSON
    st.markdown("#### 📄 Raw JSON Response")
    with st.expander("Click to expand"):
        st.json(data)


if __name__ == "__main__":
    main()
