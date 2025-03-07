from dash import Output, Input, callback, callback_context
import pandas as pd

from src.data import nyc_arrests
from src.utils import (
    filter_data_by_crime_type,
    get_selected_location,
    filter_data_by_location,
    create_pie_chart
)


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

    # Get the ID of the component that triggered the callback
    if ctx.triggered:
        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    else:
        triggered_id = None

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

    # Reset button was clicked - reset location but keep crime type filter
    if triggered_id == "reset-button":
        filtered_data = filtered_by_crime
        location_label_display = ""

    # Create crime chart
    if crime_types and len(crime_types) <= 3:
        # When specific crimes are selected and not too many,
        # show distribution among those crimes
        crime_counts = (filtered_data
                        .groupby('OFNS_DESC')
                        .size()
                        .reset_index(name='Arrests'))
        crime_counts = crime_counts[
            crime_counts['OFNS_DESC'].isin(crime_types)
        ]
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
        crime_title = (
            f"Top 10 Crime Types{location_label_display}"
            f"{crime_type_display}"
        )

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
