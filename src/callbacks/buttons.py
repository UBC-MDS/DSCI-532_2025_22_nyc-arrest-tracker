from dash import Output, Input, State, callback


@callback(
    Output("sidebar", "is_open"),
    Input("collapse-button", "n_clicks"),
    State("sidebar", "is_open"),
)
def toggle_sidebar(n, is_open):
    # Toggle sidebar visiblity
    return not is_open if n else is_open
