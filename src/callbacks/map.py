from dash import Output, Input, callback, State, callback_context
import altair as alt
import pandas as pd

from src.data import nyc_arrests, nyc_boroughs, nyc_precinct
from src.utils import filter_data

@callback(
    Output('map', 'spec'),
    [Input('map-toggle', 'value'),
     Input('apply-button', 'n_clicks'),
     Input('reset-button', 'n_clicks')],
    [State('date-picker-range', 'start_date'),
     State('date-picker-range', 'end_date'),
     State('crime-type-dropdown', 'value')]
)
def create_map_chart(
    toggle_value, apply_clicks, reset_clicks, start_date, end_date, crime_types
):

    # Start with unfiltered data
    filtered_arrests = nyc_arrests

    # Check which input triggered the callback
    ctx = callback_context
    if ctx.triggered:
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

        # Only apply filter if the apply button was clicked
        if trigger_id == 'apply-button':
            filtered_arrests = filter_data(
                nyc_arrests,
                start_date=start_date,
                end_date=end_date,
                crime_types=crime_types if crime_types else None
            )

        if trigger_id == 'reset-button':
            filtered_arrests = nyc_arrests

    if toggle_value:  # Precinct view
        arrest_data_grp_precinct_filtered = (
            filtered_arrests
            .groupby('ARREST_PRECINCT', as_index=False)
            .agg(counts=('ARREST_PRECINCT', 'size'))
        )
        
        geo_df = nyc_precinct.merge(
            arrest_data_grp_precinct_filtered,
            how="left",
            left_on="precinct",
            right_on="ARREST_PRECINCT",
            copy=False
        ).rename(
            columns={"precinct": "Precinct", "counts": "Arrests"}
        )[["Precinct", "Arrests", "geometry"]]
        
        # Handle NaN values in one vectorized operation
        geo_df["Arrests"] = geo_df["Arrests"].fillna(0).astype(int)
        tooltip_label = 'Precinct'
        map_title = "NYC Precincts"
        
    else:  # Borough view
        arrest_data_grp_borough_filtered = (
            filtered_arrests
            .groupby('borough', as_index=False)
            .agg(counts=('borough', 'size'))
        )
        
        geo_df = nyc_boroughs.merge(
            arrest_data_grp_borough_filtered,
            how="left",
            left_on="name",
            right_on="borough",
            copy=False
        ).rename(
            columns={"name": "Borough", "counts": "Arrests"}
        )[["Borough", "Arrests", "geometry"]]
        
        # Handle NaN values in one vectorized operation
        geo_df["Arrests"] = geo_df["Arrests"].fillna(0).astype(int)
        tooltip_label = 'Borough'
        map_title = "NYC Boroughs"

    select_region = alt.selection_point(
        fields=[tooltip_label],
        name='select_region',
        toggle=False
    )

    # Set opacity based on selection, grey out regions with no data
    map_opacity = alt.condition(
        (select_region & (alt.datum.Arrests > 0)),
        alt.value(0.9),
        alt.value(0.3) if alt.datum.Arrests > 0 else alt.value(0.1)
    )

    # Create map
    map_chart = alt.Chart(
        geo_df,
        width=600,
        height=500,
        title=map_title
    ).mark_geoshape(
        stroke='grey'
    ).project(
        'albersUsa'
    ).encode(
        color=alt.Color('Arrests:Q', scale=alt.Scale(scheme='blues')),
        tooltip=[tooltip_label, alt.Tooltip('Arrests', format=',')],
        opacity=map_opacity
    ).add_params(
        select_region
    ).configure_legend(
        orient="left",
        padding=10,
        offset=5,
        titleFont='Open Sans',
        titleFontWeight='normal',
        titleFontStyle='normal',
        titleColor='rgb(42, 63, 95)',
        labelFont='Open Sans',
        labelColor='rgb(42, 63, 95)'
    ).configure_title(
        font='Open Sans',
        fontSize=14,
        fontWeight='normal',
        fontStyle='normal',
        color='rgb(42, 63, 95)'
    ).to_dict()

    return map_chart
