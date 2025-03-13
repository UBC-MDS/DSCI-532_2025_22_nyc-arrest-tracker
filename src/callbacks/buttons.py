from dash import Output, Input, State, callback, callback_context
import dash
from src.data import min_date, max_date

@callback(
    Output("sidebar", "is_open"),
    Input("collapse-button", "n_clicks"),
    State("sidebar", "is_open"),
)
def toggle_sidebar(n, is_open):
    # Toggle sidebar visiblity
    return not is_open if n else is_open

@callback(
    Output('crime-type-dropdown', 'value'),
    Input('reset-button', 'n_clicks')
)
def reset_crime_dropdown(n_clicks):
    ctx = callback_context
    if not ctx.triggered or ctx.triggered[0]['prop_id'] != 'reset-button.n_clicks':
        return dash.no_update
    
    return []

@callback(
    [Output('date-picker-range', 'start_date'),
     Output('date-picker-range', 'end_date')],
    Input('reset-button', 'n_clicks'),
    prevent_initial_call=True
)
def reset_date_range(n_clicks):
    ctx = callback_context
    if not ctx.triggered or ctx.triggered[0]['prop_id'] != 'reset-button.n_clicks':
        return dash.no_update, dash.no_update
    
    return min_date, max_date

@callback(
    Output("footer-collapse", "is_open"),
    Input("footer-toggle-button", "n_clicks"),
    State("footer-collapse", "is_open"),
)
def toggle_footer(n, is_open):
    if n:
        return not is_open
    return is_open

@callback(
    Output("footer-toggle-button", "children"),
    Input("footer-collapse", "is_open"),
)
def update_footer_button_text(is_open):
    if is_open:
        return "About ▲" 
    return "About ▼" 