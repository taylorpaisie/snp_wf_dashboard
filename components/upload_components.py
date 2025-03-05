from dash import dcc
import dash_bootstrap_components as dbc

def upload_component(upload_id, button_text):
    """Creates a Dash upload component with a styled button."""
    return dcc.Upload(
        id=upload_id,
        children=dbc.Button(button_text, color="primary", className="mt-2"),
        style={
            'width': '100%', 'height': '60px', 'lineHeight': '60px',
            'borderWidth': '1px', 'borderStyle': 'dashed', 'borderRadius': '5px',
            'textAlign': 'center', 'margin': '10px'
        },
        multiple=False
    )
