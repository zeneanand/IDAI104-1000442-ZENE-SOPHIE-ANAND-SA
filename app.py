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

if 'user_stats' not in st.session_state:
    st.session_state['user_stats'] = {
        'xp': 0,
        'level': 1,
        'simulations_run': 0,
        'max_alt_reached': 0
    }
else:
    # Migration checks for older sessions
    if 'max_alt_reached' not in st.session_state['user_stats']:
        st.session_state['user_stats']['max_alt_reached'] = 0
    if 'simulations_run' not in st.session_state['user_stats']:
        st.session_state['user_stats']['simulations_run'] = 0

if 'show_launch_video' not in st.session_state:
    st.session_state['show_launch_video'] = False

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

# --- 5. VISUAL AVATAR ---
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
    update_level()
    
    lvl = st.session_state['user_stats']['level']
    lvl_info = LEVEL_DATA.get(lvl, LEVEL_DATA[max(LEVEL_DATA.keys())])
    
    # --- PERSISTENT SIDEBAR ---
    with st.sidebar:
        st.header(f"👨‍🚀 Cmdr. {st.session_state['current_user']}")
        
        st.markdown(f"<h3 style='text-align: center; color: #ff4b4b;'>RANK: LVL {lvl}</h3>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center;'>{lvl_info['title']}</p>", unsafe_allow_html=True)
        
        fig_avatar = draw_rocket_avatar(lvl)
        st.pyplot(fig_avatar)
        
        # XP Progress Bar
        next_lvl = min(lvl + 1, max(LEVEL_DATA.keys()))
        next_xp = LEVEL_DATA[next_lvl]["xp_needed"]
        
        if lvl == max(LEVEL_DATA.keys()):
            st.progress(1.0)
            st.caption(f"XP: {st.session_state['user_stats']['xp']} (MAX RANK ACHIEVED)")
        else:
            progress = min(st.session_state['user_stats']['xp'] / next_xp, 1.0)
            st.progress(progress)
            st.caption(f"XP: {st.session_state['user_stats']['xp']} / {next_xp}")
            st.write(f"**Level {lvl} Goal:** Reach {lvl_info['target_alt']}m")
        
        st.divider()
        if st.button("Abort Mission (Logout)"):
            st.session_state['current_user'] = None
            st.rerun()

    # --- DASHBOARD TABS ---
    tab1, tab2, tab3 = st.tabs(["🚀 Launch Sim", "📊 Mission Analytics", "🏅 Achievements"])

    with tab1:
        st.title(f"Level {lvl} Simulator: {lvl_info['title']}")
        st.write(f"**MISSION:** Adjust parameters to break the altitude target of **{lvl_info['target_alt']} meters**!")
        
        col_s1, col_s2 = st.columns([1, 2])
        
        with col_s1:
            st.subheader("Flight Parameters")
            thrust = st.slider("Engine Thrust (N)", 1000000, lvl_info["max_thrust"], min(4000000, lvl_info["max_thrust"]), step=500000)
            fuel = st.slider("Fuel Mass (kg)", 50000, 300000, 100000)
            payload = st.slider("Payload Mass (kg)", 5000, 100000, 20000)
            
            if st.button("🔥 IGNITION", use_container_width=True):
                # Run math immediately
                sim_data = run_physics_sim(fuel, payload, thrust)
                st.session_state['sim_results'] = sim_data
                st.session_state['user_stats']['simulations_run'] += 1
                
                max_alt = sim_data["Altitude"].max()
                if max_alt > st.session_state['user_stats']['max_alt_reached']:
                    st.session_state['user_stats']['max_alt_reached'] = max_alt
                
                if max_alt >= lvl_info['target_alt']:
                    st.success(f"Target Reached! Max Altitude: {int(max_alt)}m (+50 XP)")
                    st.session_state['user_stats']['xp'] += 50
                    st.session_state['show_launch_video'] = True  # Trigger the video!
                elif max_alt <= 0:
                    st.error("Launch Failed: Thrust too weak for current mass!")
                    st.session_state['show_launch_video'] = False
                else:
                    st.warning(f"Max Altitude: {int(max_alt)}m. Fell short of {lvl_info['target_alt']}m.")
                    st.session_state['show_launch_video'] = True # Still show video for trying

        with col_s2:
            # Show the video player if triggered
            if st.session_state['show_launch_video']:
                with st.expander("🎬 Mission Launch Camera Replay", expanded=True):
                    # Using the exact video link requested in your assignment rubric!
                    st.video("https://www.youtube.com/watch?v=22OCPbfY5SE")
                    
            if 'sim_results' in st.session_state:
                results_df = st.session_state['sim_results']
                if not results_df.empty and results_df["Altitude"].max() > 0:
                    fig = px.line(
                        results_df, x="Time", y="Altitude", 
                        title="Flight Path Trajectory", template="plotly_dark",
                        labels={"Time": "Time (s)", "Altitude": "Altitude (m)"}
                    )
                    fig.add_hline(y=lvl_info['target_alt'], line_dash="dash", line_color="red", annotation_text="TARGET ALTITUDE")
                    st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.title("Historical Mission Data")
        if df is not None:
            c_payload = get_col(df, 'payload')
            c_fuel = get_col(df, 'fuel')
            c_success = get_col(df, 'success')
            c_dist = get_col(df, 'distance')
            c_dur = get_col(df, 'duration')
            c_cost = get_col(df, 'cost')
            c_yield = get_col(df, 'yield')
            c_crew = get_col(df, 'crew')

            c1, c2 = st.columns(2)
            with c1:
                if c_payload and c_fuel and c_success:
                    fig1 = px.scatter(df, x=c_payload, y=c_fuel, color=c_success, title="1. Payload vs Fuel Consumption")
                    st.plotly_chart(fig1, use_container_width=True)
                
                if c_dist and c_dur:
                    df_sorted = df.sort_values(c_dist)
                    fig3 = px.line(df_sorted, x=c_dist, y=c_dur, title="3. Mission Duration vs Distance")
                    st.plotly_chart(fig3, use_container_width=True)

                if c_cost and c_yield and c_crew and c_success:
                    fig5 = px.scatter(df, x=c_cost, y=c_yield, size=c_crew, color=c_success, title="5. Scientific Yield vs Cost")
                    st.plotly_chart(fig5, use_container_width=True)

            with c2:
                if c_success and c_cost:
                    avg_cost = df.groupby(c_success)[c_cost].mean().reset_index()
                    fig2 = px.bar(avg_cost, x=c_success, y=c_cost, color=c_success, title="2. Avg Mission Cost: Success vs Failure")
                    st.plotly_chart(fig2, use_container_width=True)
                
                if c_success and c_crew:
                    fig4 = px.box(df, x=c_success, y=c_crew, title="4. Crew Size vs Mission Success")
                    st.plotly_chart(fig4, use_container_width=True)
                
                st.write("**6. Feature Correlation Heatmap**")
                fig_h, ax_h = plt.subplots(figsize=(8, 6))
                fig_h.patch.set_facecolor('#0E1117')
                ax_h.set_facecolor('#0E1117')
                sns.heatmap(df.corr(numeric_only=True), annot=True, cmap="mako", ax=ax_h, fmt=".2f")
                ax_h.tick_params(colors='white', labelsize=8)
                plt.xticks(rotation=45, ha='right')
                plt.tight_layout()
                st.pyplot(fig_h)
        else:
            st.error("Missing 'rocket_missions.csv'. Please upload it to your GitHub repository.")

    with tab3:
        st.title("🏆 Commander Achievements")
        st.write("Complete tasks in the simulator to unlock badges!")
        
        cols = st.columns(3)
        stats = st.session_state['user_stats']
        
        achievements = [
            ("🌱 Flight Cadet", "Run your first simulation.", stats['simulations_run'] >= 1),
            ("🔥 Orbital Veteran", "Run 5 total simulations.", stats['simulations_run'] >= 5),
            ("🌌 Deep Space Explorer", "Run 15 total simulations.", stats['simulations_run'] >= 15),
            ("🏋️ Heavy Lifter", "Reach Level 2 to unlock stronger engines.", stats['level'] >= 2),
            ("⭐ XP Hoarder", "Accumulate 1000 total XP.", stats['xp'] >= 1000),
            ("🚀 Karman Line", "Reach an altitude of 100,000m.", stats['max_alt_reached'] >= 100000)
        ]
        
        for i, (name, desc, status) in enumerate(achievements):
            with cols[i % 3]:
                if status: 
                    st.success(f"**{name}**\n\n{desc}")
                else: 
                    st.error(f"**🔒 {name}**\n\n{desc}")

if __name__ == "__main__":
    if st.session_state['current_user']: main_app()
    else: login_page()
