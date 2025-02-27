import altair as alt
import dash_bootstrap_components as dbc
import dash_vega_components as dvc
from dash import Dash, dcc, callback, Input, Output
import geopandas as gpd

# This code is adapted from the 532 lecture 4 course notes. This is an initial version just
# so we can get the deployment up and running. This code will be replaced with our actual
# code in the future.

url = 'https://naciscdn.org/naturalearth/50m/cultural/ne_50m_admin_1_states_provinces.zip'
world_regions = gpd.read_file(url)[['wikipedia', 'name', 'region', 'admin', 'postal', 'latitude', 'longitude', 'geometry']]

# Initiatlize the app
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# Layout
app.layout = dbc.Container([
    dcc.Dropdown(id='country', value='India', options=world_regions['admin'].unique()),
    dvc.Vega(id='map', spec={}),
])

# Server side callbacks/reactivity
@callback(
    Output('map', 'spec'),
    Input('country', 'value'),
)
def create_map(country):
    return alt.Chart(world_regions.query(f'admin == "{country}"'), width=600, height=500).mark_geoshape(stroke='white').encode(
        tooltip='name',
        color=alt.Color('name').scale(scheme='tableau20'),  # To avoid repeating colors
    ).to_dict()



# Run the app/dashboard
if __name__ == '__main__':
    server.run()