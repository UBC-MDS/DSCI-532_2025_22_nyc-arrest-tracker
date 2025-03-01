import altair as alt
import dash_bootstrap_components as dbc
import dash_vega_components as dvc
from dash import Dash, dcc, callback, Input, Output, html, callback_context, State
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

# Get all unique crime types for dropdown
all_crime_types = sorted(nyc_arrests['OFNS_DESC'].unique().tolist())

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


# Calculate min and max dates from the data
min_date = nyc_arrests['ARREST_DATE'].min()  
max_date = nyc_arrests['ARREST_DATE'].max() 


# Sidebar for displaying filters and customization options
sidebar = dbc.Collapse(
    html.Div(
        [
            html.H4("Filters", className="mb-3"),
            dbc.Switch(id="map-toggle", label="Toggle Precincts/Boroughs", value=False, className="mb-3"),
            html.Label("Select Crime Type:"),
            dcc.Dropdown(
                id="crime-type-dropdown",
                options=[{"label": crime, "value": crime} for crime in all_crime_types],
                value=[],
                multi=True,
                placeholder="Select crime types (empty for all)",
                className="mb-3"
            ),

            # Update the DatePickerRange
            html.Label("Select Date Range:"),
            dcc.DatePickerRange(
                id='date-picker-range',
                start_date=min_date,  # Set the start date as the minimum date from the data
                end_date=max_date,    # Set the end date as the maximum date from the data
                display_format='MM-DD',  # Format for the displayed date
                className="mb-3",
                min_date_allowed=min_date,  # Restrict selection to the min_date
                max_date_allowed=max_date  # Restrict selection to the max_date
                
            ),

            


            dbc.Button(
                "Reset All Charts",
                id="reset-button",
                color="primary",
                className="mr-1 mb-3",
                n_clicks=0,
                style={
                    "position": "absolute",  # Keeps the button fixed in place
                    "bottom": "20px",        # Position it at the bottom of the sidebar
                    "width": "80%",          # Give it a fixed width (or adjust as needed)
                    "left": "50%",           # Center the button horizontally
                    "transform": "translateX(-50%)"  # This makes sure it's perfectly centered
                }
            )
        ],
        style={
            "position": "fixed",
            "top": 0,
            "left": 0,  # Always aligned to the left
            "width": "300px",
            "height": "100vh",
            "background-color": "#e6e6e6",
            "padding": "20px",
            "z-index": "1000",  # Keep sidebar above content
            "overflow-y": "auto"  # Allow scrolling if many options
        }
    ),
    id="sidebar",
    is_open=False,  # Start collapsed
)




# Sidebar toggle button
collapse_button = dbc.Button(
    "☰ Additional Filters",
    id="collapse-button",
    style={
        'width': '150px',
        'background-color': 'white',
        'color': 'steelblue',
        'margin-top': 10
    }
)


# Layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("NYPD Arrests Map"), width="auto"),  # Title
        dbc.Col(collapse_button, width="auto"),  # Collapse Button beside it
    ], align="center", className="mb-3"),  # Align items and add margin
    sidebar,
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
                )
            ],
            md=4
        )
    ])
], fluid=True)


# Helper function to filter data by crime types
def filter_data_by_crime_type(data, crime_types):
    """
    Filter data by selected crime types
    
    Parameters:
    data (pd.DataFrame): DataFrame to filter
    crime_types (list): Crime types to filter by
    
    Returns:
    pd.DataFrame: Filtered data
    """
    if not crime_types:  # Empty list means all crimes
        return data
    
    return data[data['OFNS_DESC'].isin(crime_types)]


# Create map chart function
@callback(
    Output('map', 'spec'),
    [Input('map-toggle', 'value'),
     Input('crime-type-dropdown', 'value')]
)
def create_map_chart(toggle_value, crime_types):
    # Filter arrests data based on crime types
    filtered_arrests = nyc_arrests
    if crime_types:  # If crime types are selected
        filtered_arrests = filter_data_by_crime_type(nyc_arrests, crime_types)
    
    # Recalculate aggregated data
    arrest_data_grp_borough_filtered = filtered_arrests.groupby(
        "borough"
    ).size().reset_index(name='counts')
    
    arrest_data_grp_precinct_filtered = filtered_arrests.groupby(
        "ARREST_PRECINCT"
    ).size().reset_index(name='counts')
    
    # Update geo data with filtered counts
    if toggle_value:  # Precinct view
        precinct_geo_filtered = nyc_precinct.merge(
            arrest_data_grp_precinct_filtered,
            how="left",
            left_on="precinct",
            right_on="ARREST_PRECINCT"
        ).rename(
            columns={"precinct": "Precinct", "counts": "Arrests"}
        )[["Precinct", "Arrests", "geometry"]]
        
        precinct_geo_filtered["Arrests"] = precinct_geo_filtered["Arrests"].fillna(0)
        precinct_geo_filtered["geojson"] = precinct_geo_filtered["geometry"].apply(
            lambda x: x.__geo_interface__
        )
        
        geo_df = pd.json_normalize(precinct_geo_filtered["geojson"])
        geo_df["Precinct"] = precinct_geo_filtered["Precinct"]
        geo_df["Arrests"] = precinct_geo_filtered["Arrests"]
        tooltip_label = 'Precinct'
    else:  # Borough view
        borough_geo_filtered = arrest_data_grp_borough_filtered.merge(
            nyc_boroughs,
            how="left",
            left_on="borough",
            right_on="name"
        ).rename(
            columns={"borough": "Borough", "counts": "Arrests"}
        )[["Borough", "Arrests", "geometry"]]
        
        borough_geo_filtered["Arrests"] = borough_geo_filtered["Arrests"].fillna(0)
        borough_geo_filtered["geojson"] = borough_geo_filtered["geometry"].apply(
            lambda x: x.__geo_interface__
        )
        
        geo_df = pd.json_normalize(borough_geo_filtered["geojson"])
        geo_df["Borough"] = borough_geo_filtered["Borough"]
        geo_df["Arrests"] = borough_geo_filtered["Arrests"]
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
        color=alt.Color('Arrests:Q', scale=alt.Scale(scheme='blues')),
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
def filter_data_by_location(selected_location, data):
    """
    Filter the arrest data by the selected borough or precinct.
    
    Parameters:
    selected_location: The selected borough name or precinct number
    data: The dataset to filter (could be already filtered by crime type)
    
    Returns:
    pd.DataFrame: Filtered arrest data or None if no valid data
    """
    if selected_location is None:
        return None
        
    if selected_location in borough_mapping.values():
        # Filter data for the selected borough
        filtered_data = data[data['borough'] == selected_location]
    else:
        # Filter data for the selected precinct
        filtered_data = data[data['ARREST_PRECINCT'] == selected_location]
    
    if filtered_data.empty:
        return None
        
    return filtered_data

