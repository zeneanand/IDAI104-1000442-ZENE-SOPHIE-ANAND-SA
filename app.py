import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt
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
    1: {"xp_needed": 100, "target_alt": 15000, "max_thrust": 8000000, "title": "Flight Cadet"},
    2: {"xp_needed": 300, "target_alt": 50000, "max_thrust": 15000000, "title": "Orbital Veteran"},
    3: {"xp_needed": 600, "target_alt": 150000, "max_thrust": 25000000, "title": "Deep Space Explorer"},
    4: {"xp_needed": 1000, "target_alt": 300000, "max_thrust": 40000000, "title": "Galactic Commander"},
}

if 'current_user' not in st.session_state:
    st.session_state['current_user'] = None

if 'user_stats' not in st.session_state:
    st.session_state['user_stats'] = {
        'xp': 0,
        'level': 1,
        'simulations_run': 0
    }

# --- 3. CUSTOM CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    div[data-testid="stMetricValue"] { color: #00f2ff !important; }
    .stButton > button { 
        background-image: linear-gradient(to right, #4facfe 0%, #00f2ff 100%);
        color: black !important; font-weight: bold; border: none;
    }
    .level-up-text { color: #00ff88; font-size: 24px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- 4. DATA & PHYSICS LOGIC ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("rocket_missions.csv")
        df.columns = df.columns.str.strip()
        numeric_cols = ['Mission Cost', 'Payload Weight', 'Fuel Consumption', 'Distance from Earth', 'Scientific Yield', 'Crew Size', 'Mission Duration']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        if 'Mission Success' in df.columns:
            df = df.dropna(subset=['Mission Success'])
        return df
    except Exception:
        return None

def run_physics_sim(fuel, payload, thrust):
    g = 9.81
    burn_rate = fuel / 100.0 if fuel > 0 else 1 # Burn all fuel in 100 seconds
    dry_mass = 50000
    
    v, alt = 0.0, 0.0
    curr_fuel = fuel
    path = [{"Time": 0, "Altitude": 0.0, "Velocity": 0.0}]
    
    for t in range(1, 301): # 300 seconds flight time
        total_m = dry_mass + payload + max(0, curr_fuel)
        
        # F = ma
        if curr_fuel > 0:
            accel = (thrust - (total_m * g)) / total_m
            curr_fuel -= burn_rate
        else:
            accel = -g # Engine cuts out, gravity takes over
            
        v += accel
        alt += v
        
        # Hit the ground
        if alt <= 0 and t > 5: 
            alt = 0
            path.append({"Time": t, "Altitude": alt, "Velocity": v})
            break
            
        path.append({"Time": t, "Altitude": alt, "Velocity": v})
        
    return pd.DataFrame(path)

def check_level_up():
    lvl = st.session_state['user_stats']['level']
    xp = st.session_state['user_stats']['xp']
    
    # Check if they have reached the max level
    if lvl < max(LEVEL_DATA.keys()):
        required_xp = LEVEL_DATA[lvl]["xp_needed"]
        if xp >= required_xp:
            st.session_state['user_stats']['level'] += 1
            st.balloons()
            return True
    return False

# --- 5. PAGE ROUTING ---
def login_page():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.title("🚀 AstroDash Mission Control")
        st.write("Login to access space telemetry and analytics.")
        with st.container(border=True):
            u = st.text_input("Commander Name")
            if st.button("Initialize Systems", use_container_width=True):
                if u: 
                    st.session_state['current_user'] = u
                    st.rerun()

def main_app():
    df = load_data()
    lvl = st.session_state['user_stats']['level']
    lvl_info = LEVEL_DATA.get(lvl, LEVEL_DATA[max(LEVEL_DATA.keys())])
    
    # --- PERSISTENT SIDEBAR ---
    with st.sidebar:
        st.header(f"👨‍🚀 Cmdr. {st.session_state['current_user']}")
        
        # Realistic Rocket Image based on level
        st.image("https://images.unsplash.com/photo-1517976487492-5750f3195933?auto=format&fit=crop&w=400&q=80", caption=f"Rank: {lvl_info['title']}")
        
        # XP Progress Bar
        next_xp = lvl_info["xp_needed"] if lvl < max(LEVEL_DATA.keys()) else st.session_state['user_stats']['xp']
        progress = min(st.session_state['user_stats']['xp'] / next_xp, 1.0) if next_xp > 0 else 1.0
        
        st.progress(progress)
        st.caption(f"XP: {st.session_state['user_stats']['xp']} / {next_xp}")
        st.write(f"**Level {lvl} Goal:** Reach {lvl_info['target_alt']}m")
        
        st.divider()
        if st.button("Abort Mission (Logout)"):
            st.session_state['current_user'] = None
            st.rerun()

    # --- DASHBOARD TABS ---
    tab1, tab2 = st.tabs(["🚀 Launch Sim", "📊 Mission Analytics"])

    with tab1:
        st.title(f"Level {lvl} Simulator: {lvl_info['title']}")
        st.write(f"**MISSION:** Adjust your parameters to break the altitude target of **{lvl_info['target_alt']} meters**!")
        
        col_s1, col_s2 = st.columns([1, 2])
        
        with col_s1:
            st.subheader("Flight Parameters")
            thrust = st.slider("Engine Thrust (N)", 1000000, lvl_info["max_thrust"], lvl_info["max_thrust"] // 2, step=500000)
            fuel = st.slider("Fuel Mass (kg)", 50000, 300000, 100000)
            payload = st.slider("Payload Mass (kg)", 5000, 100000, 20000)
            
            if st.button("🔥 IGNITION", use_container_width=True):
                sim_data = run_physics_sim(fuel, payload, thrust)
                st.session_state['sim_results'] = sim_data
                st.session_state['user_stats']['simulations_run'] += 1
                
                # Check Win Condition
                max_alt = sim_data["Altitude"].max()
                if max_alt >= lvl_info['target_alt']:
                    st.success(f"Target Reached! Max Altitude: {int(max_alt)}m (+50 XP)")
                    st.session_state['user_stats']['xp'] += 50
                    if check_level_up():
                        st.markdown("<p class='level-up-text'>🎉 LEVEL UP! New Engines Unlocked!</p>", unsafe_allow_html=True)
                elif max_alt <= 0:
                    st.error("Launch Failed: Thrust was too weak to lift the rocket's mass! Increase Thrust or decrease weight.")
                else:
                    st.warning(f"Max Altitude: {int(max_alt)}m. You fell short of the {lvl_info['target_alt']}m target.")

        with col_s2:
            if 'sim_results' in st.session_state:
                results_df = st.session_state['sim_results']
                if not results_df.empty and results_df["Altitude"].max() > 0:
                    fig = px.line(
                        results_df, x="Time", y="Altitude", 
                        title="Flight Path Trajectory", template="plotly_dark",
                        labels={"Time": "Time (s)", "Altitude": "Altitude (m)"}
                    )
                    # Add a red dashed line showing the target altitude
                    fig.add_hline(y=lvl_info['target_alt'], line_dash="dash", line_color="red", annotation_text="TARGET ALTITUDE")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.error("🚀 Grounded! The rocket was too heavy for that thrust setting.")

    with tab2:
        st.title("Historical Mission Data")
        if df is not None:
            with st.expander("🔍 View Raw Dataset Exploration (EDA) & Troubleshooting"):
                st.write("**Dataset Columns Found:**", list(df.columns))
                st.write(df.head())
                st.write(df.describe())

            c1, c2 = st.columns(2)
            with c1:
                if {"Payload Weight", "Fuel Consumption", "Mission Success"}.issubset(df.columns):
                    fig1 = px.scatter(df, x="Payload Weight", y="Fuel Consumption", color="Mission Success", title="1. Payload vs Fuel Consumption")
                    st.plotly_chart(fig1, use_container_width=True)
                
                if {"Distance from Earth", "Mission Duration"}.issubset(df.columns):
                    df_sorted = df.sort_values("Distance from Earth")
                    fig3 = px.line(df_sorted, x="Distance from Earth", y="Mission Duration", title="3. Mission Duration vs Distance")
                    st.plotly_chart(fig3, use_container_width=True)

                if {"Mission Cost", "Scientific Yield", "Crew Size", "Mission Success"}.issubset(df.columns):
                    fig5 = px.scatter(df, x="Mission Cost", y="Scientific Yield", size="Crew Size", color="Mission Success", title="5. Scientific Yield vs Mission Cost")
                    st.plotly_chart(fig5, use_container_width=True)

            with c2:
                if {"Mission Success", "Mission Cost"}.issubset(df.columns):
                    avg_cost = df.groupby("Mission Success")["Mission Cost"].mean().reset_index()
                    fig2 = px.bar(avg_cost, x="Mission Success", y="Mission Cost", color="Mission Success", title="2. Avg Mission Cost: Success vs Failure")
                    st.plotly_chart(fig2, use_container_width=True)
                
                if {"Mission Success", "Crew Size"}.issubset(df.columns):
                    fig4 = px.box(df, x="Mission Success", y="Crew Size", title="4. Crew Size vs Mission Success")
                    st.plotly_chart(fig4, use_container_width=True)
                
                st.write("**6. Feature Correlation Heatmap**")
                fig_h, ax_h = plt.subplots()
                fig_h.patch.set_facecolor('#0E1117')
                ax_h.set_facecolor('#0E1117')
                sns.heatmap(df.corr(numeric_only=True), annot=True, cmap="mako", ax=ax_h)
                ax_h.tick_params(colors='white')
                st.pyplot(fig_h)
        else:
            st.error("Missing 'rocket_missions.csv'. Please upload it to your GitHub repository.")

if __name__ == "__main__":
    if st.session_state['current_user']: main_app()
    else: login_page()
