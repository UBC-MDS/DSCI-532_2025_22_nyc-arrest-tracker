from dash import Output, Input, callback
import altair as alt

from src.data import nyc_arrests, nyc_boroughs, nyc_precinct
from src.utils import filter_data_by_crime_type


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
        geo_df = nyc_precinct.merge(
            arrest_data_grp_precinct_filtered,
            how="left",
            left_on="precinct",
            right_on="ARREST_PRECINCT"
        ).rename(
            columns={"precinct": "Precinct", "counts": "Arrests"}
        )[["Precinct", "Arrests", "geometry"]]
        tooltip_label = 'Precinct'
    else:  # Borough view
        geo_df = nyc_boroughs.merge(
            arrest_data_grp_borough_filtered,
            how="left",
            left_on="name",
            right_on="borough"
        ).rename(
            columns={"borough": "Borough", "counts": "Arrests"}
        )[["Borough", "Arrests", "geometry"]]
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
