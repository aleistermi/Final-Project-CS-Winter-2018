# -*- coding: utf-8 -*-
"""
Created on Mon Feb 26 14:01:29 2018

@author: jesus
"""

import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import util_compvar 
import csv

'''
In this python file we make the computation of complementary variables 
(different from real estate prices) at neigborhood level. In Mexico 
neighborhood desagregation is not common, most of the variables reported by the 
government are grouped by municipalities, but in some cases they publish files 
with metadata that inlcudes georeferences, we use those georeferences to obtain 
statistics by neighborhood.
The complementary variables we use are:
- Number of buildings with any damage caused by the earthquake of september 
  19th of 2017 in Mexico City (2017).
- Number of robberies, home roberies and murders (2015).
- Number of hospitals (2015).
- Number of schools (2015).
- Number of markets (2015).
- Number of public transit stops (2015).
- Average temperature (2015).
- Population (2010).
'''

#This is the location of the inputs for the project
path = 'C:/Users/jesus/OneDrive/Documentos/GitHub/Final-Project-CS-Winter-2018\
        /Raw_Data/Official_data'
#This is the location of the folder for the output files
output_path = 'C:/Users/jesus/OneDrive/Documentos/GitHub/Final-Project-CS-\
               Winter-2018/Raw_Data/outputs/'

#1. Create the geodataframe containing the polygons of the neighborhoods of 
# Mexico city, from a shapefile withnthat information.
# ("colonias" is the spanish word that people from Mexico city use for neighborhood) 

# Reading the shapefile of neighborhoods of all the country
col_mex = gpd.read_file(path + '/Colonias/Colonias.shp')
#filtering the geodataframe, to get polygons only for Mexico City.
colonias_df = col_mex[col_mex.ST_NAME == 'DISTRITO FEDERAL']

#2. Count number of buildings with damage caused by the earthquake of september 
# 19th of 2017. The georenferences was published in a csv file as floats.

#Reading csv file with information.
p = pd.read_csv(path + '/damage_p.csv', names = ['num', 'lat', 'lon'])
#Deleting rows with no complete information.
p = p.dropna(axis = 0, how = 'any')

#creating Point objects from floats.
geometry = [Point(xy) for xy in zip(p.lon, p.lat)]
p = p.drop(['lat', 'lon'], axis=1)
#This the projection used in all the project, it is also the most common.
# It is also known as: "World Geodesic System 84"
crs = {'init': 'epsg:4326'}

# Creating the geodataframe of earthquake damage
pg = gpd.GeoDataFrame(p, crs=crs, geometry=geometry)

# Counting the number of biulding with damage by neighborhood, and creating 
# the csv file.
damages = util_compvar.points_in_colonia(pg,colonias_df, output_path + \
          'eqdamage_by_colonia.csv')
      
#3. Count number of robberies, home roberies and murders on echa neighborhood

# Reading the csv file, as in the damage case, the georeferences were floats.
crime_df = pd.read_csv(path + '/crime-lat-long.csv')

# We only used data of the last complete year reported
crime_df_2015 = crime_df[crime_df.year == 2015]
crime_df_2015.drop(['cuadrante', 'date', 'hour', 'year', 'month'], axis=1)

# Deleting rows with no complete information
crime_df_2015 = crime_df_2015.dropna(axis = 0, how = 'any')

# Creating Point objects from floats
crime_geo = [Point(xy) for xy in zip(crime_df_2015.long, crime_df_2015.lat)]
crime_df_2015 = crime_df_2015.drop(['lat', 'long'], axis=1)
geocrime_2015 = gpd.GeoDataFrame(crime_df_2015, crs=crs, geometry=crime_geo)

# Creating data frames for especific kind of crimes
home_robbery = geocrime_2015[geocrime_2015.crime == 'ROBO A CASA HABITACION C.V.']
robbery = geocrime_2015[(geocrime_2015.crime != 'VIOLACION') & \
                        (geocrime_2015.crime != 'LESIONES POR ARMA DE FUEGO') &\
                        (geocrime_2015.crime != 'HOMICIDIO DOLOSO')]
murder = geocrime_2015[geocrime_2015.crime == 'HOMICIDIO DOLOSO']

#Counting crimes by neighborhood and creating the csv files
home_by_colonia = util_compvar.points_in_colonia(home_robbery, colonias_df, \
                  outpu_path = 'home_robbery_by_colonia.csv')
robbery_by_colonia = util_compvar.points_in_colonia(robbery, colonias_df, \
                     output_path = 'robbery_by_colonia')
murder_by_colonia = util_compvar.points_in_colonia(murder, colonias_df, \
                    output_path + 'murder_by_colonia.csv')

#4. Reading the shapefile with point of interest, such as: hospitals, schools
# markets

#The file originally had a different proyection, so we needed to change it 
sip_15 = gpd.read_file (path + '/points/convertedsip15.shp')
sip_15_reproy = sip_15.to_crs({'init': 'epsg:4326'})

#5. Count hospitals by neighborhood
hospitals_by_colonia = util_compvar.points_in_colonia(sip_15_reproy\
                      [sip_15_reproy.GEOGRAFICO == 'Centro de Asistencia Médica'], \
                      colonias_df, output_path + 'hospitals_by_colonia.csv')

