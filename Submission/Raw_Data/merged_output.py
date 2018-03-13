# -*- coding: utf-8 -*-
"""
Created on Thu Mar  8 12:26:29 2018

@author: jesus
"""

'''
In this file we create a unique dataframe and csv file that is the input 
to produce the maps of complementary variables. This task could be done 
directly in 'Complementary_variables.py', but it takes about two hours to 
produce some of the dataframes and files needed; so we do the merge in 
a different file.
'''
import pandas as pd
import geopandas as gpd

#This is the path of the folder that contains the files we need to merge
path = 'C:/Users/jesus/OneDrive/Documentos/GitHub/Final-Project-CS-Winter-2018/\
        Raw_Data/outputs/'
        
# Reading the shapefile of neighborhoods of all the country
col_mex = gpd.read_file('C:/Users/jesus/OneDrive/Documentos/GitHub/Final-\
                        Project-CS-Winter-2018/Data/Colonias/Colonias.shp')
# Filtering the geodataframe, to get polygons only for Mexico City.
colonias_df = col_mex[col_mex.ST_NAME == 'DISTRITO FEDERAL']
# Droping the columns that we do not use.
lista_colonias = colonias_df.drop(['POSTALCODE','ST_NAME','SETT_TYPE','AREA',\
                                   'Shape_Leng','Shape_Area'], axis = 1)


#1. Read all the files needed, two of them hace different encoding, so we 
# include an extra parameter that fix this problem.
df1 = pd.read_csv(path + 'markets_by_colonia.csv')
df2 = pd.read_csv(path + 'schools_by_colonia.csv')
df3 = pd.read_csv(path + 'hospitals_by_colonia.csv')
df4 = pd.read_csv(path + 'eqdamage_by_colonia.csv')
df5 = pd.read_csv(path + 'robbery_by_colonia.csv')
df6 = pd.read_csv(path + 'home_robbery_by_colonia.csv')
df7 = pd.read_csv(path + 'murders_by_colonia.csv')
df8 = pd.read_csv(path + 'stations_by_colonia.csv')
df9 = pd.read_csv(path + 'temp_by_colonias.csv', encoding = 'iso-8859-1' )
df10 = pd.read_csv(path + 'population_by_colonias.csv', encoding = 'iso-8859-1' )

#2. We add column names
df1.columns = ['key', 'delegacion', 'colonia', 'markets']
df2.columns = ['key', 'delegacion', 'colonia', 'schools']
df3.columns = ['key', 'delegacion', 'colonia', 'hospitals']
df4.columns = ['key', 'delegacion', 'colonia', 'damage']
df5.columns = ['key', 'delegacion', 'colonia', 'robbery']
df6.columns = ['key', 'delegacion', 'colonia', 'home_robbery']
df7.columns = ['key', 'delegacion', 'colonia', 'murders']
df8.columns = ['key', 'delegacion', 'colonia', 'stations']
df9.columns = ['key', 'delegacion', 'colonia', 'temp']
df10.columns = ['key', 'delegacion', 'colonia', 'population']

#3. Merging the file using the key columns of every pair of dataframes. The
# parameter "how='outer'" allow us to preserve all the neiighborhoods that
# appear in any of the two dataframes.
df1 = df1.merge(df2, left_on='key', right_on='key', how='outer')
df1 = df1.merge(df3, left_on='key', right_on='key', how='outer')
df1 = df1.merge(df4, left_on='key', right_on='key', how='outer')
df1 = df1.merge(df5, left_on='key', right_on='key', how='outer')
df1 = df1.merge(df6, left_on='key', right_on='key', how='outer')
df1 = df1.merge(df7, left_on='key', right_on='key', how='outer')
df1 = df1.merge(df8, left_on='key', right_on='key', how='outer')
df1 = df1.merge(df9, left_on='key', right_on='key', how='outer')
df1 = df1.merge(df10, left_on='key', right_on='key', how='outer')

#4. Droping the columns that provides redundant information and appending the
# official names of neighborhoods and municipalities.
df1 = df1.drop(['delegacion_x', 'colonia_x', 'delegacion_y','colonia_y',  \
                'delegacion_x', 'colonia_x', 'delegacion_y', 'colonia_y', \
                'delegacion_x', 'colonia_x', 'delegacion_y', 'colonia_y', \
                'delegacion_x', 'colonia_x', 'delegacion_y', 'colonia_y', \
                'delegacion_x', 'colonia_x', 'delegacion_y', 'colonia_y'], \
                axis = 1)
df1 = df1.merge(lista_colonias, left_on='key', right_on='OBJECTID',how='outer')

#5. Creating a new variable that consider inly robberies committed outside 
# home
df1['outside_robbery'] = df1.robbery - df1.home_robbery

#6. Adding column names
df1.columns = ['key','Number of Markets', 'Number of Schools', \
               'Number of Hospitals', \
               'Buldings w/ damage from 09-19-17 earthquake', \
               'Number of robberies', 'Number of home robberies', \
               'Number of murders', 'Number of transit stops', \
               'Average temperature', 'Population', 'OBJECTID','MUN_NAME', \
               'SETT_NAME', 'Number of robberies outside home']

#7. Creating a csv file to store the information
df1.to_csv(path + 'integrated.csv', index = False)