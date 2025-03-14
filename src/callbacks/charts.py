from dash import Output, Input, State, callback, callback_context
import pandas as pd

from src.data import nyc_arrests
from src.utils import (
    filter_data,
    get_selected_location,
    filter_data_by_location,
    create_pie_chart,
    create_bar_chart,
    filter_data_by_date_range,
    filter_data_by_crime_type,
    create_empty_pie_chart, 
    create_empty_bar_chart
)

@callback(
    [Output('crime-bar-chart', 'figure'),
     Output('gender-pie-chart', 'figure'),
     Output('age-pie-chart', 'figure')],
    [Input('map', 'signalData'),
     Input('apply-button', 'n_clicks'),
     Input('reset-button', 'n_clicks')],
    [State('date-picker-range', 'start_date'),
     State('date-picker-range', 'end_date'),
     State('crime-type-dropdown', 'value')]
)
def update_all_pie_charts(
    clicked_region, apply_clicks, reset_clicks,
    start_date, end_date, crime_types
):
    ctx = callback_context
    # Get the ID of the component that triggered the callback
    triggered_id = None
    if ctx.triggered:
        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    # First get unfiltered data
    filtered_by_crime = nyc_arrests

    # Format crime types for display
    if not crime_types:
        crime_type_display = ""
    elif len(crime_types) == 1:
        crime_type_display = f" - {crime_types[0]}"
    else:
        crime_type_display = f" - Selected Crimes ({len(crime_types)})"

    # Apply filter ONLY if the apply button was clicked
    if triggered_id == "apply-button" or triggered_id == "map":
        # Use vectorized filtering with the combined filter function
        filtered_by_crime = filter_data(
            nyc_arrests, 
            start_date=start_date, 
            end_date=end_date,
            crime_types=crime_types if crime_types else None
        )

    # Reset button was clicked - reset to original unfiltered data
    if triggered_id == "reset-button":
        filtered_by_crime = nyc_arrests
        location_label_display = ""
        crime_type_display = ""

    # Get selected location from map click
    selected_location, location_label = get_selected_location(clicked_region)

    # Apply location filter if a location is selected
    if selected_location is not None:
        filtered_data = filter_data_by_location(
            selected_location,
            filtered_by_crime
        )
        if filtered_data is None or filtered_data.empty:
            # If no data for selected location, just use crime-filtered data
            filtered_data = filtered_by_crime
            location_label_display = ""
        else:
            location_label_display = f" in {location_label}"
    else:
        filtered_data = filtered_by_crime
        location_label_display = ""

    if filtered_data.empty:
        return (
            create_empty_bar_chart(),
            create_empty_pie_chart(),
            create_empty_pie_chart()
        )

    # For crime chart - obtain counts in one operation
    crime_counts = filtered_data['OFNS_DESC'].value_counts().reset_index()
    crime_counts.columns = ['OFNS_DESC', 'Arrests']

    # Create appropriate crime chart based on filters
    if (triggered_id == "apply-button" and crime_types and
            len(crime_types) <= 3):
        # Filter the pre-computed counts instead of filtering the DataFrame again
        crime_counts = crime_counts[crime_counts['OFNS_DESC'].isin(crime_types)]
        crime_title = (
            f"Selected Crime Types{location_label_display}{crime_type_display}"
        )
    else:
        # Sort and get top 5 without additional filtering
        crime_counts = crime_counts.sort_values(by='Arrests', ascending=False).head(5)
        crime_title = (
            f"Top 5 Crime Types{location_label_display}"
            f"{crime_type_display}"
        )

    # Create crime chart with the pre-computed data
    updated_crime_chart = create_bar_chart(crime_counts, crime_title)

    # Gender aggregation - convert to proper DataFrame format in one step
    gender_counts = filtered_data['PERP_SEX'].value_counts().reset_index()
    gender_counts.columns = ['PERP_SEX', 'Arrests']
    
    # Age aggregation - convert to proper DataFrame format in one step
    age_counts = filtered_data['AGE_GROUP'].value_counts().reset_index()
    age_counts.columns = ['AGE_GROUP', 'Arrests']

    # Create charts with pre-computed data
    updated_gender_chart = create_pie_chart(
        gender_counts,
        f"Arrests by Gender{location_label_display}{crime_type_display}"
    )

    updated_age_chart = create_pie_chart(
        age_counts,
        f"Arrests by Age Group{location_label_display}{crime_type_display}"
    )

    return updated_crime_chart, updated_gender_chart, updated_age_chart