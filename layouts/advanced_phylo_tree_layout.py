from dash import dcc, html
import dash_bootstrap_components as dbc

advanced_phylo_tree_layout = dcc.Tab(label='Advanced Phylogenetic Tree', children=[
    dbc.Container([
        dbc.Row([
            dbc.Col(html.H5("Upload a Large Tree File and Metadata", className="text-center", style={'color': 'white'}))
        ]),
        dbc.Row([
            dbc.Col([
                dcc.Upload(
                    id='upload-large-tree',
                    children=dbc.Button("Upload Large Tree File", color="primary", className="mt-2"),
                    style={'width': '100%', 'height': '60px', 'lineHeight': '60px',
                           'borderWidth': '1px', 'borderStyle': 'dashed', 'borderRadius': '5px',
                           'textAlign': 'center', 'margin': '10px'},
                    multiple=False
                ),
                dcc.Upload(
                    id='upload-large-metadata',
                    children=dbc.Button("Upload Metadata File", color="primary", className="mt-2"),
                    style={'width': '100%', 'height': '60px', 'lineHeight': '60px',
                           'borderWidth': '1px', 'borderStyle': 'dashed', 'borderRadius': '5px',
                           'textAlign': 'center', 'margin': '10px'},
                    multiple=False
                ),
                dcc.Checklist(
                    id='toggle-large-tip-labels',
                    options=[{'label': 'Show Tip Labels', 'value': 'SHOW'}],
                    value=[],  
                    style={"marginTop": "10px"}
                ),
                dcc.Dropdown(
                    id='color-by-metadata',
                    options=[],
                    placeholder='Color by Metadata Column...',
                    className="mt-2"
                ),
            ], width=12)
        ]),
        dbc.Row([
            dbc.Col(html.Div(id='large-tree-graph-container'), width=12)  # Large tree graph container
        ])
    ])
])
