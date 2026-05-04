import streamlit as st
import mysql.connector
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from streamlit_autorefresh import st_autorefresh
from sklearn.linear_model import LinearRegression
import numpy as np

# -------- PAGE CONFIG --------
st.set_page_config(page_title="Wind AI Dashboard", layout="wide")

# -------- FIXED DARK UI --------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg,#0f2027,#203a43,#2c5364);
    color: white;
}
section[data-testid="stSidebar"] {
    background-color: #111 !important;
}
h1, h2, h3, h4, h5, h6, p, span, div {
    color: white !important;
}
input, textarea {
    color: black !important;
}
button {
    background-color: #00c6ff !important;
    color: black !important;
    border-radius: 10px !important;
}
.metric-card {
    background: rgba(255,255,255,0.1);
    padding:20px;
    border-radius:20px;
    text-align:center;
    box-shadow:0 0 20px rgba(0,255,255,0.3);
}
</style>
""", unsafe_allow_html=True)

# -------- LOGIN SYSTEM --------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def login():
    st.title("🔐 Wind Energy Login")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if st.button("Login"):
        if u == "admin" and p == "1234":
            st.session_state.logged_in = True
            st.success("Login successful")
            st.rerun()
        else:
            st.error("Invalid credentials")

if not st.session_state.logged_in:
    login()
    st.stop()

# -------- AUTO REFRESH --------
st_autorefresh(interval=4000, key="refresh")

# -------- SIDEBAR --------
st.sidebar.title("🌬 Navigation")

page = st.sidebar.radio("Go to", [
    "🏠 Dashboard",
    "📈 Voltage",
    "🔋 Energy",
    "🤖 AI Prediction",
    "📊 Data Table"
])

if st.sidebar.button("🚪 Logout"):
    st.session_state.logged_in = False
    st.rerun()

# -------- DATABASE --------
def get_data():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="wind_db"
        )
        df = pd.read_sql("SELECT * FROM power_data ORDER BY time DESC LIMIT 30", conn)
        conn.close()

        if df.empty:
            return df

        df['power'] = df['voltage'] * df['current']
        return df.iloc[::-1]

    except Exception as e:
        st.error(f"Database Error: {e}")
        return pd.DataFrame()

df = get_data()

if df.empty:
    st.warning("⚠️ No data found. Run main.py")
    st.stop()

latest = df.iloc[-1]

# -------- DASHBOARD --------
if page == "🏠 Dashboard":

    st.title("🌬 Smart Wind Dashboard")
    st.info("Real-time turbine monitoring system")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(f"<div class='metric-card'><h3>⚡ Voltage</h3><h2>{latest['voltage']} V</h2></div>", unsafe_allow_html=True)

    with c2:
        st.markdown(f"<div class='metric-card'><h3>🔌 Current</h3><h2>{latest['current']} A</h2></div>", unsafe_allow_html=True)

    with c3:
        st.markdown(f"<div class='metric-card'><h3>💡 Power</h3><h2>{latest['power']:.2f} W</h2></div>", unsafe_allow_html=True)

    with c4:
        st.markdown(f"<div class='metric-card'><h3>🟢 Status</h3><h2>ACTIVE</h2></div>", unsafe_allow_html=True)

    st.success("System Running Successfully")

# -------- VOLTAGE --------
elif page == "📈 Voltage":

    st.header("Voltage Trend")

    fig = px.line(df, x='time', y='voltage')
    fig.update_layout(template="plotly_dark")

    st.plotly_chart(fig, use_container_width=True)

# -------- ENERGY --------
elif page == "🔋 Energy":

    st.header("Energy Output")

    fig = px.area(df, x='time', y='power')
    fig.update_layout(template="plotly_dark")

    st.plotly_chart(fig, use_container_width=True)

# -------- AI --------
elif page == "🤖 AI Prediction":

    st.header("AI Power Prediction")

    X = df[['voltage']]
    y = df['power']

    model = LinearRegression()
    model.fit(X, y)

    v_range = np.linspace(X.min(), X.max(), 50)
    pred = model.predict(v_range)

    fig = go.Figure()

    fig.add_trace(go.Scatter(x=df['voltage'], y=df['power'], mode='markers', name='Actual'))
    fig.add_trace(go.Scatter(x=v_range.flatten(), y=pred, mode='lines', name='Prediction'))

    fig.update_layout(template="plotly_dark")

    st.plotly_chart(fig, use_container_width=True)

# -------- DATA --------
elif page == "📊 Data Table":

    st.header("Live Data Table")
    st.dataframe(df)
