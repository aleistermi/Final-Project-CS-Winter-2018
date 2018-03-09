# -*- coding: utf-8 -*-
"""
Created on Tue Mar  6 09:25:01 2018

@author: jesus
"""
import geopandas as gpd

path = 'C:/Users/jesus/OneDrive/Documentos/GitHub/Final-Project-CS-Winter-2018/Data/'
#read shp
delegaciones = gpd.read_file(path + 'MUNICIPIOS.shp')
#calculate centroid
delegaciones['centroid'] = delegaciones.geometry.centroid
#slice GDF for CDMX
delegaciones_CDMX = delegaciones[delegaciones.CVE_ENT == '09']
#drop not used columns
delegaciones_CDMX = delegaciones_CDMX.drop(['CVE_ENT', 'CVE_MUN'], axis = 1)
#save file as csv
delegaciones_CDMX.to_csv(path + 'delegacion_centroid.csv', index = False)
