import pandas as pd
import geopandas as gpd

# Load the NYC borough GeoJSON data
borough_url = (
    "https://raw.githubusercontent.com/codeforgermany/click_that_hood/refs/"
    "heads/main/public/data/new-york-city-boroughs.geojson"
)
nyc_boroughs = gpd.read_file(borough_url)

# Load the NYPD Precinct GeoJSON data
precinct_url = (
    "https://raw.githubusercontent.com/ResidentMario/geoplot-data/refs/heads/"
    "master/nyc-police-precincts.geojson"
)
nyc_precinct = gpd.read_file(precinct_url)

# Load the NYPD Arrests data
arrest_path = "data/raw/NYPD_Arrest_Data__Year_to_Date_.csv"
nyc_arrests = pd.read_csv(arrest_path)

# Remove non-existant precincts
nyc_arrests = nyc_arrests[nyc_arrests["ARREST_PRECINCT"] != 483]
nyc_arrests["ARREST_DATE"] = pd.to_datetime(
    nyc_arrests["ARREST_DATE"], format="%m/%d/%Y"
)

# Map borough names to borough codes
borough_mapping = {
    'B': 'Bronx',
    'S': 'Staten Island',
    'K': 'Brooklyn',
    'M': 'Manhattan',
    'Q': 'Queens'
}
nyc_arrests['borough'] = nyc_arrests['ARREST_BORO'].map(borough_mapping)

# Convert precinct to integer
nyc_precinct['precinct'] = pd.to_numeric(
    nyc_precinct['precinct'],
    downcast='integer',
    errors='coerce'
)

# Gender and Age data preparation
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

# Group the data by the more general offense description (OFNS_DESC)
arrest_crimes = nyc_arrests['OFNS_DESC'].value_counts().reset_index()
arrest_crimes.columns = ['Crime Type', 'Frequency']

# Get the top 10 most frequent crimes
top_crimes = arrest_crimes.head(10)

# Get all unique crime types for dropdown
all_crime_types = sorted(nyc_arrests['OFNS_DESC'].unique().tolist())

# Calculate min and max dates from the data
min_date = nyc_arrests['ARREST_DATE'].min().strftime('%Y-%m-%d')
max_date = nyc_arrests['ARREST_DATE'].max().strftime('%Y-%m-%d')

# Data for crime frequency pie chart
crime_pie_data = top_crimes.rename(
    columns={'Crime Type': 'OFNS_DESC', 'Frequency': 'Arrests'}
)
