from dash import dcc
import plotly.graph_objects as go

def create_empty_graph(title="No Data Available"):
    """Returns an empty graph placeholder with a title."""
    fig = go.Figure()
    fig.update_layout(
        title=title,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        annotations=[dict(
            text="No data available",
            x=0.5, y=0.5,
            font_size=20,
            showarrow=False
        )]
    )
    return dcc.Graph(figure=fig)
