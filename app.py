import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# --- 1. APP CONFIGURATION ---
st.set_page_config(
    page_title="AstroDash | Mission Control",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. GAME MECHANICS & STATE ---
LEVEL_DATA = {
    1: {"xp_needed": 0, "target_alt": 15000, "max_thrust": 8000000, "title": "Flight Cadet", "color": "#00f2ff"},
    2: {"xp_needed": 200, "target_alt": 50000, "max_thrust": 15000000, "title": "Orbital Veteran", "color": "#00ff88"},
    3: {"xp_needed": 500, "target_alt": 150000, "max_thrust": 25000000, "title": "Deep Space Explorer", "color": "#bb00ff"},
    4: {"xp_needed": 1000, "target_alt": 300000, "max_thrust": 45000000, "title": "Galactic Commander", "color": "#ff007b"},
    5: {"xp_needed": 2000, "target_alt": 1000000, "max_thrust": 100000000, "title": "Starfleet Admiral", "color": "#ffaa00"}
}

if 'current_user' not in st.session_state:
    st.session_state['current_user'] = None

# --- FIXED SESSION STATE MIGRATION ---
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

# --- 3. CUSTOM CSS (SCI-FI THEME) ---
st.markdown("""
    <style>
    /* Deep space background */
    [data-testid="stAppViewContainer"] {
        background-color: #050814;
        background-image: radial-gradient(circle at 50% 0%, #1a1025 0%, #050814 70%);
        color: #E2E8F0;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #0b1021 !important;
        border-right: 1px solid #1f2937;
    }
    
    /* Neon glowing primary buttons */
    .stButton > button { 
        background: linear-gradient(90deg, #00f2ff 0%, #0077ff 100%);
        color: white !important; 
        font-weight: 800; 
        border: none;
        border-radius: 8px;
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .stButton > button:hover {
        box-shadow: 0 0 15px rgba(0, 242, 255, 0.5);
        transform: translateY(-2px);
    }

    /* Metric Styling */
    div[data-testid="stMetricValue"] {
        color: #00f2ff !important;
        font-family: 'Courier New', Courier, monospace;
        font-weight: bold;
    }
    
    /* Custom Achievement Cards */
    .achieve-card-unlocked {
        background: rgba(0, 255, 136, 0.1);
        border: 1px solid #00ff88;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 0 10px rgba(0, 255, 136, 0.2);
    }
    .achieve-card-locked {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid #333;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        color: #666;
        filter: grayscale(100%);
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
    path = [{"Time": 0, "Altitude": 0.0, "Velocity": 0.0, "Acceleration": 0.0}]
    
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
            path.append({"Time": t, "Altitude": alt, "Velocity": v, "Acceleration": accel})
            break
            
        path.append({"Time": t, "Altitude": max(0, alt), "Velocity": v, "Acceleration": accel})
        
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

# --- 5. PAGE ROUTING ---
def login_page():
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    _, col2, _ = st.columns([1.5, 2, 1.5])
    
    with col2:
        with st.container(border=True):
            st.markdown("<h1 style='text-align: center; color: #00f2ff;'>🚀 ASTRODASH</h1>", unsafe_allow_html=True)
            st.markdown("<h4 style='text-align: center; color: #a0aec0; margin-bottom: 30px;'>MISSION CONTROL TERMINAL</h4>", unsafe_allow_html=True)
            
            u = st.text_input("ENTER COMMANDER ID", placeholder="e.g. Shepard, Armstrong, Ripley...")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("INITIALIZE SYSTEMS", use_container_width=True):
                if u: 
                    st.session_state['current_user'] = u.upper()
                    st.rerun()
                else:
                    st.error("Authentication Failed: Commander ID required.")

def main_app():
    df = load_data()
    update_level()
    
    lvl = st.session_state['user_stats']['level']
    lvl_info = LEVEL_DATA.get(lvl, LEVEL_DATA[max(LEVEL_DATA.keys())])
    lvl_color = lvl_info['color']
    
    # --- PERSISTENT SIDEBAR ---
    with st.sidebar:
        st.markdown(f"### 👨‍🚀 CMDR. {st.session_state['current_user']}")
        st.divider()
        
        st.markdown(f"<h2 style='text-align: center; color: {lvl_color}; margin-bottom:0;'>RANK: LVL {lvl}</h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; font-size: 1.1em; color: #a0aec0;'>{lvl_info['title']}</p>", unsafe_allow_html=True)
        
        next_lvl = min(lvl + 1, max(LEVEL_DATA.keys()))
        next_xp = LEVEL_DATA[next_lvl]["xp_needed"]
        
        if lvl == max(LEVEL_DATA.keys()):
            st.progress(1.0)
            st.caption(f"XP: {st.session_state['user_stats']['xp']} (MAX RANK)")
        else:
            progress = min(st.session_state['user_stats']['xp'] / next_xp, 1.0)
            st.progress(progress)
            st.caption(f"XP: {st.session_state['user_stats']['xp']} / {next_xp}")
            
        st.markdown(f"""
        <div style="background-color: rgba(255,255,255,0.05); padding: 15px; border-radius: 8px; margin-top: 20px;">
            <p style="margin:0; font-size: 0.9em; color: #a0aec0;">CURRENT DIRECTIVE</p>
            <h4 style="margin:0; color: #00f2ff;">Reach {lvl_info['target_alt']:,}m</h4>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("ABORT MISSION (LOGOUT)", use_container_width=True):
            st.session_state['current_user'] = None
            st.rerun()

    # --- DASHBOARD TABS ---
    tab1, tab2, tab3 = st.tabs(["🚀 LAUNCH SIMULATOR", "📊 MISSION ANALYTICS", "🏅 ACHIEVEMENTS"])

    with tab1:
        st.markdown(f"## SIMULATION PROTOCOL: <span style='color:{lvl_color}'>{lvl_info['title']}</span>", unsafe_allow_html=True)
        st.write("Adjust orbital parameters to bypass the current altitude threshold.")
        st.markdown("<br>", unsafe_allow_html=True)
        
        col_s1, col_s2 = st.columns([1.2, 2])
        
        with col_s1:
            with st.container(border=True):
                st.subheader("⚙️ Flight Parameters")
                thrust = st.slider("Engine Thrust (N)", 1000000, lvl_info["max_thrust"], min(4000000, lvl_info["max_thrust"]), step=500000)
                fuel = st.slider("Fuel Mass (kg)", 50000, 300000, 100000, step=10000)
                payload = st.slider("Payload Mass (kg)", 5000, 100000, 20000, step=5000)
                
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🔥 IGNITION SEQUENCE START", use_container_width=True):
                    sim_data = run_physics_sim(fuel, payload, thrust)
                    st.session_state['sim_results'] = sim_data
                    st.session_state['user_stats']['simulations_run'] += 1
                    
                    max_alt = sim_data["Altitude"].max()
                    if max_alt > st.session_state['user_stats']['max_alt_reached']:
                        st.session_state['user_stats']['max_alt_reached'] = max_alt
                    
                    if max_alt >= lvl_info['target_alt']:
                        st.success(f"TARGET ACQUIRED! Max Altitude: {int(max_alt):,}m (+50 XP)")
                        st.session_state['user_stats']['xp'] += 50
                        st.rerun() 
                    elif max_alt <= 0:
                        st.error("CRITICAL FAILURE: Thrust-to-Weight ratio too low. Rocket did not clear the pad.")
                    else:
                        st.warning(f"SUB-ORBITAL. Max Altitude: {int(max_alt):,}m. Short of {lvl_info['target_alt']:,}m goal.")

        with col_s2:
            if 'sim_results' in st.session_state:
                results_df = st.session_state['sim_results']
                if not results_df.empty and results_df["Altitude"].max() > 0:
                    
                    # Live Telemetry Metrics
                    max_a = results_df["Altitude"].max()
                    max_v = results_df["Velocity"].max()
                    max_g = (results_df["Acceleration"].max() / 9.81)
                    
                    mc1, mc2, mc3 = st.columns(3)
                    mc1.metric("APOGEE", f"{int(max_a):,} m")
                    mc2.metric("MAX VELOCITY", f"{int(max_v):,} m/s")
                    mc3.metric("MAX G-FORCE", f"{max_g:.1f} G")
                    
                    # Trajectory Graph
                    fig = px.area(
                        results_df, x="Time", y="Altitude", 
                        title="FLIGHT TRAJECTORY", template="plotly_dark",
                        labels={"Time": "Time (s)", "Altitude": "Altitude (m)"},
                        color_discrete_sequence=['#00f2ff']
                    )
                    fig.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)', 
                        paper_bgcolor='rgba(0,0,0,0)',
                        margin=dict(l=0, r=0, t=40, b=0)
                    )
                    fig.add_hline(y=lvl_info['target_alt'], line_dash="dash", line_color="#ff007b", annotation_text="TARGET ALTITUDE", annotation_font_color="#ff007b")
                    st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.title("📊 Mission Analytics Archive")
        if df is not None:
            c_payload = get_col(df, 'payload')
            c_fuel = get_col(df, 'fuel')
            c_success = get_col(df, 'success')
            c_dist = get_col(df, 'distance')
            c_dur = get_col(df, 'duration')
            c_cost = get_col(df, 'cost')
            c_yield = get_col(df, 'yield')
            c_crew = get_col(df, 'crew')

            # Standardize Plotly template for this tab
            theme = "plotly_dark"
            colors = ['#00f2ff', '#ff007b', '#00ff88']

            c1, c2 = st.columns(2)
            with c1:
                if c_payload and c_fuel and c_success:
                    fig1 = px.scatter(df, x=c_payload, y=c_fuel, color=c_success, title="Payload vs Fuel Consumption", template=theme, color_discrete_sequence=colors)
                    st.plotly_chart(fig1, use_container_width=True)
                
                if c_dist and c_dur:
                    df_sorted = df.sort_values(c_dist)
                    fig3 = px.line(df_sorted, x=c_dist, y=c_dur, title="Mission Duration vs Distance", template=theme, color_discrete_sequence=colors)
                    st.plotly_chart(fig3, use_container_width=True)

                if c_cost and c_yield and c_crew and c_success:
                    fig5 = px.scatter(df, x=c_cost, y=c_yield, size=c_crew, color=c_success, title="Scientific Yield vs Cost", template=theme, color_discrete_sequence=colors)
                    st.plotly_chart(fig5, use_container_width=True)

            with c2:
                if c_success and c_cost:
                    avg_cost = df.groupby(c_success)[c_cost].mean().reset_index()
                    fig2 = px.bar(avg_cost, x=c_success, y=c_cost, color=c_success, title="Avg Cost: Success vs Failure", template=theme, color_discrete_sequence=colors)
                    st.plotly_chart(fig2, use_container_width=True)
                
                if c_success and c_crew:
                    fig4 = px.box(df, x=c_success, y=c_crew, color=c_success, title="Crew Size vs Success Rate", template=theme, color_discrete_sequence=colors)
                    st.plotly_chart(fig4, use_container_width=True)
                
                # --- UPGRADED PLOTLY HEATMAP ---
                st.write("**Feature Correlation Heatmap**")
                corr = df.corr(numeric_only=True)
                fig_h = px.imshow(
                    corr, text_auto=".2f", aspect="auto",
                    color_continuous_scale="Tealgrn", template=theme
                )
                fig_h.update_layout(margin=dict(l=0, r=0, t=30, b=0))
                st.plotly_chart(fig_h, use_container_width=True)
        else:
            st.error("Missing 'rocket_missions.csv'. Please upload it to your working directory.")

    with tab3:
        st.title("🏆 Commendations & Badges")
        st.write("Complete directives in the simulator to unlock permanent commendations.")
        st.markdown("<br>", unsafe_allow_html=True)
        
        cols = st.columns(3)
        stats = st.session_state['user_stats']
        
        achievements = [
            ("🌱 Flight Cadet", "Initialize your first simulation.", stats['simulations_run'] >= 1),
            ("🔥 Orbital Veteran", "Execute 5 total launch simulations.", stats['simulations_run'] >= 5),
            ("🌌 Deep Space Explorer", "Execute 15 total launch simulations.", stats['simulations_run'] >= 15),
            ("🏋️ Heavy Lifter", "Achieve Level 2 to unlock stronger engines.", stats['level'] >= 2),
            ("⭐ XP Hoarder", "Accumulate 1,000 total mission XP.", stats['xp'] >= 1000),
            ("🚀 Karman Line", "Break the 100,000m altitude barrier.", stats['max_alt_reached'] >= 100000)
        ]
        
        for i, (name, desc, status) in enumerate(achievements):
            with cols[i % 3]:
                if status: 
                    st.markdown(f"""
                        <div class="achieve-card-unlocked">
                            <h3 style="margin-bottom: 5px; color: #00ff88;">{name}</h3>
                            <p style="font-size: 0.9em; color: #E2E8F0;">{desc}</p>
                            <span style="background: #00ff88; color: black; padding: 2px 8px; border-radius: 12px; font-size: 0.8em; font-weight: bold;">UNLOCKED</span>
                        </div>
                        <br>
                    """, unsafe_allow_html=True)
                else: 
                    st.markdown(f"""
                        <div class="achieve-card-locked">
                            <h3 style="margin-bottom: 5px;">🔒 {name}</h3>
                            <p style="font-size: 0.9em;">{desc}</p>
                        </div>
                        <br>
                    """, unsafe_allow_html=True)

if __name__ == "__main__":
    if st.session_state['current_user']: main_app()
    else: login_page()
