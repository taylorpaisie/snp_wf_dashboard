from dash import dcc, html
import dash_bootstrap_components as dbc

phylo_tree_layout = dcc.Tab(label='Phylogenetic Tree Visualization', children=[
    dbc.Container([
        dbc.Row([
            dbc.Col(html.H5("Upload a Newick Tree File, Metadata File, and Optional Color Map", className="text-center", style={'color': 'white'}))
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
                # ✅ Tip Label Toggle
                dcc.Checklist(
                    id='show-tip-labels',
                    options=[{'label': 'Show Tip Labels', 'value': 'SHOW'}],
                    value=[],  
                    style={"marginTop": "10px"}
                ),
                html.Br(),
            ], width=12)
        ]),

        dbc.Row([
            dbc.Col([
                html.Label("Select Color Palette for Location Labels:", 
                    style={'color': 'white'}),
                dcc.Dropdown(
                    id='color-palette-dropdown-location',  # New dropdown for location colors
                    options=[
                        {'label': 'Plotly', 'value': 'Plotly'},
                        {'label': 'Vivid', 'value': 'Vivid'},
                        {'label': 'Bold', 'value': 'Bold'},
                        {'label': 'Pastel', 'value': 'Pastel'},
                        {'label': 'Dark24', 'value': 'Dark24'},
                        {'label': 'Alphabet', 'value': 'Alphabet'},
                        {'label': 'Set1', 'value': 'Set1'},
                        {'label': 'Set2', 'value': 'Set2'},
                        {'label': 'Set3', 'value': 'Set3'}
                    ],
                    value='Plotly',  # Default palette
                    clearable=False,
                    style={
                        'color': '#000000',
                        'backgroundColor': '#ffffff'}
                ),
            ], 
            className="dbc", width=6),

            dbc.Col([
                html.Label("Select Color Palette for MLST Labels:", 
                    style={'color': 'white'}),
                dcc.Dropdown(
                    id='color-palette-dropdown',
                    options=[
                        {'label': 'Plotly', 'value': 'Plotly'},
                        {'label': 'Vivid', 'value': 'Vivid'},
                        {'label': 'Bold', 'value': 'Bold'},
                        {'label': 'Pastel', 'value': 'Pastel'},
                        {'label': 'Dark24', 'value': 'Dark24'},
                        {'label': 'Alphabet', 'value': 'Alphabet'},
                        {'label': 'Set1', 'value': 'Set1'},
                        {'label': 'Set2', 'value': 'Set2'},
                        {'label': 'Set3', 'value': 'Set3'}
                    ],
                    value='Plotly',  # Default palette
                    clearable=False,
                    style={
                        'color': '#000000',
                        'backgroundColor': '#ffffff'}
                ),
            ], 
            className="dbc", width=6),

        ]),

        html.Hr(),  # Horizontal Lin
        # Phylogenetic Tree Graph Display
        dbc.Row([
            dbc.Col(html.Div(id='tree-graph-container'), width=12),
        ]),

        html.Br(),

        # Button to Download Tree as SVG
        dbc.Row([
            dbc.Col([
                dbc.Button("Download Tree as SVG", id="download-svg-btn", color="success", className="mt-3"),
                dcc.Download(id="download-svg")
            ], width=12, className="d-flex justify-content-center"),
        ])
    ])
])
