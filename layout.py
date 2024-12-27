from dash import html, dcc
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto  # Ensure you import Cytoscape

# Define the layout
app_layout = dbc.Container([
    dbc.NavbarSimple(
        brand="SNP Workflow Dashboard",
        brand_href="#",
        color="success",
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
                        html.Div(id='phylo-tree-container', className="mt-4"),
                        cyto.Cytoscape(
                            id='phylo-tree',
                            layout={'name': 'preset'},
                            style={'width': '100%', 'height': '500px'},
                            elements=[],
                            stylesheet=[]
                        )
                    ], width=12)
                ])
            ])
        ])
    ])
], fluid=True)
