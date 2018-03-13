# -*- coding: utf-8 -*-
"""
Created on Tue Mar 13 11:37:43 2018

@author: jesus
"""
'''
This file creates a shapefile for neighborhoods of Mexico City
based in shape file for neighborhoods in all the country.
'''

import geopandas as gpd

#reading shpe file with municipalities in Mexico
delegaciones = gpd.read_file('C:/Users/jesus/OneDrive/Documentos/GitHub/Final\
                             -Project-CS-Winter-2018/Data/MUNICIPIOS.shp')
#slicing the municipalities (delegaciones) of Mexico City
delegaciones_CDMX = delegaciones[delegaciones.CVE_ENT == '09']
#writing a new shp file
delegaciones_CDMX.to_file(driver = 'ESRI Shapefile',filename = 'C:/Users/jesus\
                          /OneDrive/Documentos/GitHub/Final-Project-CS-Winter-\
                          2018/Row_Data/data.shp')
