from dash import dcc

from data import crime_pie_data, gender_data, age_data
from utils import create_pie_chart

# Crime frequency pie chart
crime_pie_chart = dcc.Graph(
    id='crime-pie-chart',
    figure=create_pie_chart(crime_pie_data, "Top 10 Crime Types")
)

# Gender distribution pie chart
gender_pie_chart = dcc.Graph(
    id='gender-pie-chart',
    figure=create_pie_chart(gender_data, "Arrests by Gender")
)

# Age distribution pie chart
age_pie_chart = dcc.Graph(
    id='age-pie-chart',
    figure=create_pie_chart(age_data, "Arrests by Age Group")
)
