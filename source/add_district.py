#add liegislative districts to lara and mhvillage data

# this code takes a csv with community names, addresses, and gps coordinate
# then uses the districts geoJSON file to find the district for each coordinate
# we use the original geojson from https://gis-michigan.opendata.arcgis.com/
# we do not upload them to shiny because their too big so they don't appear in the
# github as well

#this code assumes the gps coordinates contained in each file ar called
# 'longitude', 'latitude' based on the encoding in add_clean_addresses

#####INPUT

path2folder = r"./data/" # fill in the path to your folder here.
assert len(path2folder) > 0

mhvillage_name = "mhvillage_dec7_googlecoord.csv"
lara_name = "LARA_with_all_coord.csv"
# Path to your legislative districts GeoJSON file
house_districts_geojson_path = "./data/Michigan_State_House_Districts_2021.geojson"
senate_districts_geojson_path = "./data/Michigan_State_Senate_Districts_2021.geojson"
#name of outut files
mhvillage_name_out = "data/mhvillagedec7_legislative1.csv"
lara_name_out = "data/LARA_with_coord_and_legislative_district1.csv"

#######################################################################################

import pandas as pd
import geopandas as gpd
import numpy as np
import shapely
from shapely.geometry import Point
import geopy


def find_district(geojson_file, coordinates):
    # Load the GeoJSON file into a GeoDataFrame
    gdf = gpd.read_file(geojson_file)
    
    # Create a Point geometry from the coordinates
    point = Point(coordinates)
    
    # Check each district for a containing point
    for _, row in gdf.iterrows():  # We use iterrows() here to get the row as a Series
        # If the point is within the polygon of this row, return the label
        if point.within(row['geometry']):
            return row['LABEL']
    return None  # Return None or an appropriate value if the point isn't in any district

#read data
mhvillage_df = pd.read_csv(path2folder + mhvillage_name)
lara_df = pd.read_csv(path2folder + lara_name)

#create columns
sLength = len(mhvillage_df['Longitude'])
mhvillage_df['House district'] = pd.Series(np.zeros(sLength), index=mhvillage_df.index)
mhvillage_df['Senate district'] = pd.Series(np.zeros(sLength), index=mhvillage_df.index)


for ind in range(len(mhvillage_df)):
    lon = float(mhvillage_df['longitude'].iloc[ind])
    lat = float(mhvillage_df['latitude'].iloc[ind])
    if lat and lon:
            # Check the legislative district
    	district_house = find_district(house_districts_geojson_path, (lon,lat))
    	district_senate = find_district(senate_districts_geojson_path, (lon,lat))
    	if district_senate and district_house:
    		print(district_senate)
    		print(district_house)
    		mhvillage_df.loc[ind,'House district'] = int(district_house)
    		mhvillage_df.loc[ind,'Senate district'] = int(district_senate)



mhvillage_df.to_csv(mhvillage_name_out) 

#Now LARA

sLength = len(lara_df['longitude'])
lara_df['House district'] = pd.Series(np.zeros(sLength), index=lara_df.index)
lara_df['Senate district'] = pd.Series(np.zeros(sLength), index=lara_df.index)

for ind in range(len(lara_df)):
    lon = float(lara_df['longitude'].iloc[ind])
    lat = float(lara_df['latitude'].iloc[ind])
    if lat and lon:
            # Check the legislative district
    	district_house = find_district( house_districts_geojson_path, (lon,lat))
    	district_senate = find_district(senate_districts_geojson_path,(lon,lat))
    	if district_senate and district_house:
    		print(district_senate)
    		print(district_house)
    		lara_df.loc[ind,'House district'] = int(district_house)
    		lara_df.loc[ind,'Senate district'] = int(district_senate)

lara_df.to_csv(lara_name_out)

 