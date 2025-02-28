import altair as alt
import dash_bootstrap_components as dbc
import dash_vega_components as dvc
from dash import Dash, dcc, callback, Input, Output, html
import geopandas as gpd
import pandas as pd

# Load the NYC borough GeoJSON data
borough_url = "https://raw.githubusercontent.com/codeforgermany/click_that_hood/refs/heads/main/public/data/new-york-city-boroughs.geojson"
nyc_boroughs = gpd.read_file(borough_url)

# Load the NYPD Precinct GeoJSON data
precinct_url = "https://raw.githubusercontent.com/ResidentMario/geoplot-data/refs/heads/master/nyc-police-precincts.geojson"
nyc_precinct = gpd.read_file(precinct_url)

# Load the NYPD Arrests data
arrest_path = "data/raw/NYPD_Arrest_Data__Year_to_Date_.csv"
nyc_arrests = pd.read_csv(arrest_path)

# Perform data wrangling to tie arrest data to precinct and borough
# GeoJSON data.
nyc_arrests = nyc_arrests[nyc_arrests["ARREST_PRECINCT"] != 483]

# Get precinct centroids
nyc_precinct['precinct_geom'] = nyc_precinct.geometry
nyc_precinct["centroid"] = nyc_precinct["geometry"].centroid
nyc_precinct['geometry'] = nyc_precinct['centroid']

# Perform a spatial join between the precinct and arrest data
nyc_full = gpd.sjoin(nyc_precinct, nyc_boroughs, predicate='within')
nyc_full['geometry'] = nyc_full['precinct_geom']
nyc_full['precinct'] = pd.to_numeric(
    nyc_full['precinct'],
    downcast='integer',
    errors='coerce'
)

# Merge arrest data with GeoJSON data
arrest_data_geo = nyc_full.merge(
    nyc_arrests,
    how="left",
    left_on="precinct",
    right_on="ARREST_PRECINCT"
)

# Grouped data for initial visualization
nyc_arrests_grouped = (nyc_arrests
                       .groupby("ARREST_PRECINCT")
                       .size()
                       .reset_index(name='counts'))

# Merge grouped data with GeoJSON data
arrest_data_grouped_geo = nyc_full.merge(
    nyc_arrests_grouped,
    how="left",
    left_on="precinct",
    right_on="ARREST_PRECINCT"
)

arrest_data_grouped_geo = arrest_data_grouped_geo[
    ["precinct", "name", "counts", "geometry"]
]

# Rename columns
arrest_data_grouped_geo = arrest_data_grouped_geo.rename(
    columns={"precinct": "Precinct", 'name': 'Borough', 'counts': 'Arrests'}
)

# Initiatlize the app
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# Create map altair object
map_chart = alt.Chart(
    arrest_data_grouped_geo,
    width=600,
    height=500
).mark_geoshape(
    stroke='grey'
).project(
    'albersUsa'
).encode(
    color='Arrests',
    tooltip=['Precinct', 'Borough', alt.Tooltip('Arrests', format=',')]
).to_dict()

# Layout
app.layout = dbc.Container([
    html.H1("NYPD Arrests Map"),
    dbc.Row([
        dbc.Col(
            [
                dvc.Vega(spec=map_chart)
            ],
        md=8
        )
    ])
])

# Run the app/dashboard
if __name__ == '__main__':
    server.run()