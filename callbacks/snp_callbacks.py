import base64
import io
import pandas as pd
import plotly.express as px
from dash import dcc, html, Input, Output, State, dash_table
from config import logger

def register_snp_callbacks(app):
    @app.callback(
        [Output('snp-heatmap-container', 'children'),
         Output('snp-table-container', 'children')],
        Input('upload-snp-matrix', 'contents'),
        State('upload-snp-matrix', 'filename')
    )
    def update_snp_heatmap(file_contents, file_name):
        if not file_contents:
            return html.Div("No file uploaded yet.", className="text-warning"), html.Div()

        try:
            content_type, content_string = file_contents.split(',')
            decoded = base64.b64decode(content_string)
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')), sep='\t')

            df.rename(columns={df.columns[0]: "Sample"}, inplace=True)
            df_melted = df.melt(id_vars=["Sample"], var_name="Variable", value_name="Value")
            pivot_df = df_melted.pivot(index="Sample", columns="Variable", values="Value")

            fig = px.imshow(
                pivot_df,
                color_continuous_scale='rainbow',
                labels={'color': 'SNP Distance'},
                title="SNP Distance Heatmap"
            )

            fig.update_layout(
                xaxis=dict(tickangle=-45),
                margin=dict(l=40, r=40, t=40, b=40),
                width=1000,
                height=800
            )

            heatmap_graph = dcc.Graph(figure=fig)

            table = dash_table.DataTable(
                data=df.to_dict("records"),
                columns=[{"name": i, "id": i} for i in df.columns],
                page_size=10,
                style_table={'overflowX': 'auto'},
                style_header={'backgroundColor': 'lightgrey', 'fontWeight': 'bold', 'color': 'black'},
                style_cell={'textAlign': 'center', 'padding': '10px', 'color': 'black'},
            )

            return heatmap_graph, table

        except Exception as e:
            logger.error(f"Error processing SNP matrix: {str(e)}")
            return html.Div(f"Error processing file: {str(e)}", className="text-danger"), html.Div()
