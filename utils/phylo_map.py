import folium

def generate_folium_map(latitude=40.650002, longitude=-73.949997, zoom=6, markers=[]):
    """Generates a Folium map with optional markers."""
    m = folium.Map(location=[latitude, longitude], zoom_start=zoom, tiles="OpenStreetMap")

    for marker in markers:
        folium.CircleMarker(
            location=[marker["lat"], marker["lon"]],
            popup=marker["name"],
            color="black",
            fill_opacity=0.6,
            fill_color="green",
        ).add_to(m)

    return m._repr_html_()
