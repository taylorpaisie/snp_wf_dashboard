from dash import html, dcc
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto

# Define layout
app_layout = dbc.Container([
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
