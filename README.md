To achieve the **Distinguished (60 Marks)** grade, your `README.md` must demonstrate deep research, mathematical soundness, and clear connections to the real-world dataset.

Below is a professional `README.md` template tailored to your specific project and the requirements of your assessment brief.

---

# 🚀 Space Mission Launch Path Explorer

**Student Name:** ZENE SOPHIE ANAND 

**Student ID:** 1000442

**Course:** Artificial Intelligence

**Focus:** Mathematics for AI-I

**Assessment Type:** Summative Assessment (SA)

## 📌 Project Overview

This Streamlit application provides an interactive platform for visualizing and analyzing aerospace data patterns. The project applies mathematical models—including **Newton's Second Law** and **Differential Equations**—to simulate rocket trajectories and explore historical space mission data.

Built under **Scenario 1: Rocket Launch Path Visualization**, the app fulfills the requirement to identify trends between mission cost, payload weight, fuel consumption, and success rates.

---

## 🌐 Live Web App

> **🔗 [Click here to open the live Streamlit dashboard**](https://idai104-1000442-zene-sophie-anand-sa.streamlit.app/) ---

## 🎯 What Does This App Visualise?

The app includes the five compulsory visualizations and an interactive simulation:

| Section | Visualisations |
| --- | --- |
| 📈 **Simulation** | <br>**Live Rocket Trajectory:** Line chart showing Altitude over Time using step-by-step differential equations.
| 🚀 **Resource Analysis** | <br>**Scatter Plot:** Payload Weight vs. Fuel Consumption.
| 💰 **Financial Insights** | <br>**Bar Chart:** Average Mission Cost comparing Success vs. Failure.
| ⏳ **Logistics** | <br>**Line Chart:** Mission Duration vs. Distance from Earth.
| 👨‍🚀 **Crew & Success** | <br>**Box Plot:** Crew Size distribution across Mission Success categories.
| 🔬 **Scientific Value** | <br>**Scatter Plot:** Scientific Yield vs. Mission Cost.
| 🧠 **Correlations** | <br>**Heatmap:** Statistical relationships between all numeric mission factors.
---

## 🔬 Research Context — Rocket Dynamics & Newton's Law

As required by Stage 1 of the brief, this project integrates the following research insights:


**Newton’s Second Law ($F = ma$):** Rocket movement is determined by the net force, where upward **Thrust** must exceed the downward forces of **Gravity** and **Drag**.


 
**Mass Dynamics:** As fuel burns, the rocket's mass decreases significantly. Mathematically, this causes **acceleration to increase over time** even if engine thrust remains constant.



**Atmospheric Drag:** At higher altitudes, the atmosphere becomes thinner, leading to reduced air resistance (drag) and improved velocity.



### 💡 Guiding Questions Answered


**How does adding payload affect altitude?** Greater payload increases mass, which reduces initial acceleration ($a = F/m$), requiring more thrust to reach the same altitude.



**How long does it take to reach orbit?** Our simulation models the step-by-step update of velocity and altitude to estimate arrival times.



---

## 📁 Repository Structure

To meet the deployment criteria, the repository is organized as follows:

```
📦 IDAI104-1000442-ZENE-SOPHIE-ANAND-SA 
├── app.py                # Main application code with simulation & plots
├── requirements.txt      # List of dependencies (Streamlit, Pandas, Plotly, etc.)
├── rocket_missions.csv   # The processed aerospace dataset
└── README.md             # This documentation

```

---

## 🛠️ Technologies Used


**Streamlit:** For building the interactive web dashboard.



**Pandas:** For data preprocessing, cleaning, and type conversion.



**Plotly & Seaborn:** For creating interactive and statistical visualizations.



**NumPy:** For handling numerical calculations in the physics simulation.



---

## 📋 Assessment Checklist Fulfillment

* [x] **Stage 1:** Deep research into rocket dynamics and Newton's Laws.


* [x] **Stage 2:** Data cleaning (handling nulls, converting dates, and numeric types).


* [x] **Stage 3:** Mathematically sound simulation using differential logic.


* [x] **Stage 4:** Integration of all 5 compulsory visualizations.


* [x] **Stage 5:** Deployment on Streamlit Cloud with a clear README.



---

*🌌 Aerospace Data Insights | Mathematics for AI-I Summative Assessment*# IDAI104-1000442-ZENE-SOPHIE-ANAND-SA
