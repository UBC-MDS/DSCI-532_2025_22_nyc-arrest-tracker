import dash_bootstrap_components as dbc
from dash import Dash, html
from flask_caching import Cache

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

from .utils.helpers import filter_data_by_date_range

# Initialization
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

cache = Cache(app.server, config={'CACHE_TYPE': 'simple'}) 


app.title = "Arrest Tracker"

# Cache the filter_data_by_date_range function
@cache.memoize(timeout=60*60)  # Cache for 1 hour
def cached_filter_data_by_date_range(data, start_date, end_date):
    return filter_data_by_date_range(data, start_date, end_date)


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
