import base64
from dash import Input, Output, State, html
from dash.exceptions import PreventUpdate
import plotly.graph_objs as go
from Bio import Phylo
from io import StringIO
import pandas as pd
from dash import dcc
from dash_bio.utils import PdbParser
from dash_bio import AlignmentChart


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

def create_tree_plot(tree_file, metadata_file):
    tree = Phylo.read(tree_file, 'newick')
    x_coords, y_coords = get_rectangular_coordinates(tree)

    metadata = pd.read_csv(metadata_file, sep='\t')
    location_colors = {loc: f"hsl({i * 360 / len(metadata['location'].unique())}, 70%, 50%)" for i, loc in enumerate(metadata['location'].unique())}

    line_shapes = []
    draw_clade_rectangular(tree.root, 0, line_shapes, x_coords, y_coords)

    # Create scatter points for tips
    tip_markers = []
    for clade, x in x_coords.items():
        if clade.is_terminal():
            y = y_coords[clade]
            if clade.name in metadata['strain'].values:
                meta_row = metadata[metadata['strain'] == clade.name].iloc[0]
                color = location_colors.get(meta_row['location'], 'gray')
                tip_markers.append(go.Scatter(
                    x=[x],
                    y=[y],
                    mode='markers',
                    marker=dict(size=10, color=color, line=dict(width=1, color='black')),
                    name=meta_row['location'],
                    text=f"{clade.name}<br>Location: {meta_row['location']}<br>Date: {meta_row['date']}",
                    hoverinfo='text'
                ))

    layout = go.Layout(
        title='Phylogenetic Tree (Rectangular Layout)',
        xaxis=dict(title='Evolutionary Distance', showgrid=True, zeroline=False, range=[0, max(x_coords.values()) * 1.1]),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[min(y_coords.values()) - 1, max(y_coords.values()) + 1]),
        shapes=line_shapes,
        height=800
    )
    return go.Figure(data=tip_markers, layout=layout)

def register_callbacks(app):
    @app.callback(
        Output('output-alignment-chart', 'children'),
        [Input('upload-fasta', 'contents'),
        Input('alignment-colorscale', 'value')],
        State('upload-fasta', 'filename')
    )
    def display_msa(file_contents, colorscale, file_name):
        if file_contents:
            try:
                # Decode the uploaded file
                content_type, content_string = file_contents.split(',')
                decoded = base64.b64decode(content_string).decode('utf-8')
                print("Decoded FASTA content:", decoded)  # Debugging output

                if file_name.endswith('.fasta'):
                    # Render the AlignmentChart
                    return AlignmentChart(
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

    @app.callback(
        Output('tree-graph-container', 'children'),
        [Input('upload-tree', 'contents'), Input('upload-metadata', 'contents')],
        [State('upload-tree', 'filename'), State('upload-metadata', 'filename')]
    )
    def update_tree(tree_contents, metadata_contents, tree_filename, metadata_filename):
        if tree_contents and metadata_contents:
            try:
                tree_data = base64.b64decode(tree_contents.split(",", 1)[1]).decode("utf-8")
                metadata_data = base64.b64decode(metadata_contents.split(",", 1)[1]).decode("utf-8")
                tree_file = "uploaded_tree.tree"
                metadata_file = "uploaded_metadata.tsv"

                with open(tree_file, "w") as f:
                    f.write(tree_data)

                with open(metadata_file, "w") as f:
                    f.write(metadata_data)

                fig = create_tree_plot(tree_file, metadata_file)
                return dcc.Graph(figure=fig)
            except Exception as e:
                return html.Div(f"An error occurred: {str(e)}", className="text-danger")
        return html.Div("Please upload both a tree file and a metadata file.", className="text-warning")
