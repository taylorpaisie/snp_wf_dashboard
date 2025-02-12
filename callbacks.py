import base64
import io
import json
import re
import ssl
import certifi
import os
import requests
import urllib3
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from io import StringIO
from dash import Input, Output, State, dcc, html, dash_table
from dash.exceptions import PreventUpdate
import dash_bio as dashbio
from dash import ctx
import phylo_map
from Bio import Phylo, SeqIO
from dotenv import load_dotenv  

# Geopy (for geocoding city names)
import geopy.geocoders
from geopy.geocoders import Nominatim

# ✅ Force Python to use certifi's certificates
os.environ['SSL_CERT_FILE'] = certifi.where()
os.environ['SSL_CERT_DIR'] = certifi.where()

# ✅ Create an SSL context that explicitly uses certifi
ssl_context = ssl.create_default_context(cafile=certifi.where())

# ✅ Configure urllib3 to use the correct SSL certificates
http = urllib3.PoolManager(cert_reqs="CERT_REQUIRED", ca_certs=certifi.where())

# ✅ Suppress SSL warnings (prevents flooding logs with SSL errors)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()
print(f"Loaded API Key: {os.getenv('OPENCAGE_API_KEY')}")

# Store Markers in Memory
MARKERS = []

def get_city_coordinates(city_name):
    """Fetch city coordinates using OpenCage API."""
    api_key = os.getenv("OPENCAGE_API_KEY")  # Load from environment variable
    if not api_key:
        return None, None, "⚠️ Missing OpenCage API Key."

    base_url = "https://api.opencagedata.com/geocode/v1/json"
    params = {"q": city_name, "key": api_key, "limit": 1}

    try:
        response = requests.get(base_url, params=params, verify=False, timeout=10)  # ✅ Disable SSL verification
        response.raise_for_status()

        data = response.json()
        if not data["results"]:
            return None, None, "⚠️ City not found. Please enter a valid city name."

        lat = data["results"][0]["geometry"]["lat"]
        lon = data["results"][0]["geometry"]["lng"]
        return float(lat), float(lon), None  # ✅ Success

    except requests.exceptions.RequestException as e:
        return None, None, f"⚠️ Error fetching city coordinates: {str(e)}"



def get_rectangular_coordinates(tree):
    xcoords = tree.depths(unit_branch_lengths=True)
    ycoords = {}

    def calc_y_coordinates(clade, current_y):
        if clade.is_terminal():
            ycoords[clade] = current_y
            return current_y + 1

        for subclade in clade:
            current_y = calc_y_coordinates(subclade, current_y)

        ycoords[clade] = (ycoords[clade.clades[0]] + ycoords[clade.clades[-1]]) / 2
        return current_y

    calc_y_coordinates(tree.root, 0)
    return xcoords, ycoords

def draw_clade_rectangular(clade, x_start, line_shapes, x_coords, y_coords):
    x_end = x_coords[clade]
    y_current = y_coords[clade]

    # Draw horizontal line for the branch
    line_shapes.append(dict(
        type='line',
        x0=x_start, y0=y_current, x1=x_end, y1=y_current,
        line=dict(color='black', width=1)
    ))

    # Draw vertical connecting lines for children
    if clade.clades:
        y_top = y_coords[clade.clades[0]]
        y_bottom = y_coords[clade.clades[-1]]
        line_shapes.append(dict(
            type='line',
            x0=x_end, y0=y_bottom, x1=x_end, y1=y_top,
            line=dict(color='black', width=1)
        ))

        for subclade in clade:
            draw_clade_rectangular(subclade, x_end, line_shapes, x_coords, y_coords)

