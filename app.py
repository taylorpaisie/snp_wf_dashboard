from dash import Dash
import dash_bootstrap_components as dbc
from layout import app_layout
import callbacks

# Initialize app
app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

# ✅ Allow dynamically loaded components
app.config.suppress_callback_exceptions = True  

app.layout = app_layout
server = app.server  # For deployment

# Import callbacks (ensures they're registered)
callbacks.register_callbacks(app)

if __name__ == '__main__':
    app.run_server(debug=True)
