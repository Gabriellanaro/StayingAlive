import pandas as pd
import folium
from folium.plugins import HeatMap

# Load restaurant dataset with coordinates
restaurants_df = pd.read_csv("scraped_companies_combined_clean_with_coords.csv")
restaurants_df = restaurants_df.dropna(subset=['latitude', 'longitude'])

# Load pedestrian traffic dataset with coordinates
traffic_df = pd.read_csv("foot_trafic.csv")
traffic_df = traffic_df.dropna(subset=['lat', 'lon'])

# Preprocessing longevity
restaurants_df['startdate'] = pd.to_datetime(restaurants_df['startdate'], errors='coerce')
restaurants_df['enddate'] = pd.to_datetime(restaurants_df['enddate'], errors='coerce')
restaurants_df['enddate_filled'] = restaurants_df['enddate'].fillna(pd.Timestamp.today())
restaurants_df['longevity_days'] = (restaurants_df['enddate_filled'] - restaurants_df['startdate']).dt.days

# Initialize the map centered on Copenhagen
map_ = folium.Map(location=[55.6761, 12.5683], zoom_start=13)

# --- HEATMAP: Restaurants ---
heat_points = restaurants_df[['latitude', 'longitude']].values.tolist()
heatmap_layer = folium.FeatureGroup(name="Restaurants Heatmap")
HeatMap(heat_points, radius=10, blur=15).add_to(heatmap_layer)
heatmap_layer.add_to(map_)

# --- HEATMAP: Longevity ---
longevity_points = restaurants_df[['latitude', 'longitude', 'longevity_days']].dropna().values.tolist()
longevity_layer = folium.FeatureGroup(name="Restaurants Longevity Heatmap", show=False)
HeatMap(longevity_points, radius=15, blur=25, max_zoom=14).add_to(longevity_layer)
longevity_layer.add_to(map_)

# --- MARKERS: Active / Closed Restaurants ---
active_layer = folium.FeatureGroup(name="Active Restaurants", show=False)
closed_layer = folium.FeatureGroup(name="Closed Restaurants", show=False)

for _, row in restaurants_df.iterrows():
    popup = folium.Popup(
        f"<b>{row.get('name', 'N/A')}</b><br>"
        f"Business Code: {row.get('branchekode', 'N/A')}<br>"
        f"Status: {row.get('status', 'N/A')}<br>"
        f"Opening Date: {row.get('startdate', 'N/A')}<br>"
        f"Postal Code: {row.get('zip', 'N/A')}",
        max_width=300
    )
    marker = folium.Marker(
        location=[row['latitude'], row['longitude']],
        popup=popup,
        icon=folium.Icon(color="green" if row.get('active', False) else "red")
    )
    if row.get('active', False):
        marker.add_to(active_layer)
    else:
        marker.add_to(closed_layer)

active_layer.add_to(map_)
closed_layer.add_to(map_)

# --- FILTER: Branchekode ---
branche_layer_dict = {}
for branche in restaurants_df['branchekode'].dropna().unique():
    layer = folium.FeatureGroup(name=f"Branchekode: {branche}", show=False)
    for _, row in restaurants_df[restaurants_df['branchekode'] == branche].iterrows():
        popup = folium.Popup(
            f"<b>{row.get('name', 'N/A')}</b><br>"
            f"Branchekode: {row.get('branchekode', 'N/A')}<br>"
            f"Status: {row.get('status', 'N/A')}<br>"
            f"Startdate: {row.get('startdate', 'N/A')}<br>"
            f"ZIP: {row.get('zip', 'N/A')}",
            max_width=300
        )
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=4,
            color="blue",
            fill=True,
            fill_opacity=0.6,
            popup=popup
        ).add_to(layer)
    layer.add_to(map_)

# --- PEDESTRIAN TRAFFIC: HEATMAP aadt_fod_7_19 ---
heat_traffic_points = traffic_df[['lat', 'lon', 'aadt_fod_7_19']].dropna().values.tolist()
heatmap_ped_layer = folium.FeatureGroup(name="Pedestrian Heatmap (7-19)")
HeatMap(heat_traffic_points, radius=15, blur=25, max_zoom=14).add_to(heatmap_ped_layer)
heatmap_ped_layer.add_to(map_)

# --- PEDESTRIAN TRAFFIC: CIRCLE LAYER hvdt_fod_7_19 ---
circle_layer = folium.FeatureGroup(name="Pedestrian Peak Hour 7-19", show=False)
for _, row in traffic_df.iterrows():
    value = row.get('hvdt_fod_7_19')
    if pd.notna(value):
        radius = value / 500  # scaling factor
        popup = folium.Popup(
            f"<b>{row.get('vejnavn', '')}</b><br>"
            f"Peak Hour 7-19: {int(value)}<br>"
            f"Description: {row.get('beskrivelse', '')}<br>"
            f"Date: {row.get('taelle_dato', '')}",
            max_width=300
        )
        folium.CircleMarker(
            location=[row['lat'], row['lon']],
            radius=radius,
            color="red",
            fill=True,
            fill_opacity=0.5,
            popup=popup
        ).add_to(circle_layer)
circle_layer.add_to(map_)

# Add layer control to enable toggling layers
folium.LayerControl(collapsed=False).add_to(map_)

# Save the final map
map_.save("interactive_map_with_filtered_traffic.html")
