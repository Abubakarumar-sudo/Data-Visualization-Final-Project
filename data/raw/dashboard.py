


import json
import os
import sys

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, os.path.dirname(__file__))
from sensors import berlin_to_rotterdam_shipment  # noqa: E402
from simulate import detection_latency_hours, save_records  # noqa: E402

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

st.set_page_config(page_title="IoT Supply Chain Monitoring" "Abubakar Umar Dangi", layout="wide", page_icon="📦")

# ---- Palette matching the project's report/poster/pitch deck -------------- #
NAVY = "#0B3D5C"
TEAL = "#1C7293"
AMBER = "#F2A541"
MUTED = "#4E6E87"

st.markdown(
    f"""
    <style>
    .stApp {{ background-color: #F3F8FA; }}
    .metric-card {{
        background: white; border-radius: 10px; padding: 1rem 1.2rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }}
    </style>
    """,
    unsafe_allow_html=True,
)



# Data loading / generation


@st.cache_data(show_spinner=False)
def get_shipment_data(shipment_id: str, seed: int, threshold: float):
    shipment = berlin_to_rotterdam_shipment(shipment_id=shipment_id, seed=seed)
    shipment.temp_alert_threshold_c = threshold
    records = shipment.simulate()
    df = pd.DataFrame(records)
    latency = detection_latency_hours(records)
    save_records(records, f"shipment_{shipment_id}")
    return df, latency, shipment



# Sidebar controls


st.sidebar.title("📦 Shipment Control")
shipment_id = st.sidebar.text_input("Shipment ID", "A-1042")
seed = st.sidebar.number_input("Random seed", value=40, step=1)
threshold = st.sidebar.slider("Temperature Alert Threshold (°C)", 4.0, 12.0, 8.0, 0.5)
st.sidebar.caption("Route: Berlin, DE → Rotterdam, NL (655 km, 12h simulated transit)")

df, latency, shipment = get_shipment_data(shipment_id, seed, threshold)

st.sidebar.markdown("---")
st.sidebar.markdown("### Research Question")
st.sidebar.info("Does real-time IoT sensor data actually improve transparency in a supply chain?")


# Header


st.title("IoT-Based Real-Time Supply Chain Monitoring")

st.caption("Msc-Data Science project by Abubakar Umar Dangi") 
        
st.caption(f"Shipment **{shipment_id}** · {shipment.route.origin_name} → {shipment.route.dest_name}")

tab_live, tab_alerts, tab_analysis = st.tabs(["🛰️ Live Monitoring", "🔔 Alert Log", "⚖️ Transparency Scorecard"])


# TAB 1: Live Monitoring