#6. Count schools by neighborhood
schools_by_colonia = util_compvar.points_in_colonia(sip_15_reproy\
                     [sip_15_reproy.GEOGRAFICO == 'Escuela'], colonias_df, \
                     output_path + 'schools_by_colonia.csv')

#7. Count markets by neighborhood
markets_by_colonia = util_compvar.points_in_colonia(sip_15_reproy\
                    [sip_15_reproy.GEOGRAFICO == 'Mercado'], colonias_df, \
                    output_path + 'markets_by_colonia.csv')

#8. Count transit stops by neighborhood

# Reading csv file
transit_stations = pd.read_csv(path + '/t_stations.csv')
# Deleting not useful columns and rows
transit_stations = transit_stations.drop(['orden', 'trip_id', 'trip_headsign',\
'agency_id', 'organismo', 'route_id', 'route_short_name', 'route_long_name', \
'service_id', 'route_type', 'stop_sequence', 'stop_id', 'stop_name', \
'arrival_time', 'departure_time', 'shape_id', 'monday', 'tuesday', 'wednesday',\
'thursday', 'friday', 'saturday', 'sunday', 'start_date', 'end_date', \
'calendario', 'start_time', 'end_time', 'headway_secs', 'Unnamed: 31', \
'Unnamed: 32'], axis = 1)
transit_stations = transit_stations.dropna(axis = 0, how = 'any')

# In this case the georeferences were strings, so we needed to convert it to floats
pd.to_numeric(transit_stations.stop_lat,downcast='float')
pd.to_numeric(transit_stations.stop_lon,downcast='float')

# Creating point objects 
transit_geometry = [Point(xy) for xy in zip(transit_stations.stop_lon, \
                    transit_stations.stop_lat)]
transit_stations = transit_stations.drop(['stop_lat', 'stop_lon'], axis=1)
geostations = gpd.GeoDataFrame(transit_stations, crs=crs, \
                               geometry=transit_geometry)

# Counting transit stops by neighborhood
stations_by_colonia = util_compvar.points_in_colonia(geostations,colonias_df, \
                      output_path + 'stations_by_colonia.csv')

#9. Computing average temperature per neighborhood

# Reading file with daily information of temperatures in 48 different stations
meteorologia = pd.read_csv(path +'/temp_pol/meteorologia_2015.csv', \
                           skiprows = 10)

# Deleting not useful information
meteorologia = meteorologia.drop(['date', 'unit'], axis =1)
meteorologia = meteorologia[meteorologia.id_parameter == 'TMP']
meteorologia = meteorologia.drop(['id_parameter'], axis =1)
meteorologia.dropna(axis = 0, how = 'any')

# Getting the mean of the observed temperature by station
avg_temp = meteorologia.groupby('id_station')['value'].mean()

# Creating a new csv file with useful information
avg_temp.to_csv(path + '/temp_pol/avg_temp.csv')

# Now we read the file with information about location of stations and delete 
# not useful informations
cat_stations = pd.read_csv(path + '/temp_pol/cat_estacion.csv', skiprows = 1, \
                           encoding = 'iso-8859-1')
cat_stations = cat_stations.drop(['nom_estac','alt', 'obs_estac','id_station'],\
                                 axis = 1)

# Reading the file with averages temperature by station and merging 
# georeferences of stations
avg_temp = pd.read_csv(path + '/temp_pol/avg_temp.csv')
avg_temp.columns = ['station_id', 'avg']

# Creating a unique data frame with georeferences and average temperature 
# by station
avg_temp.merge(cat_stations, left_on='station_id', right_on='cve_stac',\
               how='left')
avg_temp = avg_temp.merge(cat_stations, left_on='station_id', \
                          right_on='cve_estac', how='left')
avg_temp = avg_temp.drop(['cve_estac'], axis = 1)

# Creating point objects and a geodataframe
temp_geometry = [Point(xy) for xy in zip(avg_temp.longitud, avg_temp.latitud)]
avg_temp = avg_temp.drop(['longitud', 'latitud'], axis=1)
crs = {'init': 'epsg:4326'}
geotemp = gpd.GeoDataFrame(avg_temp, crs=crs, geometry=temp_geometry)

# Computing the centroids of neighborhood polygons. We use them to interpolate
# the average temperature using Inverse Distance Weighting technique.
lista_colonias = colonias_df.drop(['POSTALCODE', 'ST_NAME', 'SETT_TYPE', \
                                   'AREA', 'Shape_Leng', 'Shape_Area'], axis = 1)
lista_colonias['centroid'] = lista_colonias.geometry.centroid

# Computing the average tempertature per neighborhood
avg_temp_list = util_compvar.temp_by_colonia(lista_colonias, geotemp)

# Creating a csv file with this information
with open (path + '/outputs/temp_by_colonias.csv', 'w') as f:
    csv_table = csv.writer(f)
    for row in avg_temp_list:
        csv_table.writerow(row)

# 10 Computing population by neighborhood

blocks = gpd.read_file(path + '/Manzanas/df_manzanas.shp')
population_by_block = blocks[['POB1', 'geometry']]
population_by_colonia = util_compvar.population_by_colonia(population_by_block,\
                        colonias_df, path + '/outputs/population_by_colonia.csv')

