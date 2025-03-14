import dash_bootstrap_components as dbc
import dash_vega_components as dvc
from dash import dcc

map_chart = dbc.Col(
    dcc.Loading(
        children=[dvc.Vega(
            id='map',
            spec={},
            signalsToObserve=['select_region']
        )]
    ),
    md=6
)
