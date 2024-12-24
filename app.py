import base64
from dash import Dash, html, dcc, Input, Output, State
import dash_bio as dashbio

app = Dash(__name__)
server = app.server  # Add this line

app.layout = html.Div([
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ', html.A('Select a FASTA File')
        ]),
        style={
            'width': '100%', 'height': '60px', 'lineHeight': '60px',
            'borderWidth': '1px', 'borderStyle': 'dashed', 'borderRadius': '5px',
            'textAlign': 'center', 'margin': '10px'
        },
        multiple=False
    ),
    html.Div(id='output-alignment-chart')
])


import os
import tempfile

@app.callback(
    Output('output-alignment-chart', 'children'),
    Input('upload-data', 'contents'),
    State('upload-data', 'filename')
)
def update_output(file_contents, file_name):
    if file_contents is not None and file_name.endswith('.fasta'):
        content_type, content_string = file_contents.split(',')
        decoded = base64.b64decode(content_string)

        # Save the file to a temporary location
        temp_file_path = os.path.join(tempfile.gettempdir(), file_name)
        with open(temp_file_path, 'wb') as f:
            f.write(decoded)

        # Optionally, read and process the file
        with open(temp_file_path, 'r') as f:
            file_content = f.read()

        return dashbio.AlignmentChart(
            id='alignment-viewer',
            data=file_content
        )
    else:
        return html.Div("Please upload a valid FASTA file.")



if __name__ == '__main__':
    app.run_server(debug=True)
