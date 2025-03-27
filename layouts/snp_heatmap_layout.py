from dash import dcc, html
import dash_bootstrap_components as dbc

snp_heatmap_layout = dcc.Tab(label='SNP Distance Heatmap', children=[
    dbc.Container([
        dbc.Row([
            dbc.Col(html.H5("Upload SNP Distance Matrix to Generate Heatmap", className="text-center", style={'color': 'white'}))
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

            dbc.Col([
                html.Label("Select Color Palette for Location Labels:", style={'color': 'white'}),
                dcc.Dropdown(
                    id='color-palette-dropdown-heatmap',
                    options=[
                        {'label': 'Viridis', 'value': 'viridis'},
                        {'label': 'Plasma', 'value': 'plasma'},
                        {'label': 'Inferno', 'value': 'inferno'},
                        {'label': 'Magma', 'value': 'magma'},
                        {'label': 'Cividis', 'value': 'cividis'},
                        {'label': 'Turbo', 'value': 'turbo'},
                        {'label': 'Blues', 'value': 'blues'},
                        {'label': 'Greens', 'value': 'greens'},
                        {'label': 'Oranges', 'value': 'oranges'},
                        {'label': 'Reds', 'value': 'reds'},
                        {'label': 'Blackbody', 'value': 'blackbody'},
                        {'label': 'Rainbow', 'value': 'rainbow'},
                        {'label': 'Electric', 'value': 'electric'},
                        {'label': 'Hot', 'value': 'hot'}
                    ],
                    value='viridis',
                    clearable=False,
                    style={'color': '#000000', 'backgroundColor': '#ffffff'}
                ),

            ], width=6),


                html.Div(id='snp-heatmap-container', className="mt-4"),
                html.Hr(),
                html.H5("SNP Distance Matrix Table", className="text-center mt-4", style={'color': 'white'}),
                html.Div(id='snp-table-container', className="mt-4"),
            ], width=12)
        ])
    ])
])
