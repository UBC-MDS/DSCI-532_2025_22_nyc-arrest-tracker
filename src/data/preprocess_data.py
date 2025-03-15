import pandas as pd
import geopandas as gpd

# Load the NYC borough GeoJSON data
borough_url = (
    "https://raw.githubusercontent.com/codeforgermany/click_that_hood/refs/"
    "heads/main/public/data/new-york-city-boroughs.geojson"
)
borough_gpd = gpd.read_file(borough_url)

# Load the NYPD Precinct GeoJSON data
precinct_url = (
    "https://raw.githubusercontent.com/ResidentMario/geoplot-data/refs/heads/"
    "master/nyc-police-precincts.geojson"
)
precinct_gpd = gpd.read_file(precinct_url)

precinct_gpd['precinct'] = pd.to_numeric(
    precinct_gpd['precinct'],
    downcast='integer',
    errors='coerce'
)

# Load the NYPD Arrests data
dtype_dict = {
    'ARREST_KEY': 'int64',
    'ARREST_DATE': 'str',
    'PD_CD': 'int64',
    'PD_DESC': 'str',
    'KY_CD': 'int64',
    'OFNS_DESC': 'category',
    'LAW_CODE': 'str',
    'LAW_CAT_CD': 'category',
    'ARREST_BORO': 'category',
    'ARREST_PRECINCT': 'int16',
    'JURISDICTION_CODE': 'int8',
    'AGE_GROUP': 'category',
    'PERP_SEX': 'category',
    'PERP_RACE': 'category',
    'X_COORD_CD': 'float32',
    'Y_COORD_CD': 'float32',
    'Latitude': 'float32',
    'Longitude': 'float32'
}

# Load the NYPD Arrests data
arrest_path = "data/raw/NYPD_Arrest_Data__Year_to_Date_.csv"
try:
    # Try loading with optimized dtypes
    arrests_pd = pd.read_csv(
        arrest_path,
        dtype=dtype_dict,
        usecols=list(dtype_dict.keys()),  # Only load columns we need
        low_memory=False
    )
except:
    # Fallback to standard loading if optimized loading fails
    arrests_pd = pd.read_csv(arrest_path)

arrests_pd = arrests_pd[arrests_pd["ARREST_PRECINCT"] != 483]

arrests_pd["ARREST_DATE"] = pd.to_datetime(
    arrests_pd["ARREST_DATE"],
    format="%m/%d/%Y"
)

# Map borough names to borough codes - use vectorized mapping
borough_mapping = {
    'B': 'Bronx',
    'S': 'Staten Island',
    'K': 'Brooklyn',
    'M': 'Manhattan',
    'Q': 'Queens'
}
arrests_pd['borough'] = arrests_pd['ARREST_BORO'].map(borough_mapping)

# Store the processed data
arrests_pd.to_parquet("data/processed/arrest_data.parquet", engine="pyarrow")
precinct_gpd.to_parquet("data/processed/precinct_data.geoparquet", engine="pyarrow")
borough_gpd.to_parquet("data/processed/borough_data.geoparquet", engine="pyarrow")