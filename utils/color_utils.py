import plotly.express as px

def generate_location_colors(locations):
    """Generates a color map for unique locations."""
    unique_locations = locations.unique()
    colors = px.colors.qualitative.Plotly
    color_map = {loc: colors[i % len(colors)] for i, loc in enumerate(unique_locations)}
    return color_map
