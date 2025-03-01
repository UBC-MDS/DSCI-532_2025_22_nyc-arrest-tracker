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

# Gender and Age data preparation
# Create default gender data for all arrests (citywide)
gender_data = pd.DataFrame({
    'PERP_SEX': nyc_arrests['PERP_SEX'].value_counts().index,
    'Arrests': nyc_arrests['PERP_SEX'].value_counts().values
})

# Create default age data for all arrests (citywide)
age_data = pd.DataFrame({
    'AGE_GROUP': nyc_arrests['AGE_GROUP'].value_counts().index,
    'Arrests': nyc_arrests['AGE_GROUP'].value_counts().values
})

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

# Color schemes
crime_colors = ['#E63946', '#1D3557', '#F1FAEE', '#457B9D', '#A8DADC',
          '#F1FAEE', '#1D3557', '#E63946', '#457B9D', '#A8DADC']

gender_colors = ['#1D3557', '#E63946', '#457B9D']  # Colors for M, F, U/Other
age_colors = ['#1D3557', '#E63946', '#457B9D', '#A8DADC', '#90A955', '#F77F00']  # Colors for different age groups

def create_pie_chart(data, title):
    """
    Create a pie chart with consistent styling.
    
    Parameters:
    data (pd.DataFrame): DataFrame with at least two columns - one for names and one for values
    title (str): Title for the pie chart
    
    Returns:
    plotly.graph_objects.Figure: A pie chart figure
    """
    # Get the column names - one will be 'Arrests', the other is the category name
    columns = list(data.columns)
    
    # The name column is the one that's not 'Arrests'
    name_col = [col for col in columns if col != 'Arrests'][0]
    
    # Select the appropriate color scheme based on the category
    if name_col == 'OFNS_DESC':
        color_sequence = crime_colors
    elif name_col == 'PERP_SEX':
        color_sequence = gender_colors
    elif name_col == 'AGE_GROUP':
        color_sequence = age_colors
    else:
        color_sequence = crime_colors  # Default
    
    pie_chart = px.pie(
        data,
        names=name_col, 
        values='Arrests',   
        title=title,
        labels={'Arrests': 'Number of Arrests'},
        color=name_col,  
        color_discrete_sequence=color_sequence 
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


# Create the initial pie charts
crime_pie_data = top_crimes.rename(columns={'Crime Type': 'OFNS_DESC', 'Frequency': 'Arrests'})
crime_pie_chart = create_pie_chart(crime_pie_data, "Top 10 Crime Types")
gender_pie_chart = create_pie_chart(gender_data, "Arrests by Gender")
age_pie_chart = create_pie_chart(age_data, "Arrests by Age Group")

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
        # Column for the pie charts (placed right)
        dbc.Col(
            [
                dcc.Graph(
                    id='crime-pie-chart',
                    figure=crime_pie_chart
                ),
                dcc.Graph(
                    id='gender-pie-chart',
                    figure=gender_pie_chart
                ),
                dcc.Graph(
                    id='age-pie-chart',
                    figure=age_pie_chart
                ),
                # Reset button
                dbc.Button("Reset All Charts", id="reset-button", color="primary", className="mr-1 mb-3", n_clicks=0)
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

# Helper function to get the selected location from clicked_region
def get_selected_location(clicked_region):
    """
    Extract the selected location (borough or precinct) from the clicked region data.
    
    Parameters:
    clicked_region (dict): The signal data from the map click
    
    Returns:
    tuple: (selected_location, location_label) or (None, None) if no valid selection
    """
    if not clicked_region or 'select_region' not in clicked_region:
        return None, None
        
    # Check if the clicked region is a borough or precinct
    selected_location = clicked_region['select_region'].get('Borough', None)
    
    if not selected_location:
        selected_location = clicked_region['select_region'].get('Precinct', None)
    
    # If selected_location is a list, get the first element
    if isinstance(selected_location, list) and selected_location:
        selected_location = selected_location[0]
    
    # Format the location label (add "Precinct" prefix for precinct numbers)
    location_label = selected_location
    if isinstance(selected_location, int):
        location_label = f"Precinct {selected_location}"
        
    return selected_location, location_label

# Helper function to filter data by location
def filter_data_by_location(selected_location):
    """
    Filter the arrest data by the selected borough or precinct.
    
    Parameters:
    selected_location: The selected borough name or precinct number
    
    Returns:
    pd.DataFrame: Filtered arrest data or None if no valid data
    """
    if selected_location is None:
        return None
        
    if selected_location in borough_mapping.values():
        # Filter data for the selected borough
        filtered_data = nyc_arrests[nyc_arrests['borough'] == selected_location]
    else:
        # Filter data for the selected precinct
        filtered_data = nyc_arrests[nyc_arrests['ARREST_PRECINCT'] == selected_location]
    
    if filtered_data.empty:
        return None
        
    return filtered_data

# Consolidated callback for all pie charts
@callback(
    [Output('crime-pie-chart', 'figure'),
     Output('gender-pie-chart', 'figure'),
     Output('age-pie-chart', 'figure')],
    [Input('map', 'signalData'),
     Input('reset-button', 'n_clicks')]
)
def update_all_pie_charts(clicked_region, n_clicks):
    # Initialize with default charts
    crime_chart = create_pie_chart(
        top_crimes.rename(columns={'Crime Type': 'OFNS_DESC', 'Frequency': 'Arrests'}), 
        "Top 10 Crime Types"
    )
    gender_chart = create_pie_chart(gender_data, "Arrests by Gender")
    age_chart = create_pie_chart(age_data, "Arrests by Age Group")
    
    # Reset button was clicked - return all default charts
    if callback_context.triggered and callback_context.triggered[0]['prop_id'].startswith('reset-button'):
        return crime_chart, gender_chart, age_chart
    
    # Get selected location from map click
    selected_location, location_label = get_selected_location(clicked_region)
    if selected_location is None:
        return crime_chart, gender_chart, age_chart
    
    # Filter data by selected location
    filtered_data = filter_data_by_location(selected_location)
    if filtered_data is None:
        return crime_chart, gender_chart, age_chart
    
    # Create updated crime chart
    crime_counts = (
        filtered_data.groupby('OFNS_DESC')
        .size()
        .reset_index(name='Arrests')
        .sort_values(by='Arrests', ascending=False)
        .head(10)
    )
    updated_crime_chart = create_pie_chart(
        crime_counts, 
        f"Top 10 Crime Types in {location_label}"
    )
    
    # Create updated gender chart
    gender_counts = filtered_data['PERP_SEX'].value_counts()
    gender_counts_filtered = pd.DataFrame({
        'PERP_SEX': gender_counts.index,
        'Arrests': gender_counts.values
    })
    updated_gender_chart = create_pie_chart(
        gender_counts_filtered, 
        f"Arrests by Gender in {location_label}"
    )
    
    # Create updated age chart
    age_counts = filtered_data['AGE_GROUP'].value_counts()
    age_counts_filtered = pd.DataFrame({
        'AGE_GROUP': age_counts.index,
        'Arrests': age_counts.values
    })
    updated_age_chart = create_pie_chart(
        age_counts_filtered, 
        f"Arrests by Age Group in {location_label}"
    )
    
    return updated_crime_chart, updated_gender_chart, updated_age_chart

# Run the app/dashboard
if __name__ == '__main__':
    server.run()