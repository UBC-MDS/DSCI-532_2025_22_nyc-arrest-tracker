import dash_bootstrap_components as dbc
from dash import Dash, html

from . import callbacks
from .components import (
    age_pie_chart,
    collapse_button,
    crime_bar_chart,
    footer_toggle_button,
    footer_content,
    gender_pie_chart,
    map_chart,
    sidebar,
    title_comp
)

# Initialization
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server
app.title = "Arrest Tracker"


# Layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(title_comp),
        collapse_button
    ]),
    sidebar,
    dbc.Row([
        dbc.Col(map_chart, md=6),
        dbc.Col([
            crime_bar_chart,
            html.Br(),
            dbc.Row([
                dbc.Col(gender_pie_chart, md=6),
                dbc.Col(age_pie_chart, md=6)
            ])
        ], md=6)
    ]),
    dbc.Row(footer_toggle_button),
    html.Br(),
    html.Br(),
    dbc.Row(dbc.Col(footer_content, width=12))
], fluid=True)

# Run the app/dashboard
if __name__ == '__main__':
    app.run()
