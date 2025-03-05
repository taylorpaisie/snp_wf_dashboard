from dash import dcc, html
import dash_bootstrap_components as dbc

msa_layout = dcc.Tab(label='MSA Visualization', children=[
    dbc.Container([
        dbc.Row([
            dbc.Col(html.H5("Upload a FASTA File to Visualize MSA", className="text-center", style={'color': 'white'}))
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
])
