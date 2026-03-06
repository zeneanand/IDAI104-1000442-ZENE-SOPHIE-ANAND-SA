import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import seaborn as sns

# --- 1. APP CONFIGURATION ---
st.set_page_config(
    page_title="AstroDash | Mission Control",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. GAME MECHANICS & STATE ---
LEVEL_DATA = {
    1: {"xp_needed": 0, "target_alt": 15000, "max_thrust": 8000000, "title": "Flight Cadet"},
    2: {"xp_needed": 200, "target_alt": 50000, "max_thrust": 15000000, "title": "Orbital Veteran"},
    3: {"xp_needed": 500, "target_alt": 150000, "max_thrust": 25000000, "title": "Deep Space Explorer"},
    4: {"xp_needed": 1000, "target_alt": 300000, "max_thrust": 45000000, "title": "Galactic Commander"},
    5: {"xp_needed": 2000, "target_alt": 1000000, "max_thrust": 100000000, "title": "Starfleet Admiral"}
}

if 'current_user' not in st.session_state:
    st.session_state['current_user'] = None

# Session state migration to prevent NameError/KeyError on existing sessions
if 'user_stats' not in st.session_state:
    st.session_state['user_stats'] = {
        'xp': 0,
        'level': 1,
        'simulations_run': 0,
        'max_alt_reached': 0
    }
else:
    if 'max_alt_reached' not in st.session_state['user_stats']:
        st.session_state['user_stats']['max_alt_reached'] = 0
    if 'simulations_run' not in st.session_state['user_stats']:
        st.session_state['user_stats']['simulations_run'] = 0

if 'has_launched' not in st.session_state:
    st.session_state['has_launched'] = False

# --- 3. CUSTOM CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    div[data-testid="stMetricValue"] { color: #00f2ff !important; }
    .stButton > button { 
        background-image: linear-gradient(to right, #4facfe 0%, #00f2ff 100%);
        color: black !important; font-weight: bold; border: none;
    }
    </style>
""", unsafe_allow_html=True)

# --- 4. DATA & PHYSICS LOGIC ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("rocket_missions.csv")
        df.columns = df.columns.str.strip()
        # Clean numeric data as per rubric requirements [cite: 1, 2]
        for col in df.columns:
            if any(k in col.lower() for k in ['cost', 'weight', 'fuel', 'distance', 'yield', 'size', 'duration']):
                df[col] = pd.to_numeric(df[col], errors='coerce')
        return df
    except Exception:
        return None

def get_col(df, keyword):
    for col in df.columns:
        if keyword.lower() in col.lower():
            return col
    return None

def run_physics_sim(fuel, payload, thrust):
    # Simulation based on Newton's Second Law: F = ma [cite: 1]
    g = 9.81
    burn_rate = fuel / 100.0 if fuel > 0 else 1 
    dry_mass = 50000
    v, alt = 0.0, 0.0
    curr_fuel = fuel
    path = [{"Time": 0, "Altitude": 0.0, "Velocity": 0.0}]
    
    for t in range(1, 301): 
        total_m = dry_mass + payload + max(0, curr_fuel)
        if curr_fuel > 0:
            accel = (thrust - (total_m * g)) / total_m
            curr_fuel -= burn_rate
        else:
            accel = -g 
        v += accel
        alt += v
        if alt <= 0 and t > 2: 
            alt = 0
            path.append({"Time": t, "Altitude": alt, "Velocity": v})
            break
        path.append({"Time": t, "Altitude": max(0, alt), "Velocity": v})
    return pd.DataFrame(path)

def update_level():
    xp = st.session_state['user_stats']['xp']
    new_level = 1
    for lvl in sorted(LEVEL_DATA.keys(), reverse=True):
        if xp >= LEVEL_DATA[lvl]["xp_needed"]:
            new_level = lvl
            break
    if new_level > st.session_state['user_stats']['level']:
        st.balloons()
    st.session_state['user_stats']['level'] = new_level

def draw_rocket_avatar(level):
    fig, ax = plt.subplots(figsize=(2, 2))
    fig.patch.set_facecolor('#0E1117')
    ax.set_facecolor('#0E1117')
    ax.add_patch(patches.Rectangle((40, 20), 20, 50, color='#d1d5da'))
    ax.add_patch(patches.Polygon([[40, 70], [60, 70], [50, 90]], color='#ff4b4b'))
    ax.add_patch(patches.Polygon([[40, 20], [30, 10], [40, 40]], color='#ff4b4b'))
    ax.add_patch(patches.Polygon([[60, 20], [70, 10], [60, 40]], color='#ff4b4b'))
    ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis('off')
    return fig

# --- 5. MAIN APPLICATION LOGIC ---
def login_page():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🚀 AstroDash Mission Control")
        with st.container(border=True):
            u = st.text_input("Commander Name")
            if st.button("Initialize Systems", use_container_width=True):
                if u: 
                    st.session_state['current_user'] = u
                    st.rerun()

def main_app():
    df = load_data()
    update_level()
    lvl = st.session_state['user_stats']['level']
    lvl_info = LEVEL_DATA.get(lvl, LEVEL_DATA[max(LEVEL_DATA.keys())])
    
    with st.sidebar:
        st.header(f"👨‍🚀 Cmdr. {st.session_state['current_user']}")
        st.markdown(f"<h3 style='text-align: center; color: #ff4b4b;'>RANK: LVL {lvl}</h3>", unsafe_allow_html=True)
        st.pyplot(draw_rocket_avatar(lvl))
        
        # XP Progress 
        next_lvl = min(lvl + 1, max(LEVEL_DATA.keys()))
        next_xp = LEVEL_DATA[next_lvl]["xp_needed"]
        st.progress(min(st.session_state['user_stats']['xp'] / max(next_xp, 1), 1.0))
        st.write(f"Level Goal: Reach {lvl_info['target_alt']}m")
        
        if st.button("Logout"):
            st.session_state['current_user'] = None
            st.rerun()

    tab1, tab2, tab3 = st.tabs(["🚀 Launch Sim", "📊 Mission Analytics", "🏅 Achievements"])

    with tab1:
        st.title(f"Level {lvl} Simulator")
        col_s1, col_s2 = st.columns([1, 2])
        with col_s1:
            thrust = st.slider("Thrust (N)", 1000000, lvl_info["max_thrust"], 4000000)
            fuel = st.slider("Fuel (kg)", 50000, 300000, 100000)
            payload = st.slider("Payload (kg)", 5000, 100000, 20000)
            if st.button("🔥 IGNITION", use_container_width=True):
                st.session_state['has_launched'] = True
                sim_data = run_physics_sim(fuel, payload, thrust)
                st.session_state['sim_results'] = sim_data
                st.session_state['user_stats']['simulations_run'] += 1
                max_alt = sim_data["Altitude"].max()
                if max_alt >= lvl_info['target_alt']:
                    st.success(f"Success! Reached {int(max_alt)}m")
                    st.session_state['user_stats']['xp'] += 50
                st.session_state['user_stats']['max_alt_reached'] = max(st.session_state['user_stats']['max_alt_reached'], max_alt)
        with col_s2:
            if st.session_state.get('has_launched'):
                st.image("https://media.giphy.com/media/3o7btQ0NESY8zBkuo8/giphy.gif", use_container_width=True)
                if 'sim_results' in st.session_state:
                    fig = px.line(st.session_state['sim_results'], x="Time", y="Altitude", template="plotly_dark")
                    st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.title("Historical Mission Data Analysis")
        if df is not None:
            # Stage 4: Visualizations [cite: 1]
            c1, c2 = st.columns(2)
            with c1:
                st.plotly_chart(px.scatter(df, x=get_col(df, 'payload'), y=get_col(df, 'fuel'), color=get_col(df, 'success'), title="Payload vs Fuel"))
                st.plotly_chart(px.line(df.sort_values(get_col(df, 'distance')), x=get_col(df, 'distance'), y=get_col(df, 'duration'), title="Duration vs Distance"))
            with c2:
                st.plotly_chart(px.bar(df.groupby(get_col(df, 'success'))[get_col(df, 'cost')].mean().reset_index(), x=get_col(df, 'success'), y=get_col(df, 'cost'), title="Avg Cost by Success"))
                st.plotly_chart(px.box(df, x=get_col(df, 'success'), y=get_col(df, 'crew'), title="Crew Size vs Success"))
            
            # Correlation Heatmap [cite: 1]
            st.write("**Feature Correlation Heatmap**")
            fig_h, ax_h = plt.subplots(figsize=(8, 6))
            sns.heatmap(df.corr(numeric_only=True), annot=True, cmap="mako", ax=ax_h)
            st.pyplot(fig_h)

    with tab3:
        st.title("🏆 Achievements")
        stats = st.session_state['user_stats']
        achievements = [
            ("🌱 Rookie", "1 launch.", stats['simulations_run'] >= 1),
            ("🔥 Veteran", "5 launches.", stats['simulations_run'] >= 5),
            ("🚀 Karman", "Reach 100km.", stats['max_alt_reached'] >= 100000)
        ]
        cols = st.columns(3)
        for i, (name, desc, status) in enumerate(achievements):
            with cols[i % 3]:
                if status: st.success(f"**{name}**")
                else: st.error(f"**🔒 Locked**")

if __name__ == "__main__":
    if st.session_state['current_user']: main_app()
    else: login_page()
