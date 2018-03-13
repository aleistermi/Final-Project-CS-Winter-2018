# -*- coding: utf-8 -*-
"""
Created on Sat Mar  3 18:32:25 2018

@author: jesus
"""
'''
Auxiliary functions used in 'Complementary_variables.py'
'''
import pandas as pd
import geopandas as gpd

def points_in_colonia(point_gdf, polygon_gdf, file_name):
    '''
    Count the poitns within neighborhoods polygons and returns a data frame 
    where every row is a neighborhood and indicates the total numbers of
    points in that polygon
    
    Inputs:
        point_gdf: Geodataframe with information of geographic points.
        polygon_gdf: Geodataframe with information of geographic polygons of 
        neighborhoods.
        file_name: name of the file where the information is going to be stored.
     Returns: a data frame and a csv file
    '''
    working_list = []
    for index, point in point_gdf.iterrows():
        for i, polygon in polygon_gdf.iterrows():
            if point.geometry.within(polygon.geometry) == True:
                working_list.append([index, polygon.OBJECTID, polygon.MUN_NAME,\
                                     polygon.SETT_NAME])

    df = pd.DataFrame(working_list)
    df.columns = ['point_id', 'colonia_id', 'delegacion', 'colonia']
    df_by_colonia = df.groupby(['colonia_id','delegacion', 'colonia'], \
                               sort = False)['point_id'].count()
    df_by_colonia.to_csv(file_name)
    
    return df_by_colonia
    

#df1 is lista_colonias and df2 is geotemp
def temp_by_colonia(gdf1, gdf2):
    '''
    Computes the average temperature per neighborhood based on the Inverse
    Distance Weighting interpolation technique.
    
    Inputs:
        gdf1, gdf2: Geodataframes with information of geographic points (in 
        this case gdf1 is related with neighborhoods centroids and gdf2 is
        related with monitoring stations location).
    Returns: a data frame
    '''
    final_list = []
    for index, row in gdf1.iterrows():
        numerator = 0
        denominator = 0
        for i, r in gdf2.iterrows():
            sqr_dist = row.centroid.distance(r.geometry)**2
            numerator += r.avg/sqr_dist
            denominator += 1/sqr_dist
        final_list.append([index, row.MUN_NAME, row.SETT_NAME, \
                           numerator/denominator])
    
    return final_list

def population_by_colonia(mz_gdf, polygon_gdf, file_name):
    '''
    Count the population within neighborhood polygons.
    
    Inputs:
        mz_gdf: Geodataframe with centroids of blocks and population on that 
        blocks.
        polygon_gdf:
        file_name: name of the file where the information is going to be stored.
     Returns: a data frame and a csv file
    '''
    working_list = []
    for index, block in mz_gdf.iterrows():
        for i, polygon in polygon_gdf.iterrows():
            if block.centroid.within(polygon.geometry) == True:
                working_list.append([index, polygon.OBJECTID, polygon.MUN_NAME,\
                                     polygon.SETT_NAME, block.POB1])
                
    df = pd.DataFrame(working_list)
    df.columns = ['mz_local_id', 'colonia_id', 'delegacion', 'colonia', \
                  'population']
    df_by_colonia = df.groupby(['colonia_id','delegacion', 'colonia'], \
                               sort = False)['population'].sum()
    df_by_colonia.to_csv(file_name)
    
    return df_by_colonia