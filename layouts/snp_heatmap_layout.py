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
                html.Div(id='snp-heatmap-container', className="mt-4"),
                html.Hr(),
                html.H5("SNP Distance Matrix Table", className="text-center mt-4", style={'color': 'white'}),
                html.Div(id='snp-table-container', className="mt-4"),
            ], width=12)
        ])
    ])
])
