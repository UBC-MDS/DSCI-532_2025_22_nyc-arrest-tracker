from dash import dcc, html
import dash_bootstrap_components as dbc

from src.data import all_crime_types, min_date, max_date

# Dropdown for selecting crime types
crime_type_dropdown = dcc.Dropdown(
    id="crime-type-dropdown",
    options=[
        {"label": crime, "value": crime} for crime in all_crime_types
    ],
    value=[],
    multi=True,
    placeholder="Select crime types (empty for all)",
    className="mb-3",    
    style={
        "width": "100%"
    },
    # optionHeight=55,
)

# Toggle switch for displaying precincts or boroughs
map_switch = dbc.Switch(
    id="map-toggle",
    label="Toggle Precincts/Boroughs",
    value=False,
    className="mb-3"
)

# Date range picker
date_filter = dcc.DatePickerRange(
    id='date-picker-range',
    start_date=min_date,  # Set the start date as the minimum date
    end_date=max_date,    # Set the end date as the maximum date
    display_format='MM-DD',  # Format for the displayed date
    className="mb-3",
    min_date_allowed=min_date,  # Restrict selection to the min_date
    max_date_allowed=max_date,  # Restrict selection to the max_date
    style={
        "transform": "scale(0.75)",
        "transform-origin": "top left",
        "white-space": "nowrap"
    }
)

# Sidebar toggle button
collapse_button = dbc.Col(
    dbc.Button(
        "☰ Filters",
        id="collapse-button",
        n_clicks=0,  # Ensure this is explicitly set
        style={
            'width': '150px',
            'background-color': 'white',
            'color': 'steelblue',
            'margin-top': 10
        }
    ),
    width="auto",
    style={
        "position": "absolute",
        "top": "20px",
        "right": "20px",
        "z-index": "1050"
    }
)

# Apply button
apply_button = dbc.Button(
    "Apply",
    id="apply-button",
    color="success",
    className="mb-3",
    n_clicks=0,
    style={
        "position": "absolute",  
        "bottom": "70px",        
        "width": "80%",          
        "left": "50%",           
        "transform": "translateX(-50%)"
    }
)

# Reset button
reset_button = dbc.Button(
    "Reset",
    id="reset-button",
    color="primary",
    className="mr-1 mb-3",
    n_clicks=0,
    style={
        "position": "absolute",  # Keeps the button fixed in place
        "bottom": "20px",        # Position it at the bottom of the sidebar
        "width": "80%",          # Give it a fixed width (or adjust as needed)
        "left": "50%",           # Center the button horizontally
        "transform": "translateX(-50%)"  # This makes sure it's centered
    }
)

# Sidebar for displaying filters and customization options
sidebar = dbc.Collapse(
    html.Div(
        [
            html.H4("Filters", className="mb-3"),
            map_switch,
            html.Label("Select Crime Type:"),
            crime_type_dropdown,

            # Update the DatePickerRange
            html.Label("Select Date Range:"),
            date_filter,
            apply_button,
            reset_button
        ],
        style={
            "position": "fixed",
            "top": 0,
            "left": 0,  # Always aligned to the left
            "width": "375px",
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

footer_toggle_button = dbc.Col(
    dbc.Button(
        "About ▼",
        id="footer-toggle-button",
        color="light",
        size="sm",
        style={
            'width': '120px',
            'background-color': 'steelblue',
            'color': 'white',
            'margin-top': 10
        }
    ),
    width="auto",
    style={
        "position": "absolute",
        "right": "20px",
    }
)

# Footer description
footer_desc = html.P(
    '''
    This dashboard visualizes arrest data from the New York
    Police Department. It is made for policy makers to
    understand the distribution of arrests across New York
    City.
    ''',
    style={
        "font-size": "12px",
        'width': '50%',
        'margin-left': '0px',
        'color': 'black'
    }
)

# Footer creators
footer_creators = html.P(
    "Creators: Michael Gelfand, Michael Hewlett, Hala Arar",
    style={
        "font-size": "12px",
        'color': 'black'
    }
)

# GitHub repository link
github_link = html.A(
    "GitHub Repository",
    href="https://github.com/UBC-MDS/DSCI-532_2025_22_nyc-arrest-tracker",
    target="_blank",
    style={
        "font-size": "12px",
        'color': '#00BFFF'
    }
)

# Last updated date
last_update_date = html.P(
    "Last updated on March 9th, 2025",
    style={
        "font-size": "12px",
        'color': 'black'
    }
)

footer_content = dbc.Collapse(
    dbc.Card(
        dbc.CardBody([
            footer_desc,
            footer_creators,
            github_link,
            last_update_date
        ]),
        className="mt-2",
        style={'border-radius': '5px'}
    ),
    id="footer-collapse",
    is_open=False
)

# Title
title_comp = html.H1(
    'NYPD Arrests Tracker',
    style={
        'backgroundColor': 'steelblue',
        'padding': 10,
        'color': 'white',
        'margin-top': 10,
        'margin-bottom': 10,
        'text-align': 'center',
        'font-size': '48px',
        'border-radius': 3,
    }
)
