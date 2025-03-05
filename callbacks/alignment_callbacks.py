import base64
import io
from dash import html, Input, Output, State
import dash_bio as dashbio
from Bio import SeqIO
from config import logger

def register_alignment_callbacks(app):
    @app.callback(
        Output('output-alignment-chart', 'children'),
        [Input('upload-fasta', 'contents'),
         Input('alignment-colorscale', 'value')],
        [State('upload-fasta', 'filename')]
    )
    def display_msa(file_contents, colorscale, file_name):
        if not file_contents:
            return html.Div("No FASTA file uploaded yet.", className="text-warning")

        try:
            content_type, content_string = file_contents.split(',')
            decoded = base64.b64decode(content_string).decode('utf-8')
            records = list(SeqIO.parse(io.StringIO(decoded), "fasta"))

            if not records:
                return html.Div("Uploaded file is not a valid FASTA file.", className="text-danger")

            return dashbio.AlignmentChart(
                id='alignment-viewer',
                data=decoded,
                colorscale=colorscale if colorscale else 'nucleotide',
                tilewidth=20
            )

        except Exception as e:
            logger.error(f"Error processing FASTA file: {str(e)}")
            return html.Div(f"Error processing file: {str(e)}", className="text-danger")
