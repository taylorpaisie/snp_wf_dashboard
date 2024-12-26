import base64
from dash import Input, Output, State
from dash_bio import AlignmentChart
from Bio import Phylo
import io

def register_callbacks(app):
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
                return "Uploaded file is not a valid FASTA file."
        return "No FASTA file uploaded yet."

    @app.callback(
        Output('phylo-tree', 'elements'),
        Input('upload-tree', 'contents'),
        State('upload-tree', 'filename')
    )
    def display_tree(file_contents, file_name):
        if file_contents:
            if file_name.endswith('.tree') or file_name.endswith('.nwk'):
                content_type, content_string = file_contents.split(',')
                decoded = base64.b64decode(content_string).decode('utf-8')

                tree = Phylo.read(io.StringIO(decoded), "newick")
                elements = []

                def add_clade(clade, parent=None):
                    node_id = str(id(clade))
                    label = clade.name if clade.name else "Internal Node"
                    elements.append({'data': {'id': node_id, 'label': label}})
                    if parent:
                        elements.append({'data': {'source': parent, 'target': node_id}})
                    for child in clade.clades:
                        add_clade(child, node_id)

                add_clade(tree.root)
                return elements
        return []
