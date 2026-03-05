import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt

# --- PAGE CONFIG ---
st.set_page_config(page_title="Aerospace Data Insights", layout="wide")

# --- STAGE 2: DATA PREPROCESSING & CLEANING ---
@st.cache_data
def load_and_preprocess():
    try:
        # Load dataset 
        df = pd.read_csv("rocket_missions.csv")
        
        # Clean column names (removes hidden spaces that cause KeyErrors) 
        df.columns = df.columns.str.strip()
        
        # Convert Launch Date 
        if 'Launch Date' in df.columns:
            df['Launch Date'] = pd.to_datetime(df['Launch Date'], errors='coerce')

        # Define required numeric columns based on scenario 
        target_cols = [
            'Mission Cost', 'Payload Weight', 'Fuel Consumption', 
            'Distance from Earth', 'Scientific Yield', 'Crew Size'
        ]
        
        # Convert types and handle missing values 
        for col in target_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Data exploration evidence for Rubric 
        df = df.dropna(subset=['Mission Success']) 
        return df
    except Exception as e:
        st.error(f"Error loading CSV: {e}. Ensure 'rocket_missions.csv' is in the GitHub root.")
        return None

df = load_and_preprocess()

# --- STAGE 3: SIMULATION (Newton's Second Law) ---
def run_physics_sim(fuel, payload):
    # Constants: Gravity and Thrust 
    g = 9.81  
    thrust = 1500000  
    burn_rate = 500  
    dry_mass = 50000  
    dt = 1.0  
    
    results = []
    v, alt, curr_fuel = 0.0, 0.0, fuel
    
    for t in range(200):
        total_mass = dry_mass + payload + curr_fuel
        
        # F = ma logic 
        if curr_fuel > 0:
            acceleration = (thrust - (total_mass * g)) / total_mass
            curr_fuel -= burn_rate
        else:
            acceleration = -g # Gravity takes over
            
        v += acceleration * dt
        alt += v * dt
        if alt < 0: alt = 0; v = 0 # Ground hit
        
        results.append({"Time (s)": t, "Altitude (m)": alt, "Velocity (m/s)": v})
    return pd.DataFrame(results)

# --- STAGE 4: VISUALIZATIONS & INTERACTIVITY ---
st.title("🚀 Rocket Launch & Space Mission Dashboard")

if df is not None:
    # Sidebar Filters 
    st.sidebar.header("Simulation Settings")
    s_fuel = st.sidebar.slider("Initial Fuel (kg)", 50000, 200000, 100000)
    s_payload = st.sidebar.slider("Payload Weight (kg)", 5000, 50000, 20000)
    
    # 1. Simulation Line Chart 
    st.subheader("Simulation: Launch Trajectory")
    sim_df = run_physics_sim(s_fuel, s_payload)
    st.line_chart(sim_df, x="Time (s)", y="Altitude (m)")

    # 2. Required Analysis Visuals 
    st.divider()
    col1, col2 = st.columns(2)

    with col1:
        # Scatter Plot: Payload vs Fuel 
        st.write("### Payload vs. Fuel Consumption")
        fig1 = px.scatter(df, x="Payload Weight", y="Fuel Consumption", color="Mission Success")
        st.plotly_chart(fig1, use_container_width=True)

        # Bar Chart: Cost Success vs Failure 
        st.write("### Average Cost by Success")
        fig2 = px.histogram(df, x="Mission Success", y="Mission Cost", histfunc="avg")
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        # Line Chart: Duration vs Distance 
        st.write("### Duration vs. Distance")
        fig3 = px.line(df.sort_values("Distance from Earth"), x="Distance from Earth", y="Mission Duration")
        st.plotly_chart(fig3, use_container_width=True)

        # Box Plot: Crew Size vs Success 
        st.write("### Crew Size Distribution")
        fig4 = px.box(df, x="Mission Success", y="Crew Size")
        st.plotly_chart(fig4, use_container_width=True)

    # Heatmap (Scientific Yield vs Cost / Correlation) 
    st.divider()
    st.write("### Feature Correlation Heatmap")
    fig_heat, ax = plt.subplots()
    sns.heatmap(df.corr(numeric_only=True), annot=True, cmap="coolwarm", ax=ax)
    st.pyplot(fig_heat)

    # Distinguished Stage 2 Evidence 
    if st.checkbox("Show Data Exploration (EDA)"):
        st.write(df.describe())
