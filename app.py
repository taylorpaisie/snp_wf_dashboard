from dash import Dash
import dash_bootstrap_components as dbc
from layouts.layout import app_layout
from callbacks import register_callbacks
from config import APP_PORT, APP_DEBUG, logger

# ✅ Initialize Dash app
app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.SUPERHERO, dbc.icons.BOOTSTRAP],
    suppress_callback_exceptions=True
)

server = app.server  # ✅ Expose the underlying Flask server


app.layout = app_layout

# ✅ Register callbacks
register_callbacks(app)

if __name__ == '__main__':
    logger.info("🚀 Starting Dash app...")
    app.run_server(debug=APP_DEBUG, port=APP_PORT)
