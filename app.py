import base64
from dash import Dash, html, dcc, Input, Output, State
import dash_bio as dashbio
from Bio import Phylo
import io
import os

app = Dash(__name__)
server = app.server  # Expose the WSGI server for deployment

app.layout = html.Div([
    dcc.Upload(
        id='upload-fasta',
        children=html.Div([
            'Drag and Drop or ', html.A('Select a FASTA File')
        ]),
        style={
            'width': '100%', 'height': '60px', 'lineHeight': '60px',
            'borderWidth': '1px', 'borderStyle': 'dashed', 'borderRadius': '5px',
            'textAlign': 'center', 'margin': '10px'
        },
        multiple=False
    ),
    html.Div(id='output-alignment-chart'),  # Placeholder for MSA

    dcc.Upload(
        id='upload-tree',
        children=html.Div([
            'Drag and Drop or ', html.A('Select a Newick Tree File')
        ]),
        style={
            'width': '100%', 'height': '60px', 'lineHeight': '60px',
            'borderWidth': '1px', 'borderStyle': 'dashed', 'borderRadius': '5px',
            'textAlign': 'center', 'margin': '10px'
        },
        multiple=False
    ),
    html.Div(id='output-tree-chart')       # Placeholder for phylogenetic tree
])


@app.callback(
    Output('output-alignment-chart', 'children'),
    Input('upload-fasta', 'contents'),
    State('upload-fasta', 'filename')
)
def display_msa(file_contents, file_name):
    if file_contents and file_name.endswith('.fasta'):
        content_type, content_string = file_contents.split(',')
        decoded = base64.b64decode(content_string).decode('utf-8')

        # Display the MSA viewer
        return dashbio.AlignmentChart(
            id='alignment-viewer',
            colorscale='nucleotide',
            data=decoded
        )
    return html.Div("Please upload a valid FASTA file.")


@app.callback(
    Output('output-tree-chart', 'children'),
    Input('upload-tree', 'contents'),
    State('upload-tree', 'filename')
)
def display_tree(file_contents, file_name):
    if file_contents and (file_name.endswith('.tree') or file_name.endswith('.nwk')):
        content_type, content_string = file_contents.split(',')
        decoded = base64.b64decode(content_string).decode('utf-8')

        # Parse the Newick file
        tree = Phylo.read(io.StringIO(decoded), "newick")
        ascii_tree = io.StringIO()
        Phylo.draw_ascii(tree, file=ascii_tree)

        # Display tree as plain text (or replace with a visualization library)
        return html.Pre(ascii_tree.getvalue())
    return html.Div("Please upload a valid Newick (.tree/.nwk) file.")


if __name__ == '__main__':
    app.run_server(debug=True)
