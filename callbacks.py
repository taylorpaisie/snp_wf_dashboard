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

def generate_location_colors(locations):
    unique_locations = locations.unique()
    colors = px.colors.qualitative.Plotly
    color_map = {loc: colors[i % len(colors)] for i, loc in enumerate(unique_locations)}
    return color_map

def create_tree_plot(tree_file, metadata_file, show_tip_labels, height=1000, width=900):
    # Load tree and metadata
    tree = Phylo.read(tree_file, 'newick')
    tree.root_at_midpoint()  # Midpoint rooting for better visual balance

    metadata = pd.read_csv(metadata_file, sep='\t')

    # Validate required columns
    if 'taxa' not in metadata.columns or 'location' not in metadata.columns:
        raise ValueError("Metadata file must contain 'taxa' and 'location' columns.")

    metadata['location'] = metadata['location'].fillna('Unknown')

    # Dynamically generate color mapping from metadata locations
    location_colors = generate_location_colors(metadata['location'])

    # Generate x and y coordinates using cumulative branch lengths
    x_coords = {}
    y_coords = {}
    max_y = 0

    def assign_coordinates(clade, x_start=0, y_start=0):
        nonlocal max_y
        branch_length = clade.branch_length if clade.branch_length else 0.0
        x_current = x_start + branch_length
        if clade.is_terminal():
            x_coords[clade] = x_current
            y_coords[clade] = y_start
            max_y = max(max_y, y_start)
            return y_start + 1
        else:
            y_positions = []
            for child in clade.clades:
                y_start = assign_coordinates(child, x_current, y_start)
                y_positions.append(y_start - 1)
            x_coords[clade] = x_current
            y_coords[clade] = sum(y_positions) / len(y_positions)
            return y_start

    assign_coordinates(tree.root)

    # Create line shapes for branches using accurate branch lengths
    line_shapes = []
    for clade in tree.find_clades(order='level'):
        x_start = x_coords[clade]
        y_start = y_coords[clade]
        if clade.clades:
            y_positions = [y_coords[child] for child in clade.clades]
            # Vertical line for connecting children
            line_shapes.append(dict(
                type='line',
                x0=x_start, y0=min(y_positions),
                x1=x_start, y1=max(y_positions),
                line=dict(color='black', width=3)  # Thicker lines
            ))
            # Horizontal lines for branches
            for child in clade.clades:
                x_end = x_coords[child]
                y_end = y_coords[child]
                line_shapes.append(dict(
                    type='line',
                    x0=x_start, y0=y_end,
                    x1=x_end, y1=y_end,
                    line=dict(color='black', width=3)  # Thicker lines
                ))

    # Create scatter points for tips and support values > 90
    tip_markers = []
    node_markers = []
    seen_locations = set()
    for clade in tree.find_clades():
        x = x_coords[clade]
        y = y_coords[clade]
        if clade.is_terminal():
            meta_row = metadata[metadata['taxa'] == clade.name]
            location = meta_row['location'].iloc[0] if not meta_row.empty else 'Unknown'
            color = location_colors.get(location, 'gray')

            show_legend = location not in seen_locations
            if show_legend:
                seen_locations.add(location)

            tip_markers.append(go.Scatter(
                x=[x],
                y=[y],
                mode='markers+text' if show_tip_labels else 'markers',
                marker=dict(size=12, color=color, line=dict(width=1.5, color='black')),
                name=location if show_legend else None,
                text=f"<b>{clade.name}</b><br>Location: {location}" if show_tip_labels else "",
                textposition="middle right",
                hoverinfo='text',
                showlegend=show_legend
            ))
        else:
            # Plot support values > 90 as red triangles
            if clade.confidence and clade.confidence > 90:
                node_markers.append(go.Scatter(
                    x=[x],
                    y=[y],
                    mode='markers',
                    marker=dict(size=10, color='black', symbol='diamond'),
                    hoverinfo='skip',
                    showlegend=False
                ))

    # Add a scale bar equivalent
    scale_bar = [
        dict(
            type='line',
            x0=0, y0=-1,
            x1=0.05, y1=-1,
            line=dict(color='black', width=2)
        )
    ]

    layout = go.Layout(
        title='Phylogenetic Tree with Midpoint Rooting and Support Values',
        xaxis=dict(title='Evolutionary Distance', showgrid=False, zeroline=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-1, max_y + 1]),
        shapes=line_shapes + scale_bar,
        height=height,  # Dynamic height
        width=width,  # Dynamic width  # Adjust width for better alignment
        legend=dict(title="Locations", orientation="h", y=-0.2),
    )

    return go.Figure(data=tip_markers + node_markers, layout=layout)

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

                # ✅ Validate FASTA format using Biopython
                fasta_io = StringIO(decoded)
                records = list(SeqIO.parse(fasta_io, "fasta"))

                if not records:
                    return html.Div("Uploaded file is not a valid FASTA file (No valid sequences found).", className="text-danger")

                # ✅ Render the AlignmentChart
                return dashbio.AlignmentChart(
                    id='alignment-viewer',
                    data=decoded,
                    colorscale=colorscale if colorscale else 'nucleotide',
                    tilewidth=20
                )

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
