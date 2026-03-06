import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import random
from datetime import datetime

# --- 1. APP CONFIGURATION ---
st.set_page_config(
    page_title="AstroDash | Rocket Mission Control",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. SESSION STATE SETUP ---
if 'current_user' not in st.session_state:
    st.session_state['current_user'] = None

if 'user_stats' not in st.session_state:
    st.session_state['user_stats'] = {
        'xp': 0,
        'level': 1,
        'simulations_run': 0,
        'last_mission_success': None,
        'badges': []
    }

# --- 3. CUSTOM CSS (Space Theme) ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    div[data-testid="stMetricValue"] { color: #00f2ff !important; }
    .stButton > button { 
        background-image: linear-gradient(to right, #4facfe 0%, #00f2ff 100%);
        color: black !important; font-weight: bold; border: none;
    }
    .status-card {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# --- 4. DATA & PHYSICS LOGIC ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("rocket_missions.csv")
        df.columns = df.columns.str.strip()
        # Clean numeric data for distinguished marks 
        cols = ['Mission Cost', 'Payload Weight', 'Fuel Consumption', 'Distance from Earth']
        for col in cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        return df.dropna(subset=['Mission Success'])
    except:
        return None

def run_physics_sim(fuel, payload):
    g = 9.81
    thrust = 1500000
    burn_rate = 450
    dry_mass = 50000
    v, alt, t = 0.0, 0.0, 0
    curr_fuel = fuel
    path = []
    
    while t < 200:
        total_m = dry_mass + payload + curr_fuel
        if curr_fuel > 0:
            accel = (thrust - (total_m * g)) / total_m
            curr_fuel -= burn_rate
        else:
            accel = -g
        v += accel
        alt += v
        if alt < 0: alt = 0; break
        path.append({"Time": t, "Altitude": alt, "Velocity": v})
        t += 1
    return pd.DataFrame(path)

# --- 5. VISUAL COMPONENTS ---
def draw_rocket_avatar(level):
    fig, ax = plt.subplots(figsize=(2, 2))
    ax.set_facecolor('#0E1117')
    # Rocket Body
    ax.add_patch(patches.Rectangle((40, 20), 20, 50, color='#d1d5da'))
    # Nose Cone
    ax.add_patch(patches.Polygon([[40, 70], [60, 70], [50, 90]], color='#ff4b4b'))
    # Fins
    ax.add_patch(patches.Polygon([[40, 20], [30, 10], [40, 40]], color='#ff4b4b'))
    ax.add_patch(patches.Polygon([[60, 20], [70, 10], [60, 40]], color='#ff4b4b'))
    
    ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis('off')
    plt.text(50, 5, f"RANK: LVL {level}", color='white', ha='center', fontweight='bold')
    return fig

# --- 6. PAGE ROUTING ---
def login_page():
    st.title("🚀 AstroDash Mission Control")
    with st.container():
        u = st.text_input("Commander Name")
        if st.button("Initialize Systems"):
            if u: 
                st.session_state['current_user'] = u
                st.rerun()

def main_app():
    df = load_data()
    
    # --- PERSISTENT SIDEBAR ---
    with st.sidebar:
        st.header(f"👨‍🚀 Cmdr. {st.session_state['current_user']}")
        lvl = st.session_state['user_stats']['level']
        st.pyplot(draw_rocket_avatar(lvl))
        st.progress(st.session_state['user_stats']['xp'] / 500)
        st.caption(f"XP: {st.session_state['user_stats']['xp']} / 500")
        
        st.divider()
        st.subheader("💡 Flight Insights")
        st.info("Newton's 2nd Law: $a = (Thrust - Weight) / Mass$[cite: 2].")
        st.warning("Did you know? As fuel burns, mass decreases, causing acceleration to increase! [cite: 2]")
        
        if st.button("Aborts Mission (Logout)"):
            st.session_state['current_user'] = None
            st.rerun()

    # --- DASHBOARD TABS ---
    tab1, tab2, tab3 = st.tabs(["🚀 Launch Sim", "📊 Mission Analytics", "🏅 Achievements"])

    with tab1:
        st.title("Rocket Physics Simulator")
        col_s1, col_s2 = st.columns([1, 2])
        
        with col_s1:
            fuel = st.slider("Fuel Mass (kg)", 50000, 200000, 100000)
            payload = st.slider("Payload Mass (kg)", 5000, 50000, 20000)
            if st.button("🔥 IGNITION"):
                sim_data = run_physics_sim(fuel, payload)
                st.session_state['sim_results'] = sim_data
                st.session_state['user_stats']['xp'] += 50
                st.session_state['user_stats']['simulations_run'] += 1
                st.success("Launch complete! +50 XP")
        
        with col_s2:
            if 'sim_results' in st.session_state:
                fig = px.line(st.session_state['sim_results'], x="Time", y="Altitude", 
                             title="Flight Path Trajectory", template="plotly_dark")
                st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.title("Historical Mission Data")
        if df is not None:
            m1, m2, m3 = st.columns(3)
            m1.metric("Avg Mission Cost", f"${df['Mission Cost'].mean():.1f}M") [cite: 2]
            m2.metric("Success Rate", f"{(df['Mission Success'] == 'Success').mean()*100:.1%}") [cite: 2]
            m3.metric("Total Missions", len(df)) [cite: 2]
            
            # Required Visualizations for 15 marks 
            c1, c2 = st.columns(2)
            with c1:
                st.plotly_chart(px.scatter(df, x="Payload Weight", y="Fuel Consumption", color="Mission Success", title="Payload vs Fuel")) [cite: 2]
                st.plotly_chart(px.box(df, x="Mission Success", y="Crew Size", title="Crew Size vs Success")) [cite: 2]
            with c2:
                st.plotly_chart(px.bar(df, x="Mission Success", y="Mission Cost", title="Cost Analysis")) [cite: 2]
                st.write("**Correlation Heatmap**")
                fig_h, ax_h = plt.subplots()
                sns = __import__('seaborn')
                sns.heatmap(df.corr(numeric_only=True), annot=True, cmap="mako", ax=ax_h)
                st.pyplot(fig_h) [cite: 2]
        else:
            st.error("Missing 'rocket_missions.csv'. Please upload to GitHub.")

    with tab3:
        st.title("Commander Achievements")
        cols = st.columns(3)
        achievements = [
            ("🌱 Rookie", "Run 1 simulation", st.session_state['user_stats']['simulations_run'] >= 1),
            ("🔥 Veteran", "Run 5 simulations", st.session_state['user_stats']['simulations_run'] >= 5),
            ("🌌 Explorer", "Reach 500 XP", st.session_state['user_stats']['xp'] >= 500)
        ]
        for i, (name, desc, status) in enumerate(achievements):
            with cols[i % 3]:
                if status: st.success(f"**{name}**\n\n{desc}")
                else: st.error(f"**🔒 {name}**\n\n{desc}")

if __name__ == "__main__":
    if st.session_state['current_user']: main_app()
    else: login_page()
