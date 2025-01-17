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
    from plotly.colors import qualitative

    # Load tree and metadata
    tree = Phylo.read(tree_file, 'newick')
    metadata = pd.read_csv(metadata_file, sep='\t')

    # Function to sort clades by branch length
    def sort_clades_by_branch_length(clade):
        if not clade.is_terminal():
            clade.clades.sort(key=lambda child: child.branch_length if child.branch_length else 0)
            for child in clade.clades:
                sort_clades_by_branch_length(child)

    # Sort the tree
    sort_clades_by_branch_length(tree.root)

    # Map metadata to colors
    location_colors = {
        loc: qualitative.Set3[i % len(qualitative.Set3)]
        for i, loc in enumerate(metadata['location'].unique())
    }

    # Generate x and y coordinates
    x_coords = {}
    y_coords = {}
    max_y = 0

    def assign_coordinates(clade, x_start=0, y_start=0):
        nonlocal max_y
        branch_length = clade.branch_length if clade.branch_length else 0.001  # Minimal branch length
        if clade.is_terminal():
            # Assign coordinates for tips
            x_coords[clade] = x_start + branch_length
            y_coords[clade] = y_start
            max_y = max(max_y, y_start)
            return y_start + 1
        else:
            # Recursively assign coordinates for child clades
            y_positions = []
            for child in clade.clades:
                y_start = assign_coordinates(child, x_start + branch_length, y_start)
                y_positions.append(y_start - 1)
            # Position the internal node at the average of its children
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
            # Draw vertical lines connecting children
            y_positions = [y_coords[child] for child in clade.clades]
            line_shapes.append(dict(
                type='line',
                x0=x_start, y0=min(y_positions),
                x1=x_start, y1=max(y_positions),
                line=dict(color='black', width=1)
            ))
            # Draw horizontal lines to children
            for child in clade.clades:
                x_end = x_coords[child]
                y_end = y_coords[child]
                line_shapes.append(dict(
                    type='line',
                    x0=x_start, y0=y_end,
                    x1=x_end, y1=y_end,
                    line=dict(color='black', width=1)
                ))

    # Create scatter points for tips with unique legend entries
    tip_markers = []
    seen_locations = set()
    for clade in tree.get_terminals():
        x = x_coords[clade]
        y = y_coords[clade]
        if clade.name in metadata['strain'].values:
            meta_row = metadata[metadata['strain'] == clade.name].iloc[0]
            location = meta_row['location']
            color = location_colors.get(location, 'gray')

            # Add to legend only if not already seen
            show_legend = location not in seen_locations
            if show_legend:
                seen_locations.add(location)

            tip_markers.append(go.Scatter(
                x=[x],
                y=[y],
                mode='markers+text',
                marker=dict(size=10, color=color, line=dict(width=1, color='black')),
                name=location if show_legend else None,  # Add legend entry only once
                text=f"<b>{clade.name}</b><br>Location: {meta_row['location']}<br>Date: {meta_row['date']}",
                textposition="middle right",
                hoverinfo='text',
                showlegend=show_legend  # Show legend only for the first occurrence
            ))

    layout = go.Layout(
        title='Phylogenetic Tree (Sorted by Branch Length)',
        xaxis=dict(
            title='Evolutionary Distance',
            showgrid=True,
            zeroline=False
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            range=[-1, max_y + 1]
        ),
        shapes=line_shapes,
        height=800,
        legend=dict(title="Locations", orientation="h", y=-0.2),
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
