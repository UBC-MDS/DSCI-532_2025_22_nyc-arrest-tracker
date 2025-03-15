import plotly.express as px
import pandas as pd

# Filter data by date range
def filter_data_by_date_range(data, start_date, end_date):
    """
    Filter data by selected date range - vectorized version

    Parameters:
    data (pd.DataFrame): DataFrame to filter
    start_date (str): Start date of the range
    end_date (str): End date of the range

    Returns:
    pd.DataFrame: Filtered data
    """
    if start_date and end_date:
        # Single boolean mask operation instead of chained filtering
        date_mask = (data['ARREST_DATE'] >= start_date) & (data['ARREST_DATE'] <= end_date)
        return data[date_mask]
    return data


# Filter data by crime types
def filter_data_by_crime_type(data, crime_types):
    """
    Filter data by selected crime types - vectorized version

    Parameters:
    data (pd.DataFrame): DataFrame to filter
    crime_types (list): Crime types to filter by

    Returns:
    pd.DataFrame: Filtered data
    """
    if not crime_types:  # Empty list means all crimes
        return data

    crime_mask = data['OFNS_DESC'].isin(crime_types)
    return data[crime_mask]

def filter_data(data, start_date=None, end_date=None, crime_types=None, selected_location=None):
    """
    Combined filter function to apply multiple filters in one pass

    Parameters:
    data (pd.DataFrame): DataFrame to filter
    start_date (str): Start date of the range 
    end_date (str): End date of the range
    crime_types (list): Crime types to filter by
    selected_location: The selected borough or precinct

    Returns:
    pd.DataFrame: Filtered data
    """
    # Start with all rows selected
    mask = pd.Series(True, index=data.index)
    
    # Date filter
    if start_date and end_date:
        date_mask = (data['ARREST_DATE'] >= start_date) & (data['ARREST_DATE'] <= end_date)
        mask = mask & date_mask
    
    # Crime type filter
    if crime_types:
        crime_mask = data['OFNS_DESC'].isin(crime_types)
        mask = mask & crime_mask
    
    # Location filter
    if selected_location:
        if selected_location in ['Bronx', 'Staten Island', 'Brooklyn', 'Manhattan', 'Queens']:
            # Filter by borough
            location_mask = (data['borough'] == selected_location)
        else:
            # Filter by precinct
            location_mask = (data['ARREST_PRECINCT'] == selected_location)
        mask = mask & location_mask
    
    return data[mask]


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
    if selected_location is None:
        return None

    borough_mapping = {
        'B': 'Bronx',
        'S': 'Staten Island',
        'K': 'Brooklyn',
        'M': 'Manhattan',
        'Q': 'Queens'
    }

    
    if selected_location in borough_mapping.values():
        filtered_data = data[data['borough'] == selected_location]
    else:
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
    crime_colors = [
    '#1D3557',  
    '#E63946',  
    '#FFD700',  
    '#A8DADC',  
    '#F1FAEE',  
    '#D62828',  
    '#6A994E',  
    '#4A5859',  
    '#FF9F1C',  
    '#03045E',  
    '#9D0208',  
    '#7B2CBF',  
    '#FB8500',  
    '#2A9D8F',  
    '#264653'   
]

    gender_colors = ['#1D3557', '#E63946', '#FFD700']

    age_colors = [
        '#1D3557',  # Dark blue
        '#E63946',  # Red
        '#457B9D',  # Medium blue
        '#A8DADC',  # Light blue
        '#FFD700',  # Gold
        '#003049'   # Dark navy
    ]

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
        textposition='inside'
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
        uniformtext_minsize=12,
        uniformtext_mode='hide',
        height=220,  
        margin=dict(l=10, r=10, t=50, b=10),  
        title=dict(
            text=title,
            font=dict(size=14),  
            x=0.5, 
            y=0.90  
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
    pie_chart.update_traces(
        textinfo="none", hoverinfo="skip", hovertemplate=None
    )

    # Remove legend and add no data message to pie chart
    pie_chart.update_layout(
        showlegend=False,
        height=220,
        margin=dict(l=10, r=10, t=50, b=10),
        annotations=[dict(
            text="No Data",
            x=0.5,
            y=0.5,
            showarrow=False
        )],
        title=dict(
            text="No Data",
            font=dict(size=14),
            x=0.5,
            y=0.90
        )
    )

    return pie_chart



def create_bar_chart(data, title):
    """
    Create a bar chart for top crimes.

    Parameters:
    data (pd.DataFrame): DataFrame with at least two columns - crime type and count
    title (str): Title for the bar chart

    Returns:
    plotly.graph_objects.Figure: A bar chart figure
    """
    # Take only top 5 crimes
    if len(data) > 5:
        data = data.head(5)
    
    # Instead of different colors per bar, use a single NYPD blue color
    # for a more professional look
    bar_color = '#1D3557'  # Dark navy blue (NYPD uniform)
    
    # Get the column names - one will be 'Arrests', the other is the category name
    columns = list(data.columns)
    name_col = [col for col in columns if col != 'Arrests'][0]
    
    # Create horizontal bar chart with consistent coloring
    bar_chart = px.bar(
        data,
        y=name_col,  # Use crime type as y-axis for horizontal bars
        x='Arrests',
        title=title,
        labels={'Arrests': 'Number of Arrests'},
        orientation='h',  # Horizontal orientation
        color_discrete_sequence=[bar_color]  # Use single color for all bars
    )
    
    # Customize hover information
    bar_chart.update_traces(
        hovertemplate='<b>%{y}</b><br>Arrests: %{x:,}<extra></extra>'
    )
    
    # Improve layout and styling
    bar_chart.update_layout(
        dragmode=False,
        showlegend=False,
        height=240,
        margin=dict(l=10, r=10, t=30, b=10),
        title=dict(
            text=title,
            font=dict(size=14),
            x=0.5,
            y=0.95
        ),
        plot_bgcolor='white',
        yaxis=dict(
            title='',
            automargin=True,
            tickfont=dict(size=11),  # Smaller text for crime names
            fixedrange=True
        ),
        xaxis=dict(
            title='Number of Arrests',
            tickfont=dict(size=11),
            showgrid=True,
            gridcolor='lightgray',
            gridwidth=0.5,
            fixedrange=True
        )
    )

    return bar_chart


def create_empty_bar_chart():
    """Create an empty bar chart with a message."""

    # Create empty dataframe
    empty_df = pd.DataFrame({"Category": [], "Value": []})
    fig = px.bar(empty_df, x='Value', y='Category')

    fig.update_layout(
        title="No Data Available",
        dragmode=False,
        annotations=[
            dict(
                text="No data available for the selected filters",
                showarrow=False,
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5
            )
        ],
        yaxis=dict(
            fixedrange=True
        ),
        xaxis=dict(
            fixedrange=True
        ),
        height=240
    )
    return fig
