import base64
from dash import Dash, html, dcc, Input, Output, State
import dash_bio as dashbio
from Bio import Phylo
import io
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto

# Use a Bootstrap theme for enhanced styling
app = Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])
server = app.server  # Expose the WSGI server for deployment

# Layout with Cytoscape
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("SNP Workflow Dashboard", className="text-center text-primary mb-4")),
    ]),
    dbc.Row([
        dbc.Col(html.H5("Upload your files to visualize MSA and Phylogenetic Trees", className="text-center text-secondary mb-4"))
    ]),
    # MSA Upload and Visualization
    dbc.Row([
        dbc.Col([
            html.H6("Upload FASTA File"),
            dcc.Upload(
                id='upload-fasta',
                children=dbc.Button("Select FASTA File", color="primary", className="mt-2"),
                style={
                    'width': '100%', 'height': '60px', 'lineHeight': '60px',
                    'borderWidth': '1px', 'borderStyle': 'dashed', 'borderRadius': '5px',
                    'textAlign': 'center', 'margin': '10px'
                },
                multiple=False
            ),
            html.Div(id='output-alignment-chart', className="mt-4"),
        ], width=12)
    ]),
    # Tree Upload and Cytoscape Visualization
    dbc.Row([
        dbc.Col([
            html.H6("Upload Newick Tree File"),
            dcc.Upload(
                id='upload-tree',
                children=dbc.Button("Select Tree File", color="primary", className="mt-2"),
                style={
                    'width': '100%', 'height': '60px', 'lineHeight': '60px',
                    'borderWidth': '1px', 'borderStyle': 'dashed', 'borderRadius': '5px',
                    'textAlign': 'center', 'margin': '10px'
                },
                multiple=False
            ),
            cyto.Cytoscape(
                id='phylo-tree',
                layout={'name': 'breadthfirst'},
                style={'width': '100%', 'height': '500px'},
                elements=[],  # Placeholder for tree data
                stylesheet=[
                    {
                        'selector': 'node',
                        'style': {
                            'label': 'data(label)',
                            'background-color': '#0074D9',
                            'color': '#FFFFFF',
                        }
                    },
                    {
                        'selector': 'edge',
                        'style': {
                            'line-color': '#B10DC9',
                            'width': 2,
                        }
                    }
                ]
            )
        ], width=12)
    ]),
], fluid=True)


@app.callback(
    Output('output-alignment-chart', 'children'),
    Input('upload-fasta', 'contents'),
    State('upload-fasta', 'filename')
)
def display_msa(file_contents, file_name):
    if file_contents:
        if file_name.endswith('.fasta'):
            content_type, content_string = file_contents.split(',')
            decoded = base64.b64decode(content_string).decode('utf-8')

            # Display the MSA viewer
            return dashbio.AlignmentChart(
                id='alignment-viewer',
                data=decoded,
                colorscale='nucleotide'
            )
        else:
            return html.Div("Uploaded file is not a valid FASTA file.", className="text-danger")
    return html.Div("No FASTA file uploaded yet.", className="text-muted")


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

            # Parse the Newick file and convert to Cytoscape elements
            tree = Phylo.read(io.StringIO(decoded), "newick")
            elements = []

            def add_clade(clade, parent=None):
                node_id = str(id(clade))  # Unique ID for each clade
                label = clade.name if clade.name else "Internal Node"
                elements.append({'data': {'id': node_id, 'label': label}})
                if parent:
                    elements.append({'data': {'source': parent, 'target': node_id}})
                for child in clade.clades:
                    add_clade(child, node_id)

            # Start traversing the tree from the root
            add_clade(tree.root)

            return elements

    return []


if __name__ == '__main__':
    app.run_server(debug=True)
