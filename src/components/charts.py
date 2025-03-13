from dash import dcc

from src.data import crime_pie_data, gender_data, age_data
from src.utils import create_pie_chart, create_bar_chart

# Crime frequency pie chart
crime_bar_chart = dcc.Loading(
    children=[dcc.Graph(
        id='crime-bar-chart',
        config={'displayModeBar': False},
        figure=create_bar_chart(crime_pie_data.head(5), "Top 5 Crime Types")
    )]
)

# Gender distribution pie chart
gender_pie_chart = dcc.Loading(
    children=[dcc.Graph(
        id='gender-pie-chart',
        config={'displayModeBar': False},
        figure=create_pie_chart(gender_data, "Arrests by Gender")
    )]
)

# Age distribution pie chart
age_pie_chart = dcc.Loading(
    children=[dcc.Graph(
        id='age-pie-chart',
        config={'displayModeBar': False},
        figure=create_pie_chart(age_data, "Arrests by Age Group")
    )]
)
