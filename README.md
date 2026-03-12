
---

# 🚀 Space Mission Launch Path Explorer
**AstroDash | Mission Control Terminal**

**Student Name:** Zene Sophie Anand  
**Student ID:** 1000442  
**Course:** Artificial Intelligence  
**Focus:** Mathematics for AI-I  
**Assessment Type:** Summative Assessment (SA)  

## 📌 Project Overview

This Streamlit application provides an interactive platform for visualizing and analyzing aerospace data patterns. The project applies mathematical models—including **Newton's Second Law** and **Differential Equations**—to simulate rocket trajectories and explore historical space mission data.

Built under **Scenario 1: Rocket Launch Path Visualization**, the app fulfills the requirement to identify trends between mission cost, payload weight, fuel consumption, and success rates while gamifying the physics simulation.

---

## 🔗 Interactive Link

Access the live mission control dashboard directly via Streamlit Community Cloud:

> **[🚀 Launch AstroDash: Mission Control Here](https://idai104-1000442-zene-sophie-anand-sa.streamlit.app/)**)

---

## 🚀 Deployment Instructions

### Local Deployment
To run this application on your local machine, follow these steps:

1. **Clone the Repository:**
   ```bash
   git clone [https://github.com/your-username/IDAI104-1000442-ZENE-SOPHIE-ANAND-SA.git](https://github.com/your-username/IDAI104-1000442-ZENE-SOPHIE-ANAND-SA.git)
   cd IDAI104-1000442-ZENE-SOPHIE-ANAND-SA

```

2. **Install Dependencies:**
Ensure you have Python installed, then run:
```bash
pip install -r requirements.txt

```


3. **Launch the Application:**
```bash
streamlit run app.py

```



### Streamlit Cloud Deployment

This app is optimized for seamless deployment on Streamlit Community Cloud:

1. Push your code, `rocket_missions.csv`, images, and `requirements.txt` to a public GitHub repository.
2. Log in to [share.streamlit.io](https://share.streamlit.io/).
3. Click **"New app"**, select your repository, set the branch to `main`, and the main file path to `app.py`.
4. Click **Deploy**.

---

## ⚙️ Integration Details

This project tightly integrates mathematical principles with interactive UI components and data visualization:

* **Physics Engine Integration:** The `run_physics_sim()` function uses a discrete-time simulation (Euler method) to integrate acceleration into velocity, and velocity into altitude. It dynamically updates the rocket's mass loop-by-loop as fuel is consumed (burn rate).
* **UI-to-Math Binding:** Streamlit sliders (Thrust, Fuel, Payload) feed direct parameters into the physics simulation. Changes in the UI instantly recalculate the $F = ma$ equations and output a new Pandas DataFrame representing the flight path.
* **Telemetry & State Management:** Streamlit's `st.session_state` is integrated to track user progression, storing metrics like highest altitude reached, total simulations run, and accumulated XP across reruns.
* **Data Visualization Integration:** Plotly Express is hooked directly to the simulation outputs to generate a live trajectory graph, while historical CSV data is aggregated and mapped to dynamic scatter plots, box plots, and heatmaps.

---
## 🎯 What Does This App Visualise?

The app includes the five compulsory visualizations and an interactive simulation, broken down as follows:

| Section | Chart Type | Description / Data Visualised |
| :--- | :--- | :--- |
| 📈 **Simulation** | **Area Chart** | **Live Rocket Trajectory:** Visualises Altitude over Time using step-by-step differential equations. |
| 🚀 **Resource Analysis** | **Scatter Plot** | **Efficiency:** Compares Payload Weight against Fuel Consumption. |
| 💰 **Financial Insights** | **Bar Chart** | **Budgeting:** Displays Average Mission Cost comparing Success vs. Failure. |
| ⏳ **Logistics** | **Line Chart** | **Travel Metrics:** Tracks Mission Duration versus Distance from Earth. |
| 👨‍🚀 **Crew & Success** | **Box Plot** | **Human Factors:** Shows Crew Size distribution across Mission Success categories. |
| 🔬 **Scientific Value** | **Scatter Plot** | **ROI:** Maps the overall Scientific Yield against the Mission Cost. |
| 🧠 **Correlations** | **Heatmap** | **Statistical Overview:** Highlights the mathematical relationships between all numeric mission factors. |
---

# 📊 UI Dashboard Showcase

A visual overview of the application's user interface, featuring comprehensive data visualizations and management tools.

## 🖼️ SCREENSHOTS

Below are the visual highlights of the dashboard. All source images can be found in the `/SCREEN%20SHOT` directory.

| Side Panel & Overview | Statistics & Analytics | User Management |
| :---: | :---: | :---: |
| ![Step 1](./SCREEN%20SHOT/1.png) | ![Step 2](./SCREEN%20SHOT/2.png) | ![Step 3](./SCREEN%20SHOT/3.png) |
| **Main Navigation** | **Data Trends** | **Profile Settings** |

| Notifications | Financial Reports | System Health |
| :---: | :---: | :---: |
| ![Step 4](./SCREEN%20SHOT/4.png) | ![Step 5](./SCREEN%20SHOT/5.png) | ![Step 6](./SCREEN%20SHOT/6.png) |
| **Alerts UI** | **Revenue Charts** | **Server Logs** |

| Dark Mode | Mobile Responsive | Final Summary |
| :---: | :---: | :---: |
| ![Step 7](./SCREEN%20SHOT/7.png) | ![Step 8](./SCREEN%20SHOT/8.png) | ![Step 9](./SCREEN%20SHOT/9.png) |
| **Night Theme** | **Mobile View** | **Export Options** |

---

## 🚀 Key UI Features

* **Adaptive Layout:** Fully responsive design that works on desktop, tablet, and mobile.
* **Interactive Charts:** Dynamic data visualization using [Insert Library, e.g., Chart.js or Recharts].
* **Theme Support:** Seamless switching between Light and Dark modes (see SCREEN%20SHOT 1 and 7).
* **Real-time Updates:** Live data polling for system metrics.

## 🛠️ Tech Stack Used

* **Frontend:** React / Next.js / Vue
* **Styling:** Tailwind CSS / Styled Components
* **Icons:** Lucide React / FontAwesome
* **Charts:** D3.js / Chart.js

---
*Generated by the Project Development Team.*

## 🔬 Research Context — Rocket Dynamics & Newton's Law

As required by Stage 1 of the brief, this project integrates the following research insights:

* **Newton’s Second Law ($F = ma$):** Rocket movement is determined by the net force, where upward **Thrust** must exceed the downward forces of **Gravity** and **Drag**.
* **Mass Dynamics:** As fuel burns, the rocket's mass decreases significantly. Mathematically, this causes **acceleration to increase over time** even if engine thrust remains constant.
* **Atmospheric Drag:** At higher altitudes, the atmosphere becomes thinner, leading to reduced air resistance (drag) and improved velocity.

### 💡 Guiding Questions Answered

* **How does adding payload affect altitude?** Greater payload increases mass, which reduces initial acceleration ($a = F/m$), requiring more thrust to reach the same altitude.
* **How long does it take to reach orbit?** Our simulation models the step-by-step update of velocity and altitude to estimate arrival times and apogee.

---

# 📊 UI Dashboard Showcase

A visual overview of the application's user interface, featuring comprehensive data visualizations and management tools.

---

## 🖼️ SCREENSHOTS

Below are the visual highlights of the dashboard.

| Side Panel & Overview | Statistics & Analytics | User Management |
| :---: | :---: | :---: |
| ![Step 1](https://raw.githubusercontent.com/zeneanand/IDAI104-1000442-ZENE-SOPHIE-ANAND-SA/main/SCREEN%20SHOT/1.png) | ![Step 2](https://raw.githubusercontent.com/zeneanand/IDAI104-1000442-ZENE-SOPHIE-ANAND-SA/main/SCREEN%20SHOT/2.png) | ![Step 3](https://raw.githubusercontent.com/zeneanand/IDAI104-1000442-ZENE-SOPHIE-ANAND-SA/main/SCREEN%20SHOT/3.png) |
| **Main Navigation** | **Data Trends** | **Profile Settings** |

| Notifications | Financial Reports | System Health |
| :---: | :---: | :---: |
| ![Step 4](https://raw.githubusercontent.com/zeneanand/IDAI104-1000442-ZENE-SOPHIE-ANAND-SA/main/SCREEN%20SHOT/4.png) | ![Step 5](https://raw.githubusercontent.com/zeneanand/IDAI104-1000442-ZENE-SOPHIE-ANAND-SA/main/SCREEN%20SHOT/5.png) | ![Step 6](https://raw.githubusercontent.com/zeneanand/IDAI104-1000442-ZENE-SOPHIE-ANAND-SA/main/SCREEN%20SHOT/6.png) |
| **Alerts UI** | **Revenue Charts** | **Server Logs** |

| Dark Mode | Mobile Responsive | Final Summary |
| :---: | :---: | :---: |
| ![Step 7](https://raw.githubusercontent.com/zeneanand/IDAI104-1000442-ZENE-SOPHIE-ANAND-SA/main/SCREEN%20SHOT/7.png) | ![Step 8](https://raw.githubusercontent.com/zeneanand/IDAI104-1000442-ZENE-SOPHIE-ANAND-SA/main/SCREEN%20SHOT/8.png) | ![Step 9](https://raw.githubusercontent.com/zeneanand/IDAI104-1000442-ZENE-SOPHIE-ANAND-SA/main/SCREEN%20SHOT/9.png) |
| **Night Theme** | **Mobile View** | **Export Options** |

---

## 📁 Repository Structure

To meet the deployment criteria, the repository is organized as follows:

```text
📦 IDAI104-1000442-ZENE-SOPHIE-ANAND-SA 
├── app.py                                   # Main application code with simulation & plots
├── requirements.txt                         # List of dependencies
├── rocket_missions.csv                      # The processed aerospace dataset
├── Screenshot 2026-03-10 at 11.20.58 AM.jpg # App screenshot
├── Screenshot 2026-03-10 at 11.21.08 AM.jpg # App screenshot
├── Screenshot 2026-03-10 at 11.21.17 AM.jpg # App screenshot
├── ...                                      # Other screenshot files
└── README.md                                # This documentation

```

---

## 🛠️ Technologies Used

* **Streamlit:** For building the interactive web dashboard.
* **Pandas:** For data preprocessing, cleaning, and type conversion.
* **Plotly:** For creating interactive, high-fidelity visualizations.
* **NumPy:** For handling numerical calculations in the physics simulation.

---

## 📋 Assessment Checklist Fulfillment

* [x] **Stage 1:** Deep research into rocket dynamics and Newton's Laws.
* [x] **Stage 2:** Data cleaning (handling nulls, converting dates, and numeric types).
* [x] **Stage 3:** Mathematically sound simulation using differential logic.
* [x] **Stage 4:** Integration of all 5 compulsory visualizations.
* [x] **Stage 5:** Deployment on Streamlit Cloud with a clear README.

---

*🌌 Aerospace Data Insights | Mathematics for AI-I Summative Assessment*

```
