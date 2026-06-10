import streamlit as st
import json
import pandas as pd
import folium
from streamlit_folium import st_folium

# Set page configuration
st.set_page_config(page_title="HIDOT Asset Prioritization Tool", layout="wide")

st.title("🛣️ HIDOT & Blyncsy Maintenance Prioritization Dashboard")
st.markdown("Upload roadway detection layers and apply agency constraints to find high-priority repairs.")

# --- SIDEBAR: USER INPUTS & DROPDOWNS ---
st.sidebar.header("📋 Agency Control Panel")

# 1. File Uploader
uploaded_file = st.sidebar.file_uploader("Upload Blyncsy GeoJSON", type=["geojson"])

# 2. Dropdowns and Sliders for Traffic/Engineering Inputs
target_severity = st.sidebar.multiselect(
    "Select Damage Severities to Target:",
    options=["High-Medium", "Low"],
    default=["High-Medium", "Low"]
)

min_aadt = st.sidebar.slider(
    "Minimum AADT (Traffic Volume):",
    min_value=500,
    max_value=10000,
    value=1000,
    step=500
)

st.sidebar.markdown("---")
st.sidebar.info(
    "**Prioritization Formula:**\n"
    "Priority Score = (Severity Weight × 0.7) + ((AADT / 1000) × 0.3)"
)

# --- CORE LOGIC & PROCESSING ---
if uploaded_file is not None:
    # Read the uploaded GeoJSON file
    geojson_data = json.load(uploaded_file)
    features = geojson_data.get("features", [])
    
    processed_records = []
    
    # Process rows dynamically based on the exact structure provided
    for feature in features:
        props = feature.get("properties", {})
        coords = feature.get("geometry", {}).get("coordinates", [0, 0])
        
        # Parse Blyncsy comma-separated damage labels 
        raw_labels = props.get("labels", "unknown")
        damage_list = [label.strip() for label in raw_labels.split(",")]
        
        # Assign structural severity classification
        if any("high" in d for d in damage_list) or any("medium" in d for d in damage_list):
            severity = "High-Medium"
        else:
            severity = "Low"
            
        record_id = props.get("id", "Unknown ID")
        
        # Simulating your random/agency AADT allocation (e.g., swapping between 1000, 2000, 5000)
        # In production, this replaces with an exact route/segment lookup
        index_num = props.get("index", 0)
        if index_num % 3 == 0:
            aadt = 5000
        elif index_num % 2 == 0:
            aadt = 2000
        else:
            aadt = 1000
            
        processed_records.append({
            "Blyncsy Index": index_num,
            "Timestamp": props.get("localTime"),
            "Severity": severity,
            "Detections": raw_labels,
            "Longitude": coords[0],
            "Latitude": coords[1],
            "Image Link": props.get("img_link"),
            "AADT": aadt
        })
        
    df = pd.DataFrame(processed_records)
    
    # Apply User UI Filters
    df = df[df["Severity"].isin(target_severity)]
    df = df[df["AADT"] >= min_aadt]
    
    # Calculate Priority Scores dynamically based on user selections
    severity_weights = {"High-Medium": 5.0, "Low": 1.5}
    df["Priority Score"] = df.apply(
        lambda row: round((severity_weights.get(row["Severity"], 1.0) * 0.7) + ((row["AADT"] / 1000) * 0.3), 2), 
        axis=1
    )
    
    # Sort results with highest priority at top
    df = df.sort_values(by="Priority Score", ascending=False).reset_index(drop=True)
    
    # --- UI LAYOUT: MAP & METRICS ---
    col1, col2 = st.columns([1.2, 1])
    
    with col1:
        st.subheader("🗺️ Spatial Priority Heatmap")
        if not df.empty:
            # Center the map around Hawaii coordinates from your dataset
            m = folium.Map(location=[df["Latitude"].mean(), df["Longitude"].mean()], zoom_start=10)
            
            # Map out each filtered asset point
            for _, row in df.head(50).iterrows(): # Limit to top 50 pins for performance
                color = "red" if row["Severity"] == "High-Medium" else "blue"
                popup_text = f"""
                    <b>Priority Score: {row["Priority Score"]}</b><br>
                    Index: {row["Blyncsy Index"]}<br> 
                    Damage: {row["Detections"]}<br> 
                    AADT: {row["AADT"]}<br>
                    <a href='{row["Image Link"]}' target='_blank'>View Field Photo</a> 
                """
                folium.CircleMarker(
                    location=[row["Latitude"], row["Longitude"]],
                    radius=7,
                    color=color,
                    fill=True,
                    fill_color=color,
                    fill_opacity=0.7,
                    popup=folium.Popup(popup_text, max_width=300)
                ).add_to(m)
                
            st_folium(m, width=700, height=500, returned_objects=[])
        else:
            st.warning("No data matches your active filter criteria.")
            
    with col2:
        st.subheader("📊 Top Actionable Operations Manifest")
        # Display prioritized queue table to the user
        display_cols = ["Priority Score", "Blyncsy Index", "Severity", "AADT", "Detections"]
        st.dataframe(
            df[display_cols].style.background_gradient(subset=["Priority Score"], cmap="YlOrRd"),
            height=450,
            use_container_width=True
        )
        
        # Allow instant export to CSV for fieldwork crews
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Export prioritized queue to CSV / Excel",
            data=csv,
            file_name="hidot_prioritized_maintenance.csv",
            mime="text/csv",
        )

else:
    # Initial state when application loads without a file drop
    st.info("💡 Please upload your `hidot_guardrail_...combined.geojson` file in the sidebar to begin processing.")