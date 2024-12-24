import base64
from dash import Dash, html, dcc, Input, Output, State
import dash_bio as dashbio
from Bio import Phylo
import io
import matplotlib.pyplot as plt
import dash_bootstrap_components as dbc

# Use a Bootstrap theme for enhanced styling
app = Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])
server = app.server  # Expose the WSGI server for deployment

# Layout with enhanced styling and rearranged order
app.layout = dbc.Container([
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
        ], width=12)
    ]),
    # Tree Upload and Visualization
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
            html.Div(id='output-tree-chart', className="mt-4"),
        ], width=12)
    ]),
], fluid=True)


@app.callback(
    Output('output-alignment-chart', 'children'),
    Input('upload-fasta', 'contents'),
    State('upload-fasta', 'filename')
)
def display_msa(file_contents, file_name):
    if file_contents:
        if file_name.endswith('.fasta'):
            content_type, content_string = file_contents.split(',')
            decoded = base64.b64decode(content_string).decode('utf-8')

            # Display the MSA viewer
            return dashbio.AlignmentChart(
                id='alignment-viewer',
                data=decoded,
                colorscale='nucleotide'
            )
        else:
            return html.Div("Uploaded file is not a valid FASTA file.", className="text-danger")
    return html.Div("No FASTA file uploaded yet.", className="text-muted")


@app.callback(
    Output('output-tree-chart', 'children'),
    Input('upload-tree', 'contents'),
    State('upload-tree', 'filename')
)
def display_tree(file_contents, file_name):
    if file_contents:
        if file_name.endswith('.tree') or file_name.endswith('.nwk'):
            content_type, content_string = file_contents.split(',')
            decoded = base64.b64decode(content_string).decode('utf-8')

            # Parse the Newick file
            tree = Phylo.read(io.StringIO(decoded), "newick")

            # Render the tree to a PNG image
            temp_image_path = "tree_image.png"
            fig = plt.figure(figsize=(10, 10))
            Phylo.draw(tree, do_show=False)
            plt.savefig(temp_image_path)
            plt.close(fig)

            # Convert the image to base64 for embedding in Dash
            with open(temp_image_path, "rb") as f:
                encoded_image = base64.b64encode(f.read()).decode('utf-8')

            # Return the image as an HTML element
            return html.Img(src=f"data:image/png;base64,{encoded_image}", style={"width": "100%"})

        else:
            return html.Div("Uploaded file is not a valid Newick file.", className="text-danger")
    return html.Div("No tree file uploaded yet.", className="text-muted")


if __name__ == '__main__':
    app.run_server(debug=True)