# Consolidated callback for all pie charts
@callback(
    [Output('crime-pie-chart', 'figure'),
     Output('gender-pie-chart', 'figure'),
     Output('age-pie-chart', 'figure')],
    [Input('map', 'signalData'),
     Input('crime-type-dropdown', 'value'),
     Input('reset-button', 'n_clicks')]
)
def update_all_pie_charts(clicked_region, crime_types, n_clicks):
    ctx = callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None
    
    # First filter the data by crime types
    filtered_by_crime = nyc_arrests
    
    # Format crime types for display
    if not crime_types:
        crime_type_display = ""
    elif len(crime_types) == 1:
        crime_type_display = f" - {crime_types[0]}"
    else:
        crime_type_display = f" - Selected Crimes ({len(crime_types)})"
    
    # Apply crime type filter
    if crime_types:
        filtered_by_crime = filter_data_by_crime_type(nyc_arrests, crime_types)
    
    # Get selected location from map click
    selected_location, location_label = get_selected_location(clicked_region)
    
    # Apply location filter if a location is selected
    if selected_location is not None:
        filtered_data = filter_data_by_location(selected_location, filtered_by_crime)
        if filtered_data is None or filtered_data.empty:
            # If no data for selected location, just use crime-filtered data
            filtered_data = filtered_by_crime
            location_label_display = ""
        else:
            location_label_display = f" in {location_label}"
    else:
        filtered_data = filtered_by_crime
        location_label_display = ""
    
    # Reset button was clicked - reset location but keep crime type filter
    if triggered_id == "reset-button":
        filtered_data = filtered_by_crime
        location_label_display = ""
    
    # Create crime chart
    if crime_types and len(crime_types) <= 3:
        # When specific crimes are selected and not too many, show distribution among those crimes
        crime_counts = filtered_data.groupby('OFNS_DESC').size().reset_index(name='Arrests')
        crime_counts = crime_counts[crime_counts['OFNS_DESC'].isin(crime_types)]
        crime_title = f"Selected Crime Types{location_label_display}"
    else:
        # Otherwise show top 10
        crime_counts = (
            filtered_data.groupby('OFNS_DESC')
            .size()
            .reset_index(name='Arrests')
            .sort_values(by='Arrests', ascending=False)
            .head(10)
        )
        crime_title = f"Top 10 Crime Types{location_label_display}{crime_type_display}"
    
    updated_crime_chart = create_pie_chart(crime_counts, crime_title)
    
    # Create gender chart
    gender_counts = filtered_data['PERP_SEX'].value_counts()
    gender_counts_filtered = pd.DataFrame({
        'PERP_SEX': gender_counts.index,
        'Arrests': gender_counts.values
    })
    updated_gender_chart = create_pie_chart(
        gender_counts_filtered, 
        f"Arrests by Gender{location_label_display}{crime_type_display}"
    )
    
    # Create age chart
    age_counts = filtered_data['AGE_GROUP'].value_counts()
    age_counts_filtered = pd.DataFrame({
        'AGE_GROUP': age_counts.index,
        'Arrests': age_counts.values
    })
    updated_age_chart = create_pie_chart(
        age_counts_filtered, 
        f"Arrests by Age Group{location_label_display}{crime_type_display}"
    )
    
    return updated_crime_chart, updated_gender_chart, updated_age_chart

@app.callback(
    Output("sidebar", "is_open"),
    Input("collapse-button", "n_clicks"),
    State("sidebar", "is_open"),
)
def toggle_sidebar(n, is_open):
    # Toggle sidebar visiblity
    return not is_open if n else is_open

# Run the app/dashboard
if __name__ == '__main__':
    server.run()