def create_tree_plot(tree_file, metadata_file, show_tip_labels):
    from plotly.colors import qualitative

    # Load tree and metadata
    tree = Phylo.read(tree_file, 'newick')
    metadata = pd.read_csv(metadata_file, sep='\t')
    metadata['location'] = metadata['location'].fillna('Unknown')  # Handle missing locations

    # Map metadata to colors
    location_colors = {
        loc: qualitative.Plotly[i % len(qualitative.Plotly)]
        for i, loc in enumerate(metadata['location'].unique())
    }

    # Generate x and y coordinates
    x_coords = {}
    y_coords = {}
    max_y = 0

    def assign_coordinates(clade, x_start=0, y_start=0):
        nonlocal max_y
        branch_length = clade.branch_length if clade.branch_length else 0.001
        if clade.is_terminal():
            x_coords[clade] = x_start + branch_length
            y_coords[clade] = y_start
            max_y = max(max_y, y_start)
            return y_start + 1
        else:
            y_positions = []
            for child in clade.clades:
                y_start = assign_coordinates(child, x_start + branch_length, y_start)
                y_positions.append(y_start - 1)
            x_coords[clade] = x_start + branch_length
            y_coords[clade] = sum(y_positions) / len(y_positions)
            return y_start

    assign_coordinates(tree.root)

    # Create line shapes for branches
    line_shapes = []
    for clade in tree.find_clades(order='level'):
        x_start = x_coords[clade]
        y_start = y_coords[clade]
        if clade.clades:
            y_positions = [y_coords[child] for child in clade.clades]
            line_shapes.append(dict(
                type='line',
                x0=x_start, y0=min(y_positions),
                x1=x_start, y1=max(y_positions),
                line=dict(color='black', width=1)
            ))
            for child in clade.clades:
                x_end = x_coords[child]
                y_end = y_coords[child]
                line_shapes.append(dict(
                    type='line',
                    x0=x_start, y0=y_end,
                    x1=x_end, y1=y_end,
                    line=dict(color='black', width=1)
                ))

    # Create scatter points for tips
    tip_markers = []
    seen_locations = set()
    for clade in tree.get_terminals():
        x = x_coords[clade]
        y = y_coords[clade]
        if clade.name in metadata['taxa'].values:
            meta_row = metadata[metadata['taxa'] == clade.name].iloc[0]
            location = meta_row['location']
            color = location_colors.get(location, 'gray')

            show_legend = location not in seen_locations
            if show_legend:
                seen_locations.add(location)

            tip_markers.append(go.Scatter(
                x=[x],
                y=[y],
                mode='markers+text' if show_tip_labels else 'markers',
                marker=dict(size=10, color=color, line=dict(width=1, color='black')),
                name=location if show_legend else None,
                text=f"<b>{clade.name}</b><br>Location: {location}" if show_tip_labels else "",
                textposition="middle right",
                hoverinfo='text',
                showlegend=show_legend
            ))

    layout = go.Layout(
        title='Phylogenetic Tree with Tip Label Toggle',
        xaxis=dict(title='Evolutionary Distance', showgrid=True, zeroline=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-1, max_y + 1]),
        shapes=line_shapes,
        height=800,
        legend=dict(title="Locations", orientation="h", y=-0.2),
    )

    return go.Figure(data=tip_markers, layout=layout)

