import base64
import io
import tempfile
import pandas as pd
import plotly.graph_objects as go
from dash import dcc, html, Input, Output, State
from dash.exceptions import PreventUpdate
from Bio import Phylo
import plotly.io as pio
import plotly.express as px
from utils.file_processing import save_uploaded_tree, save_uploaded_metadata, decode_uploaded_file
from utils.color_utils import generate_location_colors, generate_mlst_colors
from config import logger
from utils.rectangular_tree import create_tree_plot
from utils.advanced_phylo_tree import plot_tree_circular 


def register_tree_callbacks(app):
    """Registers all tree-related callbacks for Dash."""
    @app.callback(
        Output('tree-graph-container', 'children'),
        [Input('upload-tree', 'contents'),
        Input('upload-metadata', 'contents'),
        Input('show-tip-labels', 'value'),
        Input('color-palette-dropdown', 'value'),
        Input('color-palette-dropdown-location', 'value')],
        [State('upload-tree', 'filename'),
        State('upload-metadata', 'filename')]
    )
    def update_tree(tree_contents, metadata_contents, show_labels, mlst_palette, location_palette, tree_filename, metadata_filename):
        """Callback to update the REGULAR phylogenetic tree (Rectangular Plot)."""
        if not tree_contents or not metadata_contents:
            return html.Div("Please upload both a tree file and metadata file.", className="text-warning")

        try:
            tree_file = save_uploaded_tree(tree_contents)
            metadata_file = save_uploaded_metadata(metadata_contents)

            # ✅ Pass the palettes to the function
            fig = create_tree_plot(tree_file, metadata_file, show_labels, mlst_palette, location_palette)

            return dcc.Graph(figure=fig)

        except Exception as e:
            logger.error(f"Error processing tree file: {str(e)}")
            return html.Div(f"Error processing tree file: {str(e)}", className="text-danger")



    #export svg
    @app.callback(
        Output("download-svg", "data"),
        [Input("download-svg-btn", "n_clicks")],
        [State('upload-tree', 'contents'),
        State('upload-metadata', 'contents'),
        State('show-tip-labels', 'value'),
        State('color-palette-dropdown', 'value'),
        State('color-palette-dropdown-location', 'value')],
        prevent_initial_call=True
    )
    def export_svg(n_clicks, tree_contents, metadata_contents, show_labels, selected_palette, selected_location_palette):
        """Exports the phylogenetic tree as an SVG file with the correct color palettes."""
        
        if not tree_contents or not metadata_contents:
            raise PreventUpdate  # Ensure function does not execute if no files are uploaded

        show_tip_labels = 'SHOW' in show_labels

        # ✅ Save uploaded files properly
        tree_file = save_uploaded_tree(tree_contents)
        metadata_file = save_uploaded_metadata(metadata_contents)

        # ✅ Pass palette names (not color lists) to `create_tree_plot`
        tree_fig = create_tree_plot(
            tree_file, metadata_file, show_tip_labels, selected_palette, selected_location_palette
        )
        
        # ✅ Save as SVG
        with tempfile.NamedTemporaryFile(delete=False, suffix=".svg") as tmpfile:
            tree_fig.write_image(tmpfile.name, format="svg", engine="kaleido")
            tmpfile_path = tmpfile.name  # Store the file path for return

        return dcc.send_file(tmpfile_path)



    @app.callback(
        Output('large-tree-graph-container', 'children'),
        [Input('upload-large-tree', 'contents'),
        Input('upload-large-metadata', 'contents'),
        Input('toggle-large-tip-labels', 'value'),
        Input('color-by-metadata', 'value')],
        [State('upload-large-tree', 'filename'),
        State('upload-large-metadata', 'filename')]
    )
    def update_large_tree(tree_contents, metadata_contents, show_labels, color_by, tree_filename, metadata_filename):
        """Callback to update the large phylogenetic tree visualization."""
        if not tree_contents or not metadata_contents:
            return html.Div("Please upload both a large tree file and metadata file.", className="text-warning")

        try:
            tree_file = save_uploaded_tree(tree_contents, filename="large_tree.tree")
            metadata_file = save_uploaded_metadata(metadata_contents, filename="large_metadata.tsv")

            tree = Phylo.read(tree_file, 'newick')
            tree.root_at_midpoint()

            # ✅ Fix metadata loading
            metadata = pd.read_csv(metadata_file, sep='\t', skiprows=3, header=None, on_bad_lines="warn")
            metadata = metadata.iloc[:, :4]  # ✅ Keep only the first 4 columns
            metadata.columns = ["taxa", "type", "color", "region"]

            if color_by not in metadata.columns:
                color_by = "region"  # ✅ Default to 'region' if column selection is invalid

            metadata_colors = generate_location_colors(metadata[color_by])

            fig = plot_tree_circular(tree, metadata, metadata_colors, show_labels)  # ✅ Use your function
            return dcc.Graph(figure=fig)

        except Exception as e:
            logger.error(f"Error processing large tree file: {str(e)}")
            return html.Div(f"Error processing tree file: {str(e)}", className="text-danger")



