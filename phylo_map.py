import folium
import json

def generate_folium_map(geojson_data=None, latitude=30, longitude=-80, zoom=6):
    """Generates a Folium map using an uploaded GeoJSON or a manual city location."""
    
    attr = ('&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> '
            'contributors, &copy; <a href="http://cartodb.com/attributions">CartoDB</a>')
    tiles = 'https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}{r}.png'

    # Create map centered on the user-defined or city location
    m = folium.Map(location=[latitude, longitude], zoom_start=zoom, tiles="OpenStreetMap", attr=attr)

    # ✅ If GeoJSON data exists, add it to the map
    if geojson_data:
        folium.GeoJson(geojson_data, style_function=lambda x: {
            'color': '#58bbff', 'fillColor': '#58bbff', 'fillOpacity': 0.25
        }).add_to(m)

    # 📍 Add a marker at the selected location
    folium.Marker(
        location=[latitude, longitude],
        popup="Selected Location",
        icon=folium.Icon(color="blue", icon="info-sign"),
    ).add_to(m)

    return m._repr_html_()  # Return HTML string for embedding in Dash
