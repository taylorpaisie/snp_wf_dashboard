import base64
import io
import pandas as pd
import plotly.graph_objects as go
from dash import dcc, html, Input, Output, State
from dash.exceptions import PreventUpdate
from Bio import Phylo
from utils.file_processing import save_uploaded_tree, save_uploaded_metadata
from utils.color_utils import generate_location_colors
from config import logger
from utils.rectangular_tree import create_tree_plot
from utils.advanced_phylo_tree import plot_tree_circular 


def register_tree_callbacks(app):
    """Registers all tree-related callbacks for Dash."""

    @app.callback(
        Output('tree-graph-container', 'children'),
        [Input('upload-tree', 'contents'),
         Input('upload-metadata', 'contents'),
         Input('show-tip-labels', 'value')],
        [State('upload-tree', 'filename'),
         State('upload-metadata', 'filename')]
    )
    def update_tree(tree_contents, metadata_contents, show_labels, tree_filename, metadata_filename):
        """Callback to update the REGULAR phylogenetic tree (Rectangular Plot)."""
        if not tree_contents or not metadata_contents:
            return html.Div("Please upload both a tree file and metadata file.", className="text-warning")

        try:
            tree_file = save_uploaded_tree(tree_contents)
            metadata_file = save_uploaded_metadata(metadata_contents)

            fig = create_tree_plot(tree_file, metadata_file, show_labels)
            return dcc.Graph(figure=fig)

        except Exception as e:
            logger.error(f"Error processing tree file: {str(e)}")
            return html.Div(f"Error processing tree file: {str(e)}", className="text-danger")

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



