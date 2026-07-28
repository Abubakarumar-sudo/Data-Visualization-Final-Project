
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="IoT Supply Chain Monitoring | Final Project", layout="wide", page_icon="📦")

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed"

NAVY = "#0B3D5C"
TEAL = "#1C7293"
AMBER = "#F2A541"
GREY = "#7A8793"
RED = "#B23A48"
GREEN = "#2A9D8F"

st.markdown(f"""
<style>
.stApp {{ background-color: #F7FAFC; }}
.main-title {{ color: {NAVY}; font-weight: 800; }}
.small-note {{ color: #637381; font-size: 0.9rem; }}
div[data-testid="stMetricValue"] {{ color: {NAVY}; }}
</style>
""", unsafe_allow_html=True)

@st.cache_data(show_spinner=False)
def load_data():
    shipments = pd.read_csv(DATA / "clean_supply_chain_prototype.csv", parse_dates=["timestamp"])
    summary = pd.read_csv(DATA / "shipment_summary_prototype.csv", parse_dates=["start_time", "end_time"])
    batch = pd.read_csv(DATA / "batch_results.csv")
    return shipments, summary, batch

shipments, summary, batch = load_data()

st.markdown('<h1 class="main-title">IoT-Enabled Supply Chain Monitoring</h1>', unsafe_allow_html=True)
st.caption("Prototype dashboard for cold-chain risk detection, shipment transparency, and emissions visibility.")
st.warning("Dataset provenance: the uploaded shipment sensor readings are a simulated prototype. The final assessed notebook should integrate a verified real-world dataset, with this dashboard retained as an interactive proof-of-concept.")

with st.sidebar:
    st.header("Filters")
    shipment_options = sorted(shipments["shipment_id"].unique())
    selected_shipments = st.multiselect("Shipment ID", shipment_options, default=shipment_options)
    threshold_options = sorted(shipments["temp_threshold_c"].unique())
    selected_thresholds = st.multiselect("Threshold (°C)", threshold_options, default=threshold_options)
    show_alerts_only = st.checkbox("Show alert readings only", value=False)
    st.markdown("---")
    st.markdown("### Research Question")
    st.info("How much earlier can real-time IoT monitoring reveal supply-chain temperature risk compared with checkpoint monitoring?")

filtered = shipments[
    shipments["shipment_id"].isin(selected_shipments)
    & shipments["temp_threshold_c"].isin(selected_thresholds)
].copy()
if show_alerts_only:
    filtered = filtered[filtered["temp_alert"]]
filtered_summary = summary[summary["shipment_id"].isin(selected_shipments)]

if filtered.empty:
    st.error("No records match the selected filters.")
    st.stop()

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Executive Overview", "Journey & Sensors", "Alerts & Risk", "Detection Speed", "Data Provenance"])

with tab1:
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Shipments", filtered["shipment_id"].nunique())
    c2.metric("Sensor readings", f"{len(filtered):,}")
    c3.metric("Alert readings", f"{int(filtered['temp_alert'].sum()):,}")
    c4.metric("Avg max temp", f"{filtered_summary['max_temperature_c'].mean():.1f} °C")
    c5.metric("Avg latency saved", f"{batch['latency_hours'].mean():.2f} h")

    left, right = st.columns([1.4, 1])
    with left:
        st.subheader("Temperature exposure by journey progress")
        fig = px.line(filtered, x="journey_progress_pct", y="temperature_c", color="shipment_id",
                      labels={"journey_progress_pct":"Journey progress (%)", "temperature_c":"Temperature (°C)", "shipment_id":"Shipment"})
        fig.add_hline(y=filtered["temp_threshold_c"].median(), line_dash="dash", line_color=RED,
                      annotation_text="Median threshold", annotation_position="top left")
        fig.update_layout(template="plotly_white", height=430, legend_title_text="Shipment")
        st.plotly_chart(fig, use_container_width=True)
    with right:
        st.subheader("Shipment summary")
        display_cols = ["shipment_id","threshold_c","total_distance_km","total_co2_kg","max_temperature_c","alert_readings","alert_duration_hours"]
        st.dataframe(filtered_summary[display_cols].round(2), use_container_width=True, hide_index=True)

