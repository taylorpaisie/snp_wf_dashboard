import base64
from dash import Input, Output, State, html
from dash.exceptions import PreventUpdate
from dash_bio import AlignmentChart
from Bio import Phylo
from io import StringIO
import os
import matplotlib.pyplot as plt

def register_callbacks(app):
    # Callback for MSA Visualization
    @app.callback(
        Output('output-alignment-chart', 'children'),
        [Input('upload-fasta', 'contents'),
         Input('alignment-colorscale', 'value')],
        State('upload-fasta', 'filename')
    )
    def display_msa(file_contents, colorscale, file_name):
        if file_contents:
            if file_name.endswith('.fasta'):
                content_type, content_string = file_contents.split(',')
                decoded = base64.b64decode(content_string).decode('utf-8')

                return AlignmentChart(
                    id='alignment-viewer',
                    data=decoded,
                    colorscale=colorscale if colorscale else 'nucleotide',
                    tilewidth=20
                )
            else:
                return html.Div("Uploaded file is not a valid FASTA file.", className="text-danger")
        return html.Div("No FASTA file uploaded yet.", className="text-warning")

    # Helper function for rendering tree as SVG
    def render_phylogenetic_tree_to_svg(file_contents):
        content_type, content_string = file_contents.split(',')
        decoded = base64.b64decode(content_string).decode('utf-8')
        tree = Phylo.read(StringIO(decoded), "newick")
        svg_path = "tree.svg"

        # Generate SVG
        plt.figure(figsize=(10, 6))
        ax = plt.subplot(111)
        Phylo.draw(tree, do_show=False, axes=ax)
        plt.savefig(svg_path, format="svg")
        plt.close()

        # Read the SVG file back
        with open(svg_path, "r") as svg_file:
            svg_content = svg_file.read()

        # Clean up
        os.remove(svg_path)
        return svg_content

    # Callback for Phylogenetic Tree Visualization (Cytoscape-based)
    @app.callback(
        Output('phylo-tree', 'elements'),
        Output('phylo-tree', 'stylesheet'),
        Input('upload-tree', 'contents'),
        State('upload-tree', 'filename')
    )
    def display_tree_cytoscape(file_contents, file_name):
        if file_contents:
            if file_name.endswith('.tree') or file_name.endswith('.nwk'):
                content_type, content_string = file_contents.split(',')
                decoded = base64.b64decode(content_string).decode('utf-8')

                # Parse the Newick file
                tree = Phylo.read(StringIO(decoded), "newick")
                elements = []

                # Traverse the tree and create Cytoscape elements
                def add_clade(clade, parent=None, depth=0):
                    node_id = str(id(clade))  # Unique ID for each clade
                    label = clade.name if clade.name else f"Node {depth}"
                    elements.append({'data': {'id': node_id, 'label': label}})
                    if parent:
                        elements.append({'data': {'source': parent, 'target': node_id}})
                    for child in clade.clades:
                        add_clade(child, node_id, depth + 1)

                add_clade(tree.root)

                # Define styles mimicking ggtree
                stylesheet = [
                    {
                        'selector': 'node',
                        'style': {
                            'label': 'data(label)',
                            'shape': 'circle',
                            'background-color': 'blue',
                            'width': '10px',
                            'height': '10px',
                            'font-size': '12px',
                            'text-valign': 'center',
                            'color': 'white'
                        }
                    },
                    {
                        'selector': 'edge',
                        'style': {
                            'line-color': '#888',
                            'width': 2,
                            'target-arrow-shape': 'triangle'
                        }
                    }
                ]

                # Add custom styling for specific clades or metadata
                if tree.root.clades:
                    for idx, clade in enumerate(tree.root.clades[:5]):  # Example: Style top 5 clades
                        stylesheet.append({
                            'selector': f'[id = "{id(clade)}"]',
                            'style': {
                                'background-color': f'rgb({50 * idx}, {100 + 10 * idx}, {150 - 10 * idx})',
                                'width': '15px',
                                'height': '15px'
                            }
                        })

                return elements, stylesheet

        return [], []

    # Callback for Phylogenetic Tree Visualization (SVG-based)
    @app.callback(
        Output('phylo-tree-container', 'children'),
        Input('upload-tree', 'contents')
    )
    def display_tree_svg(file_contents):
        if file_contents:
            try:
                svg_content = render_phylogenetic_tree_to_svg(file_contents)
                return html.Div(
                    html.ObjectEl(id="tree-svg", data="data:image/svg+xml;base64," + base64.b64encode(svg_content.encode()).decode(), type="image/svg+xml"),
                    style={"textAlign": "center"}
                )
            except Exception as e:
                return html.Div(f"Error processing tree file: {str(e)}", className="text-danger")
        return html.Div("No tree file uploaded yet.", className="text-warning")
