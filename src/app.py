import dash_bootstrap_components as dbc
from dash import Dash, dcc, callback, Input, Output, html
import geopandas as gpd
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, callback, Input, Output, html 

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


# Merge the arrest data with GeoJSON data
arrest_data_geo = nyc_boroughs.merge(
    nyc_arrests.groupby('borough').size().reset_index(name='Arrests'),
    how="left",
    left_on="name",
    right_on="borough"
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




# Create a Plotly choropleth map to represent the arrests per borough
map_chart = px.choropleth(
    arrest_data_geo,
    geojson=arrest_data_geo.geometry.__geo_interface__,
    locations=arrest_data_geo.index,
    color='Arrests',
    hover_name='name',
    hover_data=["Arrests"],
    color_continuous_scale="Blues",
    title="NYC Borough Arrests"
)

# Update layout for the map
map_chart.update_geos(fitbounds="locations", visible=False)
map_chart.update_layout(
    geo=dict(showcoastlines=True, coastlinecolor="Black"),
    title="NYC Borough Arrests"
)






# Group the data by the more general offense description (OFNS_DESC)
arrest_crimes = nyc_arrests.groupby('OFNS_DESC').size().reset_index(name='Arrests')

# Get the top 10 most frequent crimes based on arrests
top_crimes = arrest_crimes.sort_values(by='Arrests', ascending=False).head(10)

# Define consistent color scheme for the pie chart
colors = ['#E63946', '#1D3557', '#F1FAEE', '#457B9D', '#A8DADC', '#F1FAEE', '#1D3557', '#E63946', '#457B9D', '#A8DADC']

# Create the pie chart for the top 10 crimes by arrests
def create_pie_chart(data, title):
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








# Initialize the app
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Layout 
app.layout = dbc.Container([
    html.H1("NYPD Arrests Map"),
    dbc.Row([
        # Column for the map
        dbc.Col(
            [
                dcc.Graph(id="map", figure=map_chart)  
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



# Callback 
@app.callback(
    Output('crime-pie-chart', 'figure'),
    Input('map', 'clickData'),  # Listen for clicks on the Plotly map
    Input('reset-button', 'n_clicks')  # Listen for button clicks to reset
)
def update_pie_chart(map_data, n_clicks):
    # Check if the reset button is clicked
    if n_clicks > 0:
        return create_pie_chart(top_crimes, "Top 10 Crime Types")  # Reset to default chart

    if map_data is None:  # If nothing is selected, show top crimes for all of NYC
        return crime_pie_chart
    else:
        # Get selected borough from click event on the map
        selected_borough = map_data['points'][0]['hovertext']
        
        # Filter data for the selected borough
        filtered_data = nyc_arrests[nyc_arrests['borough'] == selected_borough]
        arrest_crimes_filtered = filtered_data.groupby('OFNS_DESC').size().reset_index(name='Arrests')

        # Get the top 10 most frequent crimes based on arrests
        top_crimes_filtered = arrest_crimes_filtered.sort_values(by='Arrests', ascending=False).head(10)

        # Create a new pie chart for the filtered borough
        crime_pie_chart_filtered = create_pie_chart(top_crimes_filtered, f"Top 10 Crime Types in {selected_borough}")

        # Return the updated pie chart
        return crime_pie_chart_filtered


if __name__ == '__main__':
    app.run_server(debug=True)  