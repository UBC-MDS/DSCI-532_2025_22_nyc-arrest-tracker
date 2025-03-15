import pandas as pd
import geopandas as gpd

nyc_boroughs = gpd.read_parquet("data/processed/borough_data.geoparquet")
nyc_precinct = gpd.read_parquet("data/processed/precinct_data.geoparquet")
nyc_arrests = pd.read_parquet("data/processed/arrest_data.parquet")

# Create default gender data for all arrests (citywide)
gender_data = pd.DataFrame({
    'PERP_SEX': nyc_arrests['PERP_SEX'].value_counts().index,
    'Arrests': nyc_arrests['PERP_SEX'].value_counts().values
})

# Create default age data for all arrests (citywide)
age_data = pd.DataFrame({
    'AGE_GROUP': nyc_arrests['AGE_GROUP'].value_counts().index,
    'Arrests': nyc_arrests['AGE_GROUP'].value_counts().values
})

arrest_crimes = nyc_arrests['OFNS_DESC'].value_counts().reset_index()
arrest_crimes.columns = ['Crime Type', 'Frequency']

# Get the top 10 most frequent crimes
top_crimes = arrest_crimes.head(10)

all_crime_types = sorted(nyc_arrests['OFNS_DESC'].unique().tolist())

# Calculate min and max dates from the data
min_date = nyc_arrests['ARREST_DATE'].min().strftime('%Y-%m-%d')
max_date = nyc_arrests['ARREST_DATE'].max().strftime('%Y-%m-%d')

# Data for crime frequency pie chart - rename columns in one step
crime_pie_data = top_crimes.rename(
    columns={'Crime Type': 'OFNS_DESC', 'Frequency': 'Arrests'}
)
