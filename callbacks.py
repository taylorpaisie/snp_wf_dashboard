import base64, io
from dash import Input, Output, State, dcc, html
from dash.exceptions import PreventUpdate
import plotly.graph_objs as go
from Bio import Phylo
from io import StringIO
import pandas as pd
from dash_bio.utils import PdbParser
from dash_bio import AlignmentChart
import plotly.express as px
from dash import dash_table


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

    # Callback for phylogenetic tree visualization
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
                import base64
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

                # Generate the tree plot with the updated `create_tree_plot` function
                fig = create_tree_plot(tree_file, metadata_file, show_tip_labels)
                return dcc.Graph(figure=fig)
            except Exception as e:
                return html.Div(f"An error occurred: {str(e)}", className="text-danger")
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
                color_continuous_scale='viridis',
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
