import altair as alt
import dash_bootstrap_components as dbc
import dash_vega_components as dvc
from dash import Dash, dcc, callback, Input, Output
import geopandas as gpd
import pandas as pd

# Load the NYC borough GeoJSON data
borough_url = "https://raw.githubusercontent.com/codeforgermany/click_that_hood/refs/heads/main/public/data/new-york-city-boroughs.geojson"
nyc_boroughs = gpd.read_file(borough_url)

# Load the NYPD Precinct GeoJSON data
precinct_url = "https://raw.githubusercontent.com/ResidentMario/geoplot-data/refs/heads/master/nyc-police-precincts.geojson"
nyc_precinct = gpd.read_file(precinct_url)

# Load the NYPD Arrests data
arrest_path = "data/raw/NYPD_Arrests_Data__Year_to_Date_.csv"
nyc_arrests = pd.read_csv(arrest_path)

# Perform data wrangling to tie arrest data to precinct and borough GeoJSON data
nyc_arrests = nyc_arrests[nyc_arrests["ARREST_PRECINCT"] != 483] # Drop bad precinct

# Get precinct centroids
nyc_precinct['precinct_geom'] = nyc_precinct.geometry
nyc_precinct["centroid"] = nyc_precinct["geometry"].centroid
nyc_precinct['geometry'] = nyc_precinct['centroid']

# Perform a spatial join between the precinct and arrest data
nyc_full = gpd.sjoin(nyc_precinct, nyc_boroughs, predicate='within')
nyc_full['geometry'] = nyc_full['precinct_geom']
nyc_full['precinct'] = pd.to_numeric(nyc_full['precinct'], downcast='integer', errors='coerce')

# Merge arrest data with GeoJSON data
arrest_data_geo = nyc_full.merge(nyc_arrests, how="left", left_on="precinct", right_on="ARREST_PRECINCT")

# Grouped data for initial visualization
nyc_arrests_grouped = (nyc_arrests
                       .groupby("ARREST_PRECINCT")
                       .size()
                       .reset_index(name='counts'))

# Merge grouped data with GeoJSON data
arrest_data_grouped_geo = nyc_full.merge(nyc_arrests_grouped, how="left", left_on="precinct", right_on="ARREST_PRECINCT")


# url = 'https://naciscdn.org/naturalearth/50m/cultural/ne_50m_admin_1_states_provinces.zip'
# world_regions = gpd.read_file(url)[['wikipedia', 'name', 'region', 'admin', 'postal', 'latitude', 'longitude', 'geometry']]

# Initiatlize the app
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# Layout
app.layout = dbc.Container([
    #dcc.Dropdown(id='country', value='India', options=world_regions['admin'].unique()),
    dvc.Vega(id='map', spec={}),
])

# Server side callbacks/reactivity
@callback(
    Output('map', 'spec')
)
def create_map():
    return alt.Chart(arrest_data_grouped_geo, width=600, height=500).mark_geoshape(stroke='white').project(
        'albersUsa'
    ).encode(
        color='counts',
        tooltip=['precinct', alt.Tooltip('counts', format=','), 'name'],
    ).to_dict()
    
# @callback(
#     Output('map', 'spec'),
#     Input('country', 'value'),
# )
# def create_map(country):
#     return alt.Chart(world_regions.query(f'admin == "{country}"'), width=600, height=500).mark_geoshape(stroke='white').encode(
#         tooltip='name',
#         color=alt.Color('name').scale(scheme='tableau20'),  # To avoid repeating colors
#     ).to_dict()

# Run the app/dashboard
if __name__ == '__main__':
    server.run()