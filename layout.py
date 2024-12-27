from dash import html, dcc
import dash_bootstrap_components as dbc
from io import StringIO
from Bio import Phylo
import base64


# Function to render phylogenetic tree to SVG format
def render_phylogenetic_tree(file_contents):
    # Decode the uploaded Newick file
    content_type, content_string = file_contents.split(',')
    decoded = base64.b64decode(content_string).decode('utf-8')

    # Parse the Newick tree
    tree = Phylo.read(StringIO(decoded), "newick")

    # Convert tree to ASCII or SVG representation
    output = StringIO()
    Phylo.draw(tree, do_show=False)  # You can use this to save as SVG directly
    ascii_tree = tree.format("ascii")
    return html.Pre(ascii_tree)  # Embed as preformatted text


# Define the layout
app_layout = dbc.Container([
    dbc.NavbarSimple(
        brand="SNP Workflow Dashboard",
        brand_href="#",
        color="primary",
        dark=True,
    ),
    dcc.Tabs([
        # Tab for MSA Visualization
        dcc.Tab(label='MSA Visualization', children=[
            dbc.Container([
                dbc.Row([
                    dbc.Col(html.H5("Upload a FASTA File to Visualize MSA", className="text-center text-secondary mb-4"))
                ]),
                dbc.Row([
                    dbc.Col([
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
                        dcc.Dropdown(
                            id='alignment-colorscale',
                            options=[
                                {'label': 'Nucleotide', 'value': 'nucleotide'},
                                {'label': 'Amino Acid', 'value': 'aminoacid'},
                                {'label': 'Custom', 'value': 'custom'}
                            ],
                            value='nucleotide',
                            placeholder="Select Color Scale",
                            className="mt-2"
                        ),
                    ], width=12)
                ])
            ])
        ]),
        # Tab for Phylogenetic Tree
        dcc.Tab(label='Phylogenetic Tree', children=[
            dbc.Container([
                dbc.Row([
                    dbc.Col(html.H5("Upload a Newick Tree File to Visualize Phylogenetic Trees", className="text-center text-secondary mb-4"))
                ]),
                dbc.Row([
                    dbc.Col([
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
                        html.Div(id='phylo-tree-container', className="mt-4")
                    ], width=12)
                ])
            ])
        ])
    ])
], fluid=True)
