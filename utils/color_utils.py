import plotly.express as px

def generate_location_colors(locations, palette='Plotly', custom_colors=None):
    """Generates a color map for unique locations, allowing custom palettes."""
    unique_locations = locations.unique()

    # ✅ Ensure palette is a string, not a list
    if isinstance(palette, list):  
        palette = 'Plotly'  # Default to Plotly if a list is given

    if hasattr(px.colors.qualitative, palette):
        colors = getattr(px.colors.qualitative, palette)
    else:
        colors = px.colors.qualitative.Plotly  # Fallback to default colors

    color_map = {loc: custom_colors.get(loc, colors[i % len(colors)]) if custom_colors else colors[i % len(colors)]
                 for i, loc in enumerate(unique_locations)}

    return color_map



def generate_mlst_colors(mlst_values, palette='Bold', custom_colors=None):
    """Generates a color map for unique MLST values using selected palette."""
    unique_mlst = mlst_values.unique()

    # ✅ Ensure palette is a string, not a list
    if isinstance(palette, list):  
        palette = 'Plotly'  # Default to Plotly if a list is given

    if hasattr(px.colors.qualitative, palette):
        colors = getattr(px.colors.qualitative, palette)
    else:
        colors = px.colors.qualitative.Plotly  # Fallback to Plotly default

    color_map = {mlst: custom_colors.get(mlst, colors[i % len(colors)]) if custom_colors else colors[i % len(colors)]
                 for i, mlst in enumerate(unique_mlst)}

    return color_map

def generate_heatmap_colors(values, palette='Plotly'):
    """Generate a color mapping for unique values in a dataset."""
    unique_values = values.unique()
    
    if hasattr(px.colors.qualitative, palette):
        colors = getattr(px.colors.qualitative, palette)
    else:
        colors = px.colors.qualitative.Plotly  # Default
    
    color_map = {val: colors[i % len(colors)] for i, val in enumerate(unique_values)}
    return color_map



