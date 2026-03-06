import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import seaborn as sns
import time

# --- 1. APP CONFIGURATION ---
st.set_page_config(
    page_title="AstroDash | Mission Control",
    page_icon="🚀",
    layout="wide"
)

# --- 2. GAME MECHANICS & STATE ---
LEVEL_DATA = {
    1: {"xp_needed": 0, "target_alt": 15000, "max_thrust": 8000000, "title": "Flight Cadet"},
    2: {"xp_needed": 200, "target_alt": 50000, "max_thrust": 15000000, "title": "Orbital Veteran"},
    3: {"xp_needed": 500, "target_alt": 150000, "max_thrust": 25000000, "title": "Deep Space Explorer"},
    4: {"xp_needed": 1000, "target_alt": 300000, "max_thrust": 45000000, "title": "Galactic Commander"}
}

if 'user_stats' not in st.session_state:
    st.session_state['user_stats'] = {'xp': 0, 'level': 1, 'sims': 0, 'max_alt': 0}
if 'current_user' not in st.session_state:
    st.session_state['current_user'] = None

# --- 3. PHYSICS & DATA LOGIC ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("rocket_missions.csv")
        df.columns = df.columns.str.strip()
        # Ensure numeric types for rubrics 
        for col in df.columns:
            if any(k in col.lower() for k in ['cost', 'weight', 'fuel', 'distance', 'yield', 'size']):
                df[col] = pd.to_numeric(df[col], errors='coerce')
        return df
    except: return None

def run_physics_sim(fuel, payload, thrust):
    g, dt = 9.81, 1.0
    burn_rate, dry_mass = fuel / 100.0, 50000
    v, alt, path = 0.0, 0.0, [{"Time": 0, "Altitude": 0.0}]
    
    for t in range(1, 301):
        total_m = dry_mass + payload + max(0, fuel - (burn_rate * t))
        # Newton's Second Law: a = F/m 
        accel = (thrust - (total_m * g)) / total_m if (fuel - (burn_rate * t)) > 0 else -g
        v += accel * dt
        alt += v * dt
        if alt <= 0 and t > 5: break
        path.append({"Time": t, "Altitude": max(0, alt)})
    return pd.DataFrame(path)

# --- 4. MAIN APP ---
if st.session_state['current_user'] is None:
    st.title("🚀 AstroDash Login")
    user = st.text_input("Commander Name")
    if st.button("Login"):
        st.session_state['current_user'] = user
        st.rerun()
else:
    # Sidebar stats 
    stats = st.session_state['user_stats']
    # Level Up Logic
    current_lvl = stats['level']
    if current_lvl < 4 and stats['xp'] >= LEVEL_DATA[current_lvl + 1]['xp_needed']:
        st.session_state['user_stats']['level'] += 1
        st.balloons()
    
    with st.sidebar:
        st.header(f"👨‍🚀 {st.session_state['current_user']}")
        st.metric("Level", f"{stats['level']} - {LEVEL_DATA[stats['level']]['title']}")
        st.metric("XP Points", f"{stats['xp']}")
        if st.button("Logout"):
            st.session_state['current_user'] = None
            st.rerun()

    tab1, tab2, tab3 = st.tabs(["🚀 Launch", "📊 Analytics", "🏅 Achievements"])

    with tab1:
        lvl_info = LEVEL_DATA[stats['level']]
        st.subheader(f"Target Altitude: {lvl_info['target_alt']}m")
        
        col1, col2 = st.columns([1, 2])
        with col1:
            thr = st.slider("Thrust (N)", 1000000, lvl_info['max_thrust'], 5000000)
            fl = st.slider("Fuel (kg)", 50000, 300000, 100000)
            pay = st.slider("Payload (kg)", 5000, 100000, 20000)
            
            if st.button("🔥 IGNITION"):
                # 1. SHOW THE GIF
                placeholder = st.empty()
                with placeholder.container():
                    st.image("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNHJueGZueXF6NjZueXF6NjZueXF6NjZueXF6NjZueXF6NjZueXF6JmVwPXYxX2ludGVybmFsX2dpZl9ieV9pZCZjdD1n/3o7btQ0NESY8zBkuo8/giphy.gif")
                    st.write("🚀 LIFT OFF!")
                
                # 2. WAIT AND RESET
                time.sleep(4) 
                placeholder.empty()
                
                # 3. SHOW RESULTS
                sim_res = run_physics_sim(fl, pay, thr)
                st.session_state['sim_data'] = sim_res
                max_a = sim_res['Altitude'].max()
                if max_a >= lvl_info['target_alt']:
                    st.success(f"Success! Reached {int(max_a)}m")
                    st.session_state['user_stats']['xp'] += 100
                    st.session_state['user_stats']['max_alt'] = max(stats['max_alt'], max_a)
                else:
                    st.error(f"Failed! Only reached {int(max_a)}m")
                st.session_state['user_stats']['sims'] += 1

        with col2:
            if 'sim_data' in st.session_state:
                fig = px.line(st.session_state['sim_data'], x="Time", y="Altitude", template="plotly_dark")
                fig.add_hline(y=lvl_info['target_alt'], line_dash="dash", line_color="red")
                st.plotly_chart(fig)

    with tab2:
        df = load_data()
        if df is not None:
            st.title("Mission Analysis ")
            c1, c2 = st.columns(2)
            with c1:
                st.plotly_chart(px.scatter(df, x="Payload Weight (tons)", y="Fuel Consumption (tons)", color="Mission Success (%)"))
                st.plotly_chart(px.box(df, x="Mission Success (%)", y="Crew Size"))
            with c2:
                st.plotly_chart(px.bar(df, x="Mission Success (%)", y="Mission Cost (billion USD)", barmode="group"))
                # Clean Heatmap 
                fig_h, ax_h = plt.subplots()
                sns.heatmap(df.corr(numeric_only=True), annot=True, cmap="mako", ax=ax_h)
                plt.xticks(rotation=45)
                st.pyplot(fig_h)

    with tab3:
        st.title("🏅 Commander Achievements")
        st.write(f"Simulations Completed: {stats['sims']}")
        st.write(f"Highest Altitude: {int(stats['max_alt'])}m")
        if stats['max_alt'] > 100000: st.success("🌟 Achievement Unlocked: Karman Line Explorer!")
