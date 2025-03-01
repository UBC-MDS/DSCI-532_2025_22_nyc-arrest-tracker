import altair as alt
import dash_bootstrap_components as dbc
import dash_vega_components as dvc
from dash import Dash, dcc, callback, Input, Output, html, callback_context
import geopandas as gpd
import pandas as pd
import plotly.express as px

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

# Grouped data for initial visualization
arrest_data_grp_borough = nyc_arrests.groupby(
    "borough"
).size().reset_index(name='counts')

# Group by precinct
arrest_data_grp_precinct = nyc_arrests.groupby(
    "ARREST_PRECINCT"
).size().reset_index(name='counts')

# Merge arrest data with GeoJSON data
precinct_geo = nyc_precinct.merge(
    arrest_data_grp_precinct,
    how="left",
    left_on="precinct",
    right_on="ARREST_PRECINCT"
).rename(
    columns={"precinct": "Precinct", "counts": "Arrests"}
)[["Precinct", "Arrests", "geometry"]]

borough_geo = arrest_data_grp_borough.merge(
    nyc_boroughs,
    how="left",
    left_on="borough",
    right_on="name"
).rename(
    columns={"borough": "Borough", "counts": "Arrests"}
)[["Borough", "Arrests", "geometry"]]

# Convert GeoDataFrame to DataFrame
borough_geo["geojson"] = borough_geo["geometry"].apply(
    lambda x: x.__geo_interface__
)
precinct_geo["geojson"] = precinct_geo["geometry"].apply(
    lambda x: x.__geo_interface__
)

geo_b_df = pd.json_normalize(borough_geo["geojson"])
geo_b_df["Borough"] = borough_geo["Borough"]
geo_b_df["Arrests"] = borough_geo["Arrests"]

geo_p_df = pd.json_normalize(precinct_geo["geojson"])
geo_p_df["Precinct"] = precinct_geo["Precinct"]
geo_p_df["Arrests"] = precinct_geo["Arrests"]


# Group the data by the more general offense description (OFNS_DESC)
arrest_crimes = nyc_arrests['OFNS_DESC'].value_counts().reset_index()
arrest_crimes.columns = ['Crime Type', 'Frequency']

# Get the top 10 most frequent crimes
top_crimes = arrest_crimes.head(10)


colors = ['#E63946', '#1D3557', '#F1FAEE', '#457B9D', '#A8DADC',
          '#F1FAEE', '#1D3557', '#E63946', '#457B9D', '#A8DADC']


# Create the pie chart for the top 10 crimes by arrests
def create_pie_chart(data, title):
    data = data.rename(columns={'Crime Type': 'OFNS_DESC', 'Frequency': 'Arrests'})
    
    pie_chart = px.pie(
        data,
        names='OFNS_DESC', 
        values='Arrests',   
        title=title,
        labels={'Arrests': 'Number of Arrests'},
        color='OFNS_DESC',  
        color_discrete_sequence=colors 
    )

    # Customize the hover template for a cleaner look and match the map style
    pie_chart.update_traces(
        hovertemplate='<b>%{label}</b><br>Arrests: %{value}<br>%{percent:.2%} of Total<extra></extra>',
        textinfo='percent',  
    )

    # Remove the legend to avoid large labels on the left
    pie_chart.update_layout(showlegend=False)

    # Remove the arrow from the tooltip and set white background
    pie_chart.update_layout(
        hoverlabel=dict(
            bgcolor="white", 
            font_size=14,     
            font_family="Arial" 
        )
    )
    return pie_chart


