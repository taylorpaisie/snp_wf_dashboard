import dash_bootstrap_components as dbc
from dash import html

def create_alert_modal(modal_id, title, message):
    """Creates a Bootstrap modal for alerts."""
    return dbc.Modal([
        dbc.ModalHeader(title),
        dbc.ModalBody(html.P(message)),
        dbc.ModalFooter(
            dbc.Button("Close", id=f"{modal_id}-close", className="ml-auto", color="primary")
        ),
    ], id=modal_id, is_open=False)
