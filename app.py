import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt

# PAGE CONFIG
st.set_page_config(page_title="Aerospace Data Insights", layout="wide")

# --- STAGE 2: DATA PREPROCESSING & CLEANING ---
@st.cache_data
def load_and_clean_data():
    # Replace with your actual dataset link or local path
    df = pd.read_csv("rocket_missions.csv") 
    
    # Cleaning: Convert dates and handle numeric types 
    df['Launch Date'] = pd.to_datetime(df['Launch Date'], errors='coerce')
    numeric_cols = ['Mission Cost', 'Payload Weight', 'Fuel Consumption', 'Distance from Earth']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    df.dropna(subset=['Mission Success'], inplace=True) # Remove missing critical values
    return df

df = load_and_clean_data()

# --- STAGE 3: SIMULATION (MATHEMATICAL MODELING) ---
def run_simulation(initial_fuel, payload_mass):
    # Constants
    g = 9.81
    thrust = 1500000 
    burn_rate = 500  # fuel units per second
    dry_mass = 50000
    
    dt = 1.0
    time_steps = 200
    
    results = []
    velocity = 0
    altitude = 0
    current_fuel = initial_fuel
    
    for t in range(time_steps):
        total_mass = dry_mass + payload_mass + current_fuel
        
        if current_fuel > 0:
            current_thrust = thrust
            current_fuel -= burn_rate
        else:
            current_thrust = 0
        
        # Physics: a = (Thrust - Weight) / Mass 
        acceleration = (current_thrust - (total_mass * g)) / total_mass
        velocity += acceleration * dt
        altitude += velocity * dt
        
        if altitude < 0: altitude = 0; velocity = 0 # Ground limit
        
        results.append({"Time": t, "Altitude": altitude, "Velocity": velocity, "Fuel": current_fuel})
        
    return pd.DataFrame(results)

# --- STAGE 4: STREAMLIT DASHBOARD UI ---
st.title("🚀 Rocket Launch & Mission Analytics Dashboard")

# Sidebar Filters
st.sidebar.header("Simulation Settings")
fuel_input = st.sidebar.slider("Initial Fuel (kg)", 50000, 200000, 100000)
payload_input = st.sidebar.slider("Payload Weight (kg)", 5000, 50000, 20000)

if st.sidebar.button("Run Simulation"):
    sim_df = run_simulation(fuel_input, payload_input)
    fig_sim = px.line(sim_df, x="Time", y="Altitude", title="Simulated Rocket Path")
    st.plotly_chart(fig_sim, use_container_width=True)

# REQUIRED VISUALIZATIONS 
st.header("Real-World Mission Analysis")
col1, col2 = st.columns(2)

with col1:
    # 1. Scatter Plot: Payload vs Fuel
    fig1 = px.scatter(df, x="Payload Weight", y="Fuel Consumption", color="Mission Success", 
                      title="Payload Weight vs. Fuel Consumption")
    st.plotly_chart(fig1)

    # 2. Bar Chart: Cost Success vs Failure
    fig2 = px.histogram(df, x="Mission Success", y="Mission Cost", histfunc="avg", 
                        title="Average Mission Cost: Success vs. Failure")
    st.plotly_chart(fig2)

with col2:
    # 3. Line Chart: Duration vs Distance
    fig3 = px.line(df.sort_values("Distance from Earth"), x="Distance from Earth", y="Mission Duration",
                   title="Mission Duration vs. Distance")
    st.plotly_chart(fig3)

    # 4. Box Plot: Crew Size vs Success
    fig4 = px.box(df, x="Mission Success", y="Crew Size", title="Crew Size Distribution by Success")
    st.plotly_chart(fig4)

# 5. Correlation Heatmap
st.subheader("Correlation Analysis")
fig_corr, ax = plt.subplots()
sns.heatmap(df.corr(numeric_only=True), annot=True, cmap="YlGnBu", ax=ax)
st.pyplot(fig_corr)
