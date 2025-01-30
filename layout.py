from dash import dcc, html
import dash_bootstrap_components as dbc

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

        # Tab for Phylogenetic Tree Visualization
        dcc.Tab(label='Phylogenetic Tree', children=[
            dbc.Container([
                dbc.Row([
                    dbc.Col(html.H5("Upload a Newick Tree File and Metadata File", className="text-center text-secondary mb-4"))
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
                        dcc.Upload(
                            id='upload-metadata',
                            children=dbc.Button("Select Metadata File", color="primary", className="mt-2"),
                            style={
                                'width': '100%', 'height': '60px', 'lineHeight': '60px',
                                'borderWidth': '1px', 'borderStyle': 'dashed', 'borderRadius': '5px',
                                'textAlign': 'center', 'margin': '10px'
                            },
                            multiple=False
                        ),
                        dcc.Checklist(
                            id='show-tip-labels',
                            options=[{'label': 'Show Tip Labels', 'value': 'SHOW'}],
                            value=[],  # Default: labels off
                            style={"marginTop": "10px"}
                        ),
                        html.Div(id='tree-graph-container', className="mt-4")
                    ], width=12)
                ])
            ])
        ]),

        # New Tab for SNP Distance Heatmap
# Tab for SNP Distance Heatmap
        dcc.Tab(label='SNP Distance Heatmap', children=[
            dbc.Container([
                dbc.Row([
                    dbc.Col(html.H5("Upload SNP Distance Matrix to Generate Heatmap", className="text-center text-secondary mb-4"))
                ]),
                dbc.Row([
                    dbc.Col([
                        dcc.Upload(
                            id='upload-snp-matrix',
                            children=dbc.Button("Select SNP Matrix File", color="primary", className="mt-2"),
                            style={
                                'width': '100%', 'height': '60px', 'lineHeight': '60px',
                                'borderWidth': '1px', 'borderStyle': 'dashed', 'borderRadius': '5px',
                                'textAlign': 'center', 'margin': '10px'
                            },
                            multiple=False
                        ),
                        html.Div(id='snp-heatmap-container', className="mt-4"),  # Heatmap
                        html.Hr(),  # Add a horizontal separator
                        html.H5("SNP Distance Matrix Table", className="text-center text-secondary mt-4"),
                        html.Div(id='snp-table-container', className="mt-4"),  # DataTable Container
                    ], width=12)
                ])
            ])
        ])
    ],
    colors={
        "border": "black",      # ✅ Make tab borders black
        "primary": "black",      # ✅ Make selected tab text black
        "background": "lightgrey"  # ✅ Make unselected tab background light grey for contrast
    }
    )
], fluid=True)
