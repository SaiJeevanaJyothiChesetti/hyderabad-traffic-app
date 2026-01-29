import streamlit as st
import pandas as pd
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium

# ---------------------------------
# PAGE CONFIG
# ---------------------------------
st.set_page_config(
    page_title="Hyderabad Traffic Monitor",
    layout="wide"
)

st.title("🚦 Hyderabad Traffic Heatmap")

# ---------------------------------
# LOAD DATA (CACHED)
# ---------------------------------
@st.cache_data
def load_data():
    return pd.read_csv("hyderabad_traffic.csv")

traffic_df = load_data()

# ---------------------------------
# SIDEBAR
# ---------------------------------
st.sidebar.header("🛣️ Road Selection")

selected_road = st.sidebar.selectbox(
    "Select Road / Street",
    ["All Roads"] + sorted(traffic_df["road_name"].unique())
)

# Manual refresh button (NO experimental_rerun)
if st.sidebar.button("🔄 Refresh Traffic Data"):
    st.cache_data.clear()
    st.rerun()

# ---------------------------------
# FILTER DATA
# ---------------------------------
if selected_road == "All Roads":
    filtered_df = traffic_df
else:
    filtered_df = traffic_df[traffic_df["road_name"] == selected_road]

# ---------------------------------
# SUMMARY METRICS
# ---------------------------------
st.subheader("📊 Traffic Summary")

col1, col2, col3 = st.columns(3)

col1.metric(
    "🚗 Avg Speed (km/h)",
    round(filtered_df["avg_speed_kmh"].mean(), 1)
)

col2.metric(
    "🚦 Congestion",
    filtered_df["congestion_level"].iloc[0]
)

col3.metric(
    "⚠️ Incident",
    filtered_df["incident_type"].iloc[0]
)

# ---------------------------------
# MAP CENTER
# ---------------------------------
if selected_road == "All Roads":
    center = [17.3850, 78.4867]  # Hyderabad
    zoom = 12
else:
    center = [
        filtered_df.iloc[0]["latitude"],
        filtered_df.iloc[0]["longitude"]
    ]
    zoom = 15

# ---------------------------------
# MAP
# ---------------------------------
m = folium.Map(
    location=center,
    zoom_start=zoom,
    tiles="cartodbpositron"
)

# ---------------------------------
# HEATMAP
# ---------------------------------
heat_data = [
    [row["latitude"], row["longitude"], 1]
    for _, row in filtered_df.iterrows()
]

HeatMap(
    heat_data,
    radius=25,
    blur=15,
    min_opacity=0.4
).add_to(m)

# ---------------------------------
# MARKERS
# ---------------------------------
color_map = {
    "Free": "green",
    "Moderate": "orange",
    "Heavy": "red",
    "Very Heavy": "darkred"
}

for _, row in filtered_df.iterrows():
    folium.CircleMarker(
        location=[row["latitude"], row["longitude"]],
        radius=8,
        color=color_map[row["congestion_level"]],
        fill=True,
        fill_opacity=0.9,
        popup=f"""
        <b>{row['road_name']}</b><br>
        Speed: {row['avg_speed_kmh']} km/h<br>
        Congestion: {row['congestion_level']}<br>
        Incident: {row['incident_type']}
        """
    ).add_to(m)

# ---------------------------------
# DISPLAY MAP
# ---------------------------------
st.subheader("🗺️ Live Traffic Map")
st_folium(m, height=550, width=1200)

# ---------------------------------
# DATA TABLE
# ---------------------------------
with st.expander("📄 View Traffic Data"):
    st.dataframe(filtered_df)
