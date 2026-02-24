import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt

# --- PAGE CONFIG ---
st.set_page_config(page_title="Space Rocket Path Analytics", layout="wide")

# --- STAGE 1 & 2: DATA LOADING & CLEANING ---
@st.cache_data
def load_and_preprocess():
    # Attempt to load the dataset
    try:
        df = pd.read_csv("rocket_missions.csv")
        
        # Cleaning: Convert types 
        df['Launch Date'] = pd.to_datetime(df['Launch Date'], errors='coerce')
        numeric_cols = ['Mission Cost', 'Payload Weight', 'Fuel Consumption', 'Distance from Earth', 'Scientific Yield', 'Crew Size']
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
        # Handle missing values 
        df = df.dropna(subset=['Mission Success', 'Payload Weight', 'Fuel Consumption'])
        return df
    except FileNotFoundError:
        st.error("Error: 'rocket_missions.csv' not found. Please upload it to your GitHub repo.")
        return None

df = load_and_preprocess()

# --- STAGE 3: MATHEMATICAL SIMULATION (Newton's 2nd Law) ---
# Goal: Calculate acceleration based on Thrust, Gravity, and Drag 
def run_physics_sim(fuel, payload):
    # Constants
    g = 9.81  # Gravity
    thrust = 1200000  # Newtons
    burn_rate = 400  # kg/s
    dry_mass = 45000  # kg
    dt = 1.0  # Time step
    
    data = []
    v, alt, t = 0.0, 0.0, 0
    curr_fuel = fuel
    
    while t < 150 and alt >= 0:
        total_mass = dry_mass + payload + curr_fuel
        
        # F = m * a -> a = F / m
        if curr_fuel > 0:
            net_force = thrust - (total_mass * g)
            curr_fuel -= burn_rate
        else:
            net_force = -(total_mass * g) # Only gravity if fuel is out
            
        acceleration = net_force / total_mass
        v += acceleration * dt
        alt += v * dt
        
        data.append({"Time (s)": t, "Altitude (m)": max(0, alt), "Velocity (m/s)": v})
        t += 1
        if alt < 0 and t > 1: break
        
    return pd.DataFrame(data)

# --- STAGE 4: BUILD VISUALIZATIONS ---
st.title("🚀 Rocket Launch Path & Mission Analytics")
st.markdown("Exploring rocket dynamics through Calculus and Real-World Data.")

if df is not None:
    # Sidebar Simulation Controls
    st.sidebar.header("Simulation Parameters")
    user_fuel = st.sidebar.slider("Initial Fuel (kg)", 40000, 150000, 80000)
    user_payload = st.sidebar.slider("Payload Weight (kg)", 2000, 30000, 10000)
    
    # 1. Simulation Result (Line Chart) 
    sim_results = run_physics_sim(user_fuel, user_payload)
    st.subheader("👨‍🔬 Rocket Physics Simulation")
    fig_sim = px.line(sim_results, x="Time (s)", y="Altitude (m)", title="Altitude over Time (Newtonian Model)")
    st.plotly_chart(fig_sim, use_container_width=True)

    # 2. Required Data Visualizations 
    st.divider()
    st.header("📊 Real-World Mission Insights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Visualization 1: Scatter Plot (Payload vs Fuel)
        fig1 = px.scatter(df, x="Payload Weight", y="Fuel Consumption", color="Mission Success",
                          title="Payload Weight vs. Fuel Consumption", trendline="ols")
        st.plotly_chart(fig1)

        # Visualization 2: Bar Chart (Cost: Success vs Failure)
        avg_cost = df.groupby("Mission Success")["Mission Cost"].mean().reset_index()
        fig2 = px.bar(avg_cost, x="Mission Success", y="Mission Cost", color="Mission Success",
                      title="Average Mission Cost: Success vs. Failure")
        st.plotly_chart(fig2)

        # Visualization 5: Scientific Yield vs Cost
        fig5 = px.scatter(df, x="Mission Cost", y="Scientific Yield", size="Crew Size",
                          title="Scientific Yield vs. Mission Cost")
        st.plotly_chart(fig5)

    with col2:
        # Visualization 3: Line Chart (Duration vs Distance)
        fig3 = px.line(df.sort_values("Distance from Earth"), x="Distance from Earth", y="Mission Duration",
                       title="Mission Duration vs. Distance from Earth")
        st.plotly_chart(fig3)

        # Visualization 4: Box Plot (Crew Size vs Success)
        fig4 = px.box(df, x="Mission Success", y="Crew Size", title="Crew Size vs. Mission Success %")
        st.plotly_chart(fig4)

        # Heatmap (Correlation)
        st.write("**Feature Correlation Heatmap**")
        fig_heat, ax = plt.subplots()
        sns.heatmap(df.corr(numeric_only=True), annot=True, cmap="viridis", ax=ax)
        st.pyplot(fig_heat)

    # Stage 2 Evidence: Data Exploration 
    if st.checkbox("Show Data Exploration (head/describe)"):
        st.write("First 5 Rows:", df.head())
        st.write("Statistical Summary:", df.describe())
