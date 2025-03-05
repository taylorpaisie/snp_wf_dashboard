from dash import dcc, html
import dash_bootstrap_components as dbc

phylo_tree_layout = dcc.Tab(label='Phylogenetic Tree Visualization', children=[
    dbc.Container([
        dbc.Row([
            dbc.Col(html.H5("Upload a Newick Tree File and Metadata File", className="text-center", style={'color': 'white'}))
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
                    value=[],  
                    style={"marginTop": "10px"}
                ),
            ], width=12)
        ]),
        dbc.Row([
            dbc.Col(html.Div(id='tree-graph-container'), width=12)
        ])
    ])
])