with tab_live:
    col1, col2, col3, col4 = st.columns(4)
    latest = df.iloc[-1]
    col1.metric("🌡️ Current Temperature", f"{latest['temperature_c']} °C",
                delta=f"threshold {threshold}°C", delta_color="off")
    col2.metric("Cumulative CO₂ (kg)", f"{latest['cumulative_co2_kg']:.1f} kg")
    col3.metric("Distance Covered", f"{latest['distance_km']} / {shipment.route.distance_km} km")
    n_alerts = int(df["temp_alert"].sum())
    col4.metric("Alert Readings", n_alerts, delta="ALERT" if n_alerts else "Normal",
                delta_color="inverse" if n_alerts else "normal")

    st.markdown("### Route Map")
    fig_map = px.line_mapbox(df, lat="lat", lon="lon", zoom=5, height=420)
    fig_map.add_scattermapbox(
        lat=[df.iloc[-1]["lat"]], lon=[df.iloc[-1]["lon"]],
        mode="markers", marker=dict(size=15, color=AMBER), name="Current position",
    )
    fig_map.update_layout(mapbox_style="carto-positron", margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig_map, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### Temperature vs. Alert Threshold")
        fig_temp = go.Figure()
        fig_temp.add_trace(go.Scatter(x=df["hour"], y=df["temperature_c"], name="Temperature (°C)",
                                       line=dict(color=TEAL, width=3)))
        fig_temp.add_trace(go.Scatter(x=df["hour"], y=df["temp_threshold_c"], name="Alert threshold",
                                       line=dict(color="#C0392B", width=2, dash="dash")))
        fig_temp.update_layout(height=350, margin=dict(l=10, r=10, t=10, b=10),
                                xaxis_title="Hour", yaxis_title="°C", plot_bgcolor="white")
        st.plotly_chart(fig_temp, use_container_width=True)
    with c2:
        st.markdown("### Cumulative Emissions")
        fig_co2 = px.area(df, x="hour", y="cumulative_co2_kg", color_discrete_sequence=[TEAL])
        fig_co2.update_layout(height=350, margin=dict(l=10, r=10, t=10, b=10),
                               xaxis_title="Hour", yaxis_title="kg CO₂", plot_bgcolor="white")
        st.plotly_chart(fig_co2, use_container_width=True)

# --------------------------------------------------------------------------- #
# TAB 2: Alert log + detection-latency comparison
# --------------------------------------------------------------------------- #

with tab_alerts:
    st.markdown("### Threshold-Breach Events")
    alert_df = df[df["temp_alert"]][["hour", "timestamp", "temperature_c", "lat", "lon"]]
    if alert_df.empty:
        st.success("No threshold breaches in this run. Try lowering the threshold or changing the seed.")
    else:
        st.dataframe(alert_df, use_container_width=True, hide_index=True)

        st.markdown("### Real-Time vs. Checkpoint-Based Detection")
        colA, colB, colC = st.columns(3)
        colA.metric("Real-time detection", f"hour {latency['real_time_hour']}")
        colB.metric("Checkpoint detection", f"hour {latency['checkpoint_hour']}")
        colC.metric("Latency saved", f"{latency['latency_hours']} h", delta="faster with real-time data")
       

# --------------------------------------------------------------------------- #
# TAB 3: Transparency scorecard (the project's critical-analysis outcome)
# --------------------------------------------------------------------------- #

with tab_analysis:
    st.markdown("## Does Real-Time Data Actually Improve Transparency?")
    st.write(
        "Detection speed is only part of the answer. This scorecard rates the "
        "**dashboard you are using right now** against three properties that "
        "together determine whether real-time data amounts to genuine transparency."
    )

    scorecard = [
        ("Visibility", "High", "#3A11D0",
         "Temperature, emissions, and location are captured every 5 minutes for the full shipment."),
        ("Accessibility", "Low", "#2B2223",
         "This dashboard is operator-facing only — no customer, auditor, or regulator view exists yet."),
        ("Verifiability", "Low", "#2B2223",
         "Readings are stored as plain CSV/JSON with no tamper-evidence (e.g. hashing) applied."),
    ]
    cols = st.columns(3)
    for col, (name, score, color, just) in zip(cols, scorecard):
        with col:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div style="color:{MUTED};font-size:0.85rem;letter-spacing:1px;"></div>
                    <div style="font-size:1.4rem;font-weight:700;color:{NAVY};">{name}</div>
                    <div style="display:inline-block;margin-top:0.4rem;padding:0.2rem 0.7rem;
                                border-radius:999px;background:{color};color:WHITE;font-weight:600;">
                        {score}
                    </div>
                    <p style="margin-top:0.8rem;color:#1B2733;font-size:0.9rem;">{just}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("---")
    st.markdown(
        f"""
        <div style="background:{NAVY};color:white;padding:1.2rem 1.5rem;border-radius:10px;">
        <b>Key finding:</b> Real-time data doesn't create transparency by itself — it creates the
        <i>possibility</i> of transparency. This tool demonstrates the gap directly: high Visibility,
        unresolved Accessibility and Verifiability. A {latency['latency_hours'] or '—'}-hour faster
        detection is real and valuable, but it is not the same claim as "this supply chain is transparent."
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Recommendations Suggested by the Critical-Analysis Report")
    st.markdown(
        "- **Accessibility** — add a scoped, read-only dashboard view for customers/auditors.\n"
        "- **Verifiability** — hash-chain each logged reading so tampering becomes detectable.\n"
        "- **Governance** — define in writing who can see what data, and for how long."
    )
