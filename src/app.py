import dash_bootstrap_components as dbc
from dash import Dash

from . import callbacks
from .components import (
    age_pie_chart,
    collapse_button,
    crime_pie_chart,
    footer_info,
    gender_pie_chart,
    map_chart,
    sidebar,
    title_comp
)

# Initialization
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Layout
app.layout = dbc.Container([
    dbc.Row([
        title_comp,
        dbc.Col(collapse_button, width="auto"),  # Collapse Button beside it
    ], align="center", className="mb-3"),  # Align items and add margin
    sidebar,
    dbc.Row([
        map_chart,
        # Column for the pie charts (placed right)
        dbc.Col([
            crime_pie_chart,
            gender_pie_chart,
            age_pie_chart
        ], md=4)
    ]),
    dbc.Row(footer_info)
], fluid=True)

# Run the app/dashboard
if __name__ == '__main__':
    app.run_server(debug=True)