# Create the initial pie chart for all of NYC
crime_pie_chart = create_pie_chart(top_crimes, "Top 10 Crime Types")

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# Layout
app.layout = dbc.Container([
    html.H1("NYPD Arrests Map"),
    dbc.Switch(
        id='map-toggle',
        label='Toggle Precincts/Boroughs',
        value=False
    ),
    dbc.Row([
        # Column for the map
        dbc.Col(
            [
                dvc.Vega(id='map', spec={}, signalsToObserve=['select_region'])
            ],
            md=8
        ),
        # Column for the pie chart (placed top-right)
        dbc.Col(
            [
                dcc.Graph(
                    id='crime-pie-chart',
                    figure=crime_pie_chart
                ),
                # Reset button
                dbc.Button("Reset Pie Chart", id="reset-button", color="primary", className="mr-1", n_clicks=0)
            ],
            md=4
        )
    ])
])


# Create map chart function
@callback(
    Output('map', 'spec'),
    Input('map-toggle', 'value')
)
def create_map_chart(toggle_value):
    # Toggle controls whether the map displays boroughs or precincts
    if toggle_value:
        geo_df = geo_p_df
        tooltip_label = 'Precinct'
    else:
        geo_df = geo_b_df
        tooltip_label = 'Borough'

    select_region = alt.selection_point(
        fields=[tooltip_label],
        name='select_region',
        toggle=False
    )
    # Create map
    map_chart = alt.Chart(
        geo_df,
        width=600,
        height=500
    ).mark_geoshape(
        stroke='grey'
    ).project(
        'albersUsa'
    ).encode(
        color='Arrests',
        tooltip=[tooltip_label, alt.Tooltip('Arrests', format=',')],
        opacity=alt.condition(select_region, alt.value(0.9), alt.value(0.3))
    ).add_params(
        select_region
    ).to_dict()

    return map_chart

# Callback 
@callback(
    Output('crime-pie-chart', 'figure'),
    Input('map', 'signalData'),
    Input('reset-button', 'n_clicks')
)
def update_pie_chart(clicked_region, n_clicks):
    # Reset button was clicked
    if callback_context.triggered and callback_context.triggered[0]['prop_id'].startswith('reset-button'):
        return create_pie_chart(top_crimes, "Top 10 Crime Types")

    # Ensure clicked_region is valid
    if clicked_region and 'select_region' in clicked_region:
        # Check if the clicked region is a borough or precinct
        selected_location = clicked_region['select_region'].get(
            'Borough', None
        )

        if not selected_location:
            selected_location = clicked_region['select_region'].get(
                'Precinct', None
            )

        # If selected_location is a list, get the first element
        if isinstance(selected_location, list) and selected_location:
            selected_location = selected_location[0]

        # location should only ever been a string or an int
        if isinstance(selected_location, str) or isinstance(selected_location, int):
            if selected_location in borough_mapping.values():
                # Filter data for the selected borough
                filtered_data = nyc_arrests[
                    nyc_arrests['borough'] == selected_location
                ]
            else:
                # Filter data for the selected precinct
                filtered_data = nyc_arrests[nyc_arrests['ARREST_PRECINCT'] == selected_location]

            # Ensure that filtered data is being returned, otherwise do nothing
            if not filtered_data.empty:
                # Get the top 10 most frequent crimes based on arrests
                arrest_crimes_filtered = (
                    filtered_data.groupby('OFNS_DESC')
                    .size()
                    .reset_index(name='Arrests')
                    .sort_values(by='Arrests', ascending=False)
                    .head(10)
                )

                # Rename for consistency
                arrest_crimes_filtered = arrest_crimes_filtered.rename(columns={'OFNS_DESC': 'Crime Type', 'Arrests': 'Frequency'})

                # If the selected location is an integer, add "Precinct" to the label
                if isinstance(selected_location, int):
                    selected_location = f"Precinct {selected_location}"

                # Create a new pie chart for the filtered borough or precinct
                crime_pie_chart_filtered = create_pie_chart(arrest_crimes_filtered, f"Top 10 Crime Types in {selected_location}")
                return crime_pie_chart_filtered

    # If no region is selected, return the default pie chart
    return create_pie_chart(top_crimes, "Top 10 Crime Types")


# Run the app/dashboard
if __name__ == '__main__':
    server.run()