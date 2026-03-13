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
    [data-testid="stAppViewContainer"] {
        background-color: #050814;
        background-image: radial-gradient(circle at 50% 0%, #1a1025 0%, #050814 70%);
        color: #E2E8F0;
    }
    [data-testid="stSidebar"] {
        background-color: #0b1021 !important;
        border-right: 1px solid #1f2937;
    }
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
    div[data-testid="stMetricValue"] {
        color: #00f2ff !important;
        font-family: 'Courier New', Courier, monospace;
        font-weight: bold;
    }
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
    .insight-box {
        background: rgba(0, 242, 255, 0.05);
        border-left: 4px solid #00f2ff;
        padding: 15px;
        margin: 10px 0;
        border-radius: 4px;
        font-size: 0.9rem;
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
        
        if st.button("ABORT MISSION (LOGOUT)", use_container_width=True):
            st.session_state['current_user'] = None
            st.rerun()

    tab1, tab2, tab3, tab4 = st.tabs(["🚀 LAUNCH SIMULATOR", "📊 MISSION ANALYTICS", "🏅 ACHIEVEMENTS", "📖 FLIGHT MANUAL"])

    with tab1:
        st.markdown(f"## SIMULATION PROTOCOL: <span style='color:{lvl_color}'>{lvl_info['title']}</span>", unsafe_allow_html=True)
        col_s1, col_s2 = st.columns([1.2, 2])
        
        with col_s1:
            with st.container(border=True):
                st.subheader("⚙️ Flight Parameters")
                thrust = st.slider("Engine Thrust (N)", 1000000, lvl_info["max_thrust"], min(4000000, lvl_info["max_thrust"]), step=500000)
                fuel = st.slider("Fuel Mass (kg)", 50000, 300000, 100000, step=10000)
                payload = st.slider("Payload Mass (kg)", 5000, 100000, 20000, step=5000)
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
                        st.error("CRITICAL FAILURE: Thrust-to-Weight ratio too low.")
                    else:
                        st.warning(f"SUB-ORBITAL. Max Altitude: {int(max_alt):,}m.")

        with col_s2:
            if 'sim_results' in st.session_state:
                results_df = st.session_state['sim_results']
                if not results_df.empty and results_df["Altitude"].max() > 0:
                    mc1, mc2, mc3 = st.columns(3)
                    mc1.metric("APOGEE", f"{int(results_df['Altitude'].max()):,} m")
                    mc2.metric("MAX VELOCITY", f"{int(results_df['Velocity'].max()):,} m/s")
                    mc3.metric("MAX G-FORCE", f"{(results_df['Acceleration'].max() / 9.81):.1f} G")
                    
                    fig = px.area(results_df, x="Time", y="Altitude", template="plotly_dark", color_discrete_sequence=['#00f2ff'])
                    fig.add_hline(y=lvl_info['target_alt'], line_dash="dash", line_color="#ff007b", annotation_text="TARGET")
                    st.plotly_chart(fig, use_container_width=True)
                    st.markdown("""<div class="insight-box"><b>📡 TELEMETRY INSIGHT:</b> Apogee occurs when vertical velocity hits zero. To climb higher, optimize the initial <b>Thrust-to-Weight Ratio</b>.</div>""", unsafe_allow_html=True)

    with tab2:
        st.title("📊 Mission Analytics Archive")
        if df is not None:
            c_payload, c_fuel, c_success = get_col(df, 'payload'), get_col(df, 'fuel'), get_col(df, 'success')
            c_dist, c_dur, c_cost, c_yield = get_col(df, 'distance'), get_col(df, 'duration'), get_col(df, 'cost'), get_col(df, 'yield')
            c_crew = get_col(df, 'crew')

            c1, c2 = st.columns(2)
            with c1:
                if c_payload and c_fuel and c_success:
                    st.plotly_chart(px.scatter(df, x=c_payload, y=c_fuel, color=c_success, template="plotly_dark"), use_container_width=True)
                    st.markdown('<div class="insight-box"><b>🔍 INSIGHT:</b> Successful missions (cyan) follow a specific efficiency corridor between mass and fuel.</div>', unsafe_allow_html=True)
                if c_dist and c_dur:
                    st.plotly_chart(px.line(df.sort_values(c_dist), x=c_dist, y=c_dur, template="plotly_dark"), use_container_width=True)
                    st.markdown('<div class="insight-box"><b>🔍 INSIGHT:</b> Slope spikes may indicate gravitational slingshots or mid-flight engine failures.</div>', unsafe_allow_html=True)
                if c_cost and c_yield:
                    st.plotly_chart(px.scatter(df, x=c_cost, y=c_yield, size=c_crew, color=c_success, template="plotly_dark"), use_container_width=True)
                    st.markdown('<div class="insight-box"><b>🔍 INSIGHT:</b> Top-left entries represent high-efficiency missions with maximum scientific ROI.</div>', unsafe_allow_html=True)
            with c2:
                if c_success and c_cost:
                    st.plotly_chart(px.bar(df.groupby(c_success)[c_cost].mean().reset_index(), x=c_success, y=c_cost, template="plotly_dark"), use_container_width=True)
                    st.markdown('<div class="insight-box"><b>🔍 INSIGHT:</b> Failures often correlate with lower investment, pointing to structural or testing shortcuts.</div>', unsafe_allow_html=True)
                if c_success and c_crew:
                    st.plotly_chart(px.box(df, x=c_success, y=c_crew, template="plotly_dark"), use_container_width=True)
                    st.markdown('<div class="insight-box"><b>🔍 INSIGHT:</b> Successful missions show a consistent median crew size, suggesting an optimal team density.</div>', unsafe_allow_html=True)
                st.plotly_chart(px.imshow(df.corr(numeric_only=True), text_auto=".2f", template="plotly_dark"), use_container_width=True)
                st.markdown('<div class="insight-box"><b>🔍 INSIGHT:</b> Strong correlations (values near 1.0) reveal the hard physical limits of the current rocket tech.</div>', unsafe_allow_html=True)

    with tab3:
        st.title("🏆 Commendations & Badges")
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
                card_class = "achieve-card-unlocked" if status else "achieve-card-locked"
                status_txt = "UNLOCKED" if status else "LOCKED"
                st.markdown(f'<div class="{card_class}"><h3>{name}</h3><p>{desc}</p><b>{status_txt}</b></div><br>', unsafe_allow_html=True)

    with tab4:
        st.title("📖 Flight Manual & Orbital Physics")
        st.markdown("**Newton's Second Law Observation:**")
        st.write("Force equals mass times acceleration ($F = ma$). Net force determines your climb.")
        
        with st.container(border=True):
            st.markdown("### 🍎 Telemetry Principles")
            st.markdown("

[Image of Newton's second law of motion diagram]
")
            f1, f2, f3 = st.columns(3)
            f1.markdown("<h4 style='color:#00f2ff;'>🚀 Thrust</h4>", unsafe_allow_html=True)
            f1.write("Upward engine force.")
            f2.markdown("<h4 style='color:#00ff88;'>💨 Drag</h4>", unsafe_allow_html=True)
            f2.write("Atmospheric resistance.")
            f3.markdown("<h4 style='color:#ff007b;'>📦 Payload</h4>", unsafe_allow_html=True)
            f3.write("Vessel cargo weight.")
        
        st.markdown("### 🎯 Mission Planning Insights")
        st.markdown("""<div class="insight-box"><b>💡 ACADEMIC INSIGHT:</b> Launching in a vacuum would eliminate Drag, allowing for much higher velocities with identical fuel. This is why orbital stages are more efficient once they clear the atmosphere.</div>""", unsafe_allow_html=True)
        with st.expander("**Payload vs Altitude?**"): st.write("Heavier payloads decrease acceleration and apogee.")
        with st.expander("**Thrust vs Success?**"): st.write("Higher thrust overcomes gravity faster but increases structural G-stress.")

if __name__ == "__main__":
    if st.session_state['current_user']: main_app()
    else: login_page()
