import dash_bootstrap_components as dbc
from dash import Dash

from . import callbacks
from .components import (
    age_pie_chart,
    collapse_button,
    crime_bar_chart,
    footer_info,
    gender_pie_chart,
    map_chart,
    sidebar,
    title_comp
)

# Initialization
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# Layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(title_comp),
        collapse_button
    ]),
    sidebar,
    dbc.Row([
        dbc.Col(map_chart, md=8),
        dbc.Col([
            crime_bar_chart,  
            gender_pie_chart,
            age_pie_chart
        ], md=4)
    ]),
    dbc.Row(footer_info)
], fluid=True)

# Run the app/dashboard
if __name__ == '__main__':
    server.run(debug=True)
