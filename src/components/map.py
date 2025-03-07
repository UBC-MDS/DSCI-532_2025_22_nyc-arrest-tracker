import dash_bootstrap_components as dbc
import dash_vega_components as dvc

map_chart = dbc.Col(
    dvc.Vega(
        id='map',
        spec={},
        signalsToObserve=['select_region']
    ),
    md=8
)