def register_callbacks(app):
    # Callback for MSA display
    @app.callback(
        Output('output-alignment-chart', 'children'),
        [Input('upload-fasta', 'contents'),
         Input('alignment-colorscale', 'value')],
        [State('upload-fasta', 'filename')]
    )
    def display_msa(file_contents, colorscale, file_name):
        if file_contents:
            try:
                # Decode the uploaded FASTA file
                content_type, content_string = file_contents.split(',')
                decoded = base64.b64decode(content_string).decode('utf-8')
                print("Decoded FASTA content:", decoded)  # Debugging output

                if file_name.endswith('.fasta'):
                    # Render the AlignmentChart
                    return dashbio.AlignmentChart(
                        id='alignment-viewer',
                        data=decoded,
                        colorscale=colorscale if colorscale else 'nucleotide',
                        tilewidth=20
                    )
                else:
                    return html.Div("Uploaded file is not a valid FASTA file.", className="text-danger")
            except Exception as e:
                print("Error processing FASTA file:", str(e))  # Debugging output
                return html.Div(f"An error occurred: {str(e)}", className="text-danger")

        return html.Div("No FASTA file uploaded yet.", className="text-warning")


    # Callback for Phylogenetic Tree Visualization
    @app.callback(
        Output('tree-graph-container', 'children'),
        [Input('upload-tree', 'contents'),
         Input('upload-metadata', 'contents'),
         Input('show-tip-labels', 'value')],
        [State('upload-tree', 'filename'),
         State('upload-metadata', 'filename')]
    )
    def update_tree(tree_contents, metadata_contents, show_labels, tree_filename, metadata_filename):
        if tree_contents and metadata_contents:
            try:
                # Decode tree and metadata files
                tree_data = base64.b64decode(tree_contents.split(",", 1)[1]).decode("utf-8")
                metadata_data = base64.b64decode(metadata_contents.split(",", 1)[1]).decode("utf-8")
                tree_file = "uploaded_tree.tree"
                metadata_file = "uploaded_metadata.tsv"

                with open(tree_file, "w") as f:
                    f.write(tree_data)

                with open(metadata_file, "w") as f:
                    f.write(metadata_data)

                # Determine if tip labels should be shown
                show_tip_labels = 'SHOW' in show_labels

                # Generate the tree plot with `create_tree_plot`
                fig = create_tree_plot(tree_file, metadata_file, show_tip_labels)
                return dcc.Graph(figure=fig)

            except Exception as e:
                return html.Div(f"Error processing tree file: {str(e)}", className="text-danger")
        return html.Div("Please upload both a tree file and a metadata file.", className="text-warning")

    # Callback for Folium Map Display

    @app.callback(
        Output('phylo-map-container', 'children'),
        [Input('upload-geojson', 'contents'),
        Input('map-city', 'value'),  # Added city name input
        Input('map-lat', 'value'),
        Input('map-lon', 'value'),
        Input('map-zoom', 'value'),
        Input('add-marker-btn', 'n_clicks')],
        [State('marker-name', 'value'),
        State('marker-lat', 'value'),
        State('marker-lon', 'value')]
    )
    def update_folium_map(geojson_contents, city_name, latitude, longitude, zoom, n_clicks, marker_name, marker_lat, marker_lon):
        global MARKERS  # Use global storage for markers

        # ✅ 1. Convert city name to coordinates if provided
        if city_name:
            geocoded_lat, geocoded_lon, error_msg = get_city_coordinates(city_name)
            if geocoded_lat and geocoded_lon:
                latitude, longitude = geocoded_lat, geocoded_lon
            else:
                return html.Div(f"⚠️ Error: {error_msg}", className="text-danger")

        # ✅ 2. Decode GeoJSON if uploaded
        geojson_data = None
        if geojson_contents:
            content_type, content_string = geojson_contents.split(',')
            decoded = base64.b64decode(content_string).decode('utf-8')
            geojson_data = json.loads(decoded)

        # ✅ 3. Add new marker if button clicked
        if ctx.triggered_id == "add-marker-btn" and marker_name and marker_lat and marker_lon:
            MARKERS.append({"name": marker_name, "lat": float(marker_lat), "lon": float(marker_lon)})

        # ✅ 4. Generate updated Folium map
        folium_map_html = phylo_map.generate_folium_map(geojson_data, latitude, longitude, zoom, MARKERS)

        return html.Iframe(
            srcDoc=folium_map_html,
            width="100%",
            height="1000px",
            style={"border": "none"}
        )

    #standalone map tab
    @app.callback(
        Output('standalone-map-container', 'children'),
        [Input('upload-standalone-geojson', 'contents'),
        Input('search-standalone-city-btn', 'n_clicks'),
        Input('standalone-map-zoom', 'value')],  # ✅ New Zoom Input
        [State('upload-standalone-geojson', 'filename'),
        State('search-standalone-city', 'value')]
    )
    def update_standalone_map(geojson_contents, n_clicks, zoom, filename, city_name):
        """Update Standalone Folium map based on GeoJSON upload, city search, and zoom level."""
        
        latitude, longitude, error_msg = 30, -80, None  # Default location

        # ✅ Handle city name search separately
        if ctx.triggered_id == "search-standalone-city-btn" and city_name:
            lat, lon, error_msg = get_city_coordinates(city_name)
            if lat and lon:
                latitude, longitude = lat, lon
            else:
                return html.Div(f"⚠️ Error: {error_msg}", className="text-danger")

        # ✅ Handle GeoJSON Upload
        geojson_data = None
        if geojson_contents:
            try:
                content_type, content_string = geojson_contents.split(',')
                decoded = base64.b64decode(content_string).decode('utf-8')
                geojson_data = json.loads(decoded)
            except Exception as e:
                return html.Div(f"⚠️ Error parsing GeoJSON: {str(e)}", className="text-danger")

        # ✅ Generate Standalone Map with Zoom
        standalone_map_html = phylo_map.generate_standalone_map(geojson_data, latitude, longitude, zoom)

        return html.Iframe(
            srcDoc=standalone_map_html,
            width="100%",
            height="600px",
            style={"border": "none"}
        )



    @app.callback(
        [Output('snp-heatmap-container', 'children'),
         Output('snp-table-container', 'children')],  # New Output for DataTable
        Input('upload-snp-matrix', 'contents'),
        State('upload-snp-matrix', 'filename')
    )
    def update_snp_heatmap(file_contents, file_name):
        if not file_contents:
            return html.Div("No file uploaded yet.", className="text-warning"), html.Div()

        try:
            # Decode the uploaded file
            content_type, content_string = file_contents.split(',')
            decoded = base64.b64decode(content_string)
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')), sep='\t')

            # ✅ Rename first column dynamically
            first_column_name = df.columns[0]
            df.rename(columns={first_column_name: "Sample"}, inplace=True)

            # ✅ Melt DataFrame correctly
            df_melted = df.melt(id_vars=["Sample"], var_name="Variable", value_name="Value")

            # ✅ Ensure pivot table is properly formed
            if not df_melted["Variable"].isin(df["Sample"]).all():
                return html.Div("Error: Some column names do not match the sample names.", className="text-danger"), html.Div()

            # ✅ Pivot DataFrame for heatmap
            pivot_df = df_melted.pivot(index="Sample", columns="Variable", values="Value")

            # ✅ Create the heatmap using Plotly
            fig = px.imshow(
                pivot_df,
                color_continuous_scale='rainbow',
                labels={'color': 'SNP Distance'},
                title="SNP Distance Heatmap"
            )

            # ✅ Make the plot larger
            fig.update_layout(
                xaxis=dict(tickangle=-45),
                margin=dict(l=40, r=40, t=40, b=40),
                width=1000,  # Set the width
                height=800   # Set the height
            )

            heatmap_graph = dcc.Graph(figure=fig)

            # ✅ Create DataTable
            table = dash_table.DataTable(
                data=df.to_dict("records"),  # Convert DataFrame to dictionary format
                columns=[{"name": i, "id": i} for i in df.columns],  # Column names
                page_size=10,  # Show 10 rows per page
                style_table={'overflowX': 'auto'},  # Enable scrolling
                style_header={'backgroundColor': 'lightgrey', 'fontWeight': 'bold', 'color': 'black'},  # ✅ Make header text black
                style_cell={'textAlign': 'center', 'padding': '10px', 'color': 'black'},  # ✅ Make all table text black
            )

            return heatmap_graph, table  # Return both the heatmap and the DataTable

        except Exception as e:
            return html.Div(f"Error processing file: {str(e)}", className="text-danger"), html.Div()
