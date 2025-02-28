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

# Map borough names to borough codes
borough_mapping = {
    'B': 'Bronx',
    'S': 'Staten Island',
    'K': 'Brooklyn',
    'M': 'Manhattan',
    'Q': 'Queens'
}
nyc_arrests['borough'] = nyc_arrests['ARREST_BORO'].map(borough_mapping)

nyc_precinct['precinct'] = pd.to_numeric(
    nyc_precinct['precinct'],
    downcast='integer',
    errors='coerce'
)

# Merge arrest data with GeoJSON data
arrest_data_geo = nyc_precinct.merge(
    nyc_arrests,
    how="left",
    left_on="precinct",
    right_on="ARREST_PRECINCT"
)

# Grouped data for initial visualization
arrest_data_grouped_geo = arrest_data_geo.groupby(
    "borough"
).size().reset_index(name='counts')

# Merge grouped data with GeoJSON data
nyc_full = arrest_data_grouped_geo.merge(
    nyc_boroughs,
    how="left",
    left_on="borough",
    right_on="name"
)

# Select columns
nyc_full = nyc_full[
    ["borough", "counts", "geometry"]
]

# Rename columns
nyc_full = nyc_full.rename(
    columns={'borough': 'Borough', 'counts': 'Arrests'}
)

# Convert GeoDataFrame to DataFrame
nyc_full["geojson"] = nyc_full["geometry"].apply(lambda x: x.__geo_interface__)

# Normalize the GeoJSON data
geo_data = pd.json_normalize(nyc_full["geojson"])
geo_data["Borough"] = nyc_full["Borough"]
geo_data["Arrests"] = nyc_full["Arrests"]

# Initiatlize the app
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# Create map altair object
map_chart = alt.Chart(
    geo_data,
    width=600,
    height=500
).mark_geoshape(
    stroke='grey'
).project(
    'albersUsa'
).encode(
    color='Arrests',
    tooltip=['Borough', alt.Tooltip('Arrests', format=',')]
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