with tab2:
    st.subheader("Route map and current simulated positions")
    fig_map = px.line_map(filtered.sort_values(["shipment_id","step"]), lat="lat", lon="lon", color="shipment_id",
                          hover_data=["shipment_id","hour","temperature_c","temp_alert"], zoom=5, height=500)
    latest = filtered.sort_values("step").groupby("shipment_id").tail(1)
    fig_map.add_scattermapbox(lat=latest["lat"], lon=latest["lon"], mode="markers", marker={"size":15,"color":AMBER}, name="latest")
    fig_map.update_layout(mapbox_style="carto-positron", margin={"l":0,"r":0,"t":0,"b":0})
    st.plotly_chart(fig_map, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Cumulative CO₂ over transit")
        fig = px.line(filtered, x="hour", y="cumulative_co2_kg", color="shipment_id",
                      labels={"hour":"Transit hour", "cumulative_co2_kg":"Cumulative CO₂ (kg)"})
        fig.update_layout(template="plotly_white", height=380)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.subheader("Interval emissions distribution")
        fig = px.box(filtered, x="shipment_id", y="interval_co2_kg", color="shipment_id",
                     labels={"shipment_id":"Shipment", "interval_co2_kg":"Interval CO₂ (kg)"})
        fig.update_layout(template="plotly_white", height=380, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("Where alerts concentrate")
    stage_alerts = filtered.groupby(["shipment_id","journey_stage"], observed=False)["alert"].sum().reset_index()
    fig = px.bar(stage_alerts, x="journey_stage", y="alert", color="shipment_id", barmode="group",
                 labels={"journey_stage":"Journey stage", "alert":"Alert readings"})
    fig.update_layout(template="plotly_white", height=420)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("High-risk readings")
    st.dataframe(filtered[filtered["temp_alert"]][["shipment_id","timestamp","hour","lat","lon","temperature_c","temp_threshold_c","temperature_difference_c","distance_km"]].round(3), use_container_width=True, hide_index=True)

with tab4:
    st.subheader("Real-time monitoring detects alerts before checkpoints")
    c1, c2, c3 = st.columns(3)
    c1.metric("Runs", len(batch))
    c2.metric("Alert occurred", f"{batch['alert_occurred'].mean()*100:.0f}%")
    c3.metric("Mean hours saved", f"{batch['latency_hours'].mean():.2f} h")

    fig = go.Figure()
    fig.add_trace(go.Box(y=batch["real_time_hour"], name="Real-time detection", marker_color=TEAL))
    fig.add_trace(go.Box(y=batch["checkpoint_hour"], name="Checkpoint detection", marker_color=AMBER))
    fig.update_layout(template="plotly_white", yaxis_title="Detection hour", height=430)
    st.plotly_chart(fig, use_container_width=True)

    fig2 = px.histogram(batch, x="latency_hours", nbins=8, labels={"latency_hours":"Hours saved"})
    fig2.update_layout(template="plotly_white", height=330)
    st.plotly_chart(fig2, use_container_width=True)

with tab5:
    st.subheader("Dataset provenance and project integrity")
    st.markdown("""
    **Current uploaded data:** simulated IoT shipment prototype readings.  
    **Final project requirement:** replace or supplement this with a credible real-world logistics or sensor dataset.  
    **Recommended real-world source:** UCI Daily Demand Forecasting Orders, which UCI describes as 60 days of real data from a large Brazilian logistics company.

    Use this dashboard as the proof-of-concept layer, and use the notebook to clearly separate real-world evidence from simulated scenario analysis.
    """)
    st.code("python src/prepare_data.py", language="bash")
    st.dataframe(shipments.head(20), use_container_width=True, hide_index=True)
