import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import seaborn as sns
import random

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
    </style>
""", unsafe_allow_html=True)

# --- 4. DATA & PHYSICS LOGIC ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("rocket_missions.csv")
        # Clean column names to prevent KeyErrors
        df.columns = df.columns.str.strip()
        
        # Target numeric columns required by the rubric
        numeric_cols = [
            'Mission Cost', 'Payload Weight', 'Fuel Consumption', 
            'Distance from Earth', 'Scientific Yield', 'Crew Size', 
            'Mission Duration'
        ]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
                
        # Drop rows missing the most critical classification data
        if 'Mission Success' in df.columns:
            df = df.dropna(subset=['Mission Success'])
            
        return df
    except Exception as e:
        return None

def run_physics_sim(fuel, payload):
    # Constants
    g = 9.81
    thrust = 1500000
    burn_rate = 450
    dry_mass = 50000
    
    v, alt = 0.0, 0.0
    curr_fuel = fuel
    path = []
    
    # Initialize point 0 to prevent Plotly ValueError (Empty DataFrame)
    path.append({"Time": 0, "Altitude": 0.0, "Velocity": 0.0})
    
    for t in range(1, 201):
        total_m = dry_mass + payload + curr_fuel
        
        # Physics Logic: F = ma
        if curr_fuel > 0:
            accel = (thrust - (total_m * g)) / total_m
            curr_fuel -= burn_rate
        else:
            accel = -g # Gravity takes over
            
        v += accel
        alt += v
        
        # Ground collision check
        if alt < 0: 
            alt = 0
            path.append({"Time": t, "Altitude": alt, "Velocity": v})
            break
            
        path.append({"Time": t, "Altitude": alt, "Velocity": v})
        
    return pd.DataFrame(path)

# --- 5. VISUAL COMPONENTS ---
def draw_rocket_avatar(level):
    fig, ax = plt.subplots(figsize=(2, 2))
    fig.patch.set_facecolor('#0E1117')
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
    
    # --- PERSISTENT SIDEBAR ---
    with st.sidebar:
        st.header(f"👨‍🚀 Cmdr. {st.session_state['current_user']}")
        lvl = st.session_state['user_stats']['level']
        
        fig_avatar = draw_rocket_avatar(lvl)
        st.pyplot(fig_avatar)
        
        st.progress(min(st.session_state['user_stats']['xp'] / 500, 1.0))
        st.caption(f"XP: {st.session_state['user_stats']['xp']} / 500")
        
        st.divider()
        st.subheader("💡 Flight Insights")
        st.info("Newton's 2nd Law: $a = (Thrust - Weight) / Mass$.")
        st.warning("As fuel burns, mass decreases, causing acceleration to increase even if thrust is constant! ")
        
        if st.button("Abort Mission (Logout)"):
            st.session_state['current_user'] = None
            st.rerun()

    # --- DASHBOARD TABS ---
    tab1, tab2, tab3 = st.tabs(["🚀 Launch Sim", "📊 Mission Analytics", "🏅 Achievements"])

    with tab1:
        st.title("Rocket Physics Simulator")
        st.write("Apply differential equations step-by-step to simulate a launch.")
        
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
                results_df = st.session_state['sim_results']
                if not results_df.empty:
                    fig = px.line(
                        results_df, 
                        x="Time", 
                        y="Altitude", 
                        title="Flight Path Trajectory", 
                        template="plotly_dark",
                        labels={"Time": "Time (s)", "Altitude": "Altitude (m)"}
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("Simulation error: No data generated.")

    with tab2:
        st.title("Historical Mission Data")
        if df is not None:
            # Data Exploration Evidence (For the 10 marks in Preprocessing)
            with st.expander("🔍 View Raw Dataset Exploration (EDA)"):
                st.write(df.head())
                st.write(df.describe())

            # The 5 Required Visualizations + Heatmap
            c1, c2 = st.columns(2)
            with c1:
                # 1. Scatter Plot (Payload vs Fuel)
                fig1 = px.scatter(df, x="Payload Weight", y="Fuel Consumption", color="Mission Success", title="1. Payload vs Fuel Consumption ")
                st.plotly_chart(fig1, use_container_width=True)
                
                # 3. Line Chart (Duration vs Distance)
                if 'Distance from Earth' in df.columns and 'Mission Duration' in df.columns:
                    df_sorted = df.sort_values("Distance from Earth")
                    fig3 = px.line(df_sorted, x="Distance from Earth", y="Mission Duration", title="3. Mission Duration vs Distance ")
                    st.plotly_chart(fig3, use_container_width=True)

                # 5. Scatter Plot (Scientific Yield vs Cost)
                if 'Scientific Yield' in df.columns and 'Mission Cost' in df.columns:
                    fig5 = px.scatter(df, x="Mission Cost", y="Scientific Yield", size="Crew Size", color="Mission Success", title="5. Scientific Yield vs Mission Cost ")
                    st.plotly_chart(fig5, use_container_width=True)

            with c2:
                # 2. Bar Chart (Cost vs Success)
                avg_cost = df.groupby("Mission Success")["Mission Cost"].mean().reset_index()
                fig2 = px.bar(avg_cost, x="Mission Success", y="Mission Cost", color="Mission Success", title="2. Avg Mission Cost: Success vs Failure ")
                st.plotly_chart(fig2, use_container_width=True)
                
                # 4. Box Plot (Crew Size vs Success)
                fig4 = px.box(df, x="Mission Success", y="Crew Size", title="4. Crew Size vs Mission Success ")
                st.plotly_chart(fig4, use_container_width=True)
                
                # 6. Correlation Heatmap
                st.write("**6. Feature Correlation Heatmap** ")
                fig_h, ax_h = plt.subplots()
                fig_h.patch.set_facecolor('#0E1117')
                ax_h.set_facecolor('#0E1117')
                sns.heatmap(df.corr(numeric_only=True), annot=True, cmap="mako", ax=ax_h)
                # Change tick colors to white for dark theme
                ax_h.tick_params(colors='white')
                st.pyplot(fig_h)
        else:
            st.error("Missing 'rocket_missions.csv'. Please upload it to your GitHub repository.")

    with tab3:
        st.title("Commander Achievements")
        cols = st.columns(3)
        achievements = [
            ("🌱 Flight Cadet", "Run 1 simulation", st.session_state['user_stats']['simulations_run'] >= 1),
            ("🔥 Orbital Veteran", "Run 5 simulations", st.session_state['user_stats']['simulations_run'] >= 5),
            ("🌌 Deep Space Explorer", "Reach 500 XP", st.session_state['user_stats']['xp'] >= 500)
        ]
        for i, (name, desc, status) in enumerate(achievements):
            with cols[i % 3]:
                if status: st.success(f"**{name}**\n\n{desc}")
                else: st.error(f"**🔒 {name}**\n\n{desc}")

if __name__ == "__main__":
    if st.session_state['current_user']: main_app()
    else: login_page()
