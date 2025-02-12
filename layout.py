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
                            id='upload-fasta',  # ✅ This ID must match the callback in callbacks.py
                            children=dbc.Button("Select FASTA File", color="primary", className="mt-2"),
                            style={
                                'width': '100%', 'height': '60px', 'lineHeight': '60px',
                                'borderWidth': '1px', 'borderStyle': 'dashed', 'borderRadius': '5px',
                                'textAlign': 'center', 'margin': '10px'
                            },
                            multiple=False
                        ),
                        html.Div(id='output-alignment-chart', className="mt-4", style={"border": "2px solid red"}),
                        dcc.Dropdown(
                            id='alignment-colorscale',
                            options=[
                                {'label': 'Nucleotide', 'value': 'nucleotide'},
                                {'label': 'Amino Acid', 'value': 'aminoacid'},
                                {'label': 'Custom', 'value': 'custom'}
                            ],
                            value='nucleotide',
                            placeholder="Select Color Scale",
                            className="mt-2",
                            style={'color': 'black', 'backgroundColor': 'white'}
                        ),
                        dbc.Button("Test Callback", id="test-button", color="danger", className="mt-2"),
                    ], width=12)
                ])
            ])
        ]),

        # Tab for Phylogenetic Tree Visualization
        dcc.Tab(label='Phylogenetic Tree', children=[
            dbc.Container([
                dbc.Row([
                    dbc.Col(html.H5("Upload a Newick Tree File, Metadata File, and GeoJSON for Map", 
                                    className="text-center text-secondary mb-4"))
                ]),

                # Upload Section
                dbc.Row([
                    dbc.Col([
                        dcc.Upload(
                            id='upload-tree',
                            children=dbc.Button("Select Tree File", color="primary", className="mt-2"),
                            style={'width': '100%', 'height': '60px', 'lineHeight': '60px',
                                   'borderWidth': '1px', 'borderStyle': 'dashed', 'borderRadius': '5px',
                                   'textAlign': 'center', 'margin': '10px'},
                            multiple=False
                        ),
                        dcc.Upload(
                            id='upload-metadata',
                            children=dbc.Button("Select Metadata File", color="primary", className="mt-2"),
                            style={'width': '100%', 'height': '60px', 'lineHeight': '60px',
                                   'borderWidth': '1px', 'borderStyle': 'dashed', 'borderRadius': '5px',
                                   'textAlign': 'center', 'margin': '10px'},
                            multiple=False
                        ),
                        dcc.Upload(
                            id='upload-geojson',
                            children=dbc.Button("Select GeoJSON File", color="primary", className="mt-2"),
                            style={'width': '100%', 'height': '60px', 'lineHeight': '60px',
                                   'borderWidth': '1px', 'borderStyle': 'dashed', 'borderRadius': '5px',
                                   'textAlign': 'center', 'margin': '10px'},
                            multiple=False
                        ),
                        html.Br(),

                        # ✅ New: City Name Input
                        html.Label("Enter a City Name:"),
                        dcc.Input(id="map-city", type="text", placeholder="e.g., New York", className="mb-2"),
                        
                        html.Label("Latitude:"),
                        dcc.Input(id="map-lat", type="number", value=33, step=0.0001, className="mb-2"),
                        html.Label("Longitude:"),
                        dcc.Input(id="map-lon", type="number", value=-83, step=0.0001, className="mb-2"),
                        html.Label("Zoom Level:"),
                        dcc.Slider(
                            id="map-zoom",
                            min=1, 
                            max=18, 
                            step=1, 
                            value=7,  
                            marks={i: str(i) for i in range(5, 21, 3)}
                        ),
                        html.Br(),
                        # ✅ Tip Label Toggle
                        dcc.Checklist(
                            id='show-tip-labels',
                            options=[{'label': 'Show Tip Labels', 'value': 'SHOW'}],
                            value=[],  
                            style={"marginTop": "10px"}
                        ),
                        html.Br(),
                        html.H5("Add Custom Marker", className="text-center text-secondary mt-4"),
                        dbc.Row([
                            dbc.Col([
                                html.Label("Marker Name:"),
                                dcc.Input(id="marker-name", type="text", placeholder="Enter marker name", className="mb-2"),
                            ], width=3),
                            dbc.Col([
                                html.Label("Latitude:"),
                                dcc.Input(id="marker-lat", type="number", placeholder="Enter latitude", className="mb-2"),
                            ], width=3),
                            dbc.Col([
                                html.Label("Longitude:"),
                                dcc.Input(id="marker-lon", type="number", placeholder="Enter longitude", className="mb-2"),
                            ], width=3),
                            dbc.Col([
                                dbc.Button("Add Marker", id="add-marker-btn", color="success", className="mt-4"),
                            ], width=3),
                        ]),
                        html.Br(),
                    ], width=12)
                ]),

                html.Hr(),  # Horizontal Line

                # Row for Phylogenetic Tree and Map
                dbc.Row([
                    dbc.Col(html.Div(id='tree-graph-container'), width=6),  # Tree on the Left (50%)
                    dbc.Col(html.Div(id='phylo-map-container'), width=6),  # Map on the Right (50%)
                ])
            ])
        ]),

        # Tab for Standalone Map
        dcc.Tab(label='Standalone Map Viewer', children=[
            dbc.Container([
                dbc.Row([
                    dbc.Col(html.H5("Upload GeoJSON or Search for a Location", className="text-center text-secondary mb-4"))
                ]),

                # Upload GeoJSON
                dbc.Row([
                    dbc.Col([
                        dcc.Upload(
                            id='upload-standalone-geojson',
                            children=dbc.Button("Upload GeoJSON File", color="primary", className="mt-2"),
                            style={
                                'width': '100%', 'height': '60px', 'lineHeight': '60px',
                                'borderWidth': '1px', 'borderStyle': 'dashed', 'borderRadius': '5px',
                                'textAlign': 'center', 'margin': '10px'
                            },
                            multiple=False
                        ),
                        html.Div(id="standalone-geojson-upload-status", className="mt-2 text-success"),
                    ], width=12)
                ]),

                html.Hr(),

                # Location Search
                dbc.Row([
                    dbc.Col([
                        html.Label("Search for a City Name:"),
                        dcc.Input(id="search-standalone-city", type="text", placeholder="e.g., Paris", className="mb-2"),
                        dbc.Button("Search", id="search-standalone-city-btn", color="primary", className="mt-2"),
                        html.Div(id="standalone-city-search-status", className="mt-2 text-success"),
                    ], width=6)
                ]),

                html.Hr(),

                # Standalone Map Display
                dbc.Row([
                    dbc.Col(html.Div(id='standalone-map-container', style={'height': '600px'}), width=12)
                ])
            ])
        ]),


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
        "background": "grey"  # ✅ Make unselected tab background light grey for contrast
    }
    )
], fluid=True)
