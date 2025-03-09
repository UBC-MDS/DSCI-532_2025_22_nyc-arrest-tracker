import plotly.express as px
import pandas as pd


# Helper function to filter data by date range
def filter_data_by_date_range(data, start_date, end_date):
    """
    Filter data by selected date range

    Parameters:
    data (pd.DataFrame): DataFrame to filter
    start_date (str): Start date of the range
    end_date (str): End date of the range

    Returns:
    pd.DataFrame: Filtered data
    """
    if start_date and end_date:
        return data[
            (data['ARREST_DATE'] >= start_date) &
            (data['ARREST_DATE'] <= end_date)
        ]
    return data


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


# Helper function to get the selected location from clicked_region
def get_selected_location(clicked_region):
    """
    Extract the selected location (borough or precinct) from the clicked
    region data.

    Parameters:
    clicked_region (dict): The signal data from the map click

    Returns:
    tuple: (selected_location, location_label) or (None, None) if no valid
    selection
    """
    if not clicked_region or 'select_region' not in clicked_region:
        return None, None

    # Check if the clicked region is a borough or precinct
    selected_location = clicked_region['select_region'].get('Borough', None)

    if not selected_location:
        selected_location = clicked_region['select_region'].get(
            'Precinct', None
        )

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

    borough_mapping = {
        'B': 'Bronx',
        'S': 'Staten Island',
        'K': 'Brooklyn',
        'M': 'Manhattan',
        'Q': 'Queens'
    }
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


def create_pie_chart(data, title):
    """
    Create a pie chart with consistent styling.

    Parameters:
    data (pd.DataFrame): DataFrame with at least two columns - one for names
        and one for values
    title (str): Title for the pie chart

    Returns:
    plotly.graph_objects.Figure: A pie chart figure
    """

    # Color schemes
    crime_colors = ['#E63946', '#1D3557', '#F1FAEE', '#457B9D', '#A8DADC',
                    '#F1FAEE', '#1D3557', '#E63946', '#457B9D', '#A8DADC']

    # Colors for M, F, U/Other
    gender_colors = ['#1D3557', '#E63946', '#457B9D']

    # Colors for age groups
    age_colors = ['#1D3557', '#E63946', '#457B9D',
                  '#A8DADC', '#90A955', '#F77F00']

    # Get the column names - one will be 'Arrests',
    # the other is the category name
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
        hovertemplate=(
            '<b>%{label}</b><br>Arrests: %{value}<br>'
            '%{percent:.2%} of Total<extra></extra>'
        ),
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
        ),
        
        height=200,  
        margin=dict(l=10, r=10, t=30, b=10),  
        title=dict(
            text=title,
            font=dict(size=14),  
            x=0.5, 
            y=0.95  
        )
    )
    return pie_chart


def create_empty_pie_chart():
    """
    Creates a placeholder pie chart when no data is present.

    Returns:
    plotly.express.Figure: A blank pie chart
    """

    # Create empty dataframe
    empty_df = pd.DataFrame({"Category": ["No Data"], "Value": [1]})

    # Create pie chart from empty df
    pie_chart = px.pie(
        empty_df,
        names="Category",
        values='Value',
        title="No Data",
        color_discrete_sequence=["lightgray"]
    )

    # Hide labels and percentage values
    pie_chart.update_traces(textinfo="none", hoverinfo="none")

    # Remove legend and add no data message to pie chart
    pie_chart.update_layout(
        showlegend=False,
        annotations=[dict(
            text="No Data",
            x=0.5,
            y=0.5,
            showarrow=False
        )]
    )

    return pie_chart
