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
        [Input('upload-snp-matrix', 'contents'),
         Input('color-palette-dropdown-heatmap', 'value')],  # ✅ Listen to Dropdown
        State('upload-snp-matrix', 'filename')
    )
    def update_snp_heatmap(file_contents, heatmap_palette, file_name):

        if not file_contents:
            return html.Div("No file uploaded yet.", className="text-warning"), html.Div()

        try:
            content_type, content_string = file_contents.split(',')
            decoded = base64.b64decode(content_string)
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')), sep='\t')

            df.rename(columns={df.columns[0]: "Sample"}, inplace=True)
            df_melted = df.melt(id_vars=["Sample"], var_name="Variable", value_name="Value")
            pivot_df = df_melted.pivot(index="Sample", columns="Variable", values="Value")

            # ✅ Define a color scale mapping dictionary
            color_scales = {
                'viridis': px.colors.sequential.Viridis,
                'plasma': px.colors.sequential.Plasma,
                'inferno': px.colors.sequential.Inferno,
                'magma': px.colors.sequential.Magma,
                'cividis': px.colors.sequential.Cividis,
                'turbo': px.colors.sequential.Turbo,
                'blues': px.colors.sequential.Blues,
                'greens': px.colors.sequential.Greens,
                'oranges': px.colors.sequential.Oranges,
                'reds': px.colors.sequential.Reds,
                'blackbody': px.colors.sequential.Blackbody,
                'rainbow': px.colors.sequential.Rainbow,
                'electric': px.colors.sequential.Electric,
                'hot': px.colors.sequential.Hot
            }

            # ✅ Ensure valid color scale selection (default to Viridis)
            if not heatmap_palette:
                heatmap_palette = 'viridis'  # ✅ Set default if None
            
            selected_palette = color_scales.get(heatmap_palette.lower(), px.colors.sequential.Viridis)

            fig = px.imshow(
                pivot_df,
                color_continuous_scale=selected_palette,  # ✅ Now correctly maps colors
                labels={'color': 'SNP Distance'},
                title=f"SNP Distance Heatmap ({heatmap_palette})"
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
