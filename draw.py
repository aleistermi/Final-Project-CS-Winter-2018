# CS122: Project
#
# Linux commands to get CDMX Geojson file are as follows
#
# wget http://datamx.io/dataset/8ac02ebd-3a48-4e82-8042-c283e3eee1d5/resource/7b5a3b0a-4405-48d6-a4eb-d9f13bb50d3a/download/coloniasmexico.zip
# unzip coloniasmexico.zip
# ogr2ogr -f GeoJSON -where 'ST_NAME = "DISTRITO FEDERAL"' CDMX.geojson Colonias/Colonias.shp

# wget http://internet.contenidos.inegi.org.mx/contenidos/Productos/prod_serv/contenidos/espanol/bvinegi/productos/geografia/marcogeo/889463171829_s.zip
# unzip 889463171829_s.zip
# ogr2ogr -f GeoJSON try2.geojson 09mun.shp


# ogr2ogr -f GeoJSON -where 'CVE_ENT = "09"' delegacines.geojson 09ent.shx

# ogr2ogr -f GeoJSON delegacines.geojson data.shp

import json
import pandas as pd
import folium
import webbrowser
import geopandas as gpd
import os
import time
import csv
import numpy as np


columnn = ['Number of Markets',
            'Number of Schools',
            'Number of Hospitals',
            'Buldings w/ damage from 09-19-17 earthquake',
            'Number of transit stops',
            'Average temperature',
            'Robberies per 100,000 inhabitants',
            'Home robberies per 100,000 inhabitants',
            'Murders per 100,000 inhabitants',
            'Robberies outside home per 100,000 inhabitants']

columns = ['Number of Markets',
            'Number of Schools',
            'Number of Hospitals',
            'Buldings w/ damage from 09-19-17 earthquake',
            'Number of robberies',
            'Number of home robberies',
            'Number of murders',
            'Number of transit stops',
            'Average temperature',
            'Population',
            'Number of robberies outside home']

def show_additional_information():
    print()
    print('you can choose from the additional_information written below')
    print()
    print()
    for option in columns:
        print("'{}'".format(option))

def get_necessary_file(type_of_house, type_of_operation):
    if not type_of_house in ['house', 'appartment']:
        print('select either "house" or "appartment"')  
    elif not type_of_operation in ['sale', 'rent']:
        print('select either "sale" or "rent"')
    else:
        filename =  "{} {}.csv".format(type_of_house, type_of_operation)
        return filename

def main(type_of_house, type_of_operation, additional_information=None):

    cdmx_location = [19.4326077, -99.1332080]
    map_ = folium.Map(location=cdmx_location, zoom_start=12)

    geojson = r'CDMX.geojson'

    filename = get_necessary_file(type_of_house, type_of_operation)

    price_df = pd.read_csv(filename, 
                            header = None, 
                            names = ['OBJECTID', 'place','price'])
    n = filename[:-4].split()
    name = 'The price of {} for {} (US$)'.format(n[0], n[1])
    get_choropleth_map(geojson, map_, price_df,'price', 'YlGnBu', name)
    del price_df

    if additional_information:
        df = pd.read_csv('integrated.csv', encoding = "utf-8", header = 0)
        columnname = additional_information
        get_choropleth_map(geojson, map_, df, columnname, 'YlOrRd', columnname, boudary=True)
        get_marker(map_, df, columnname)


    geojson3 = r'delegacion.geojson'
    map_.choropleth(geo_data=geojson3,    
                    fill_color='#3186cc',
                     fill_opacity = 0,
                     line_opacity = 1,
                     reset=False,
                     name='Municipality')

    folium.LayerControl().add_to(map_)

    # Get the mapping as a html data
    lst = [type_of_house, type_of_operation,'.html']
    outfile = "".join(lst)
    map_.save(outfile=outfile)

    # Delete the html file
#    if check_open("map.html"):
    webbrowser.open(outfile)
    time.sleep(30)
    os.remove(outfile)


def get_choropleth_map(geojson, map_, df, columnname, color ,name ,boudary=False):
    # Read csv file data
    df = df[['OBJECTID',columnname]]
    mini = df[columnname].min()
    df = df[df[columnname] != 0]
    scale = []
    # Read Geojson file data. Polygons corresponds to 'key_on' and 
    # columns' first element should be exactly same to the content of 'key_on'
    # The data to show should be put in the second element of the columns in
    # the csv file. Colors are defined by 'fill_color' and the gradation of 
    # the color is defined by the 'threshold_scale'.
#    scale = [mini, twenty, forty, sixty, eighty]
#    if boudary:
#        i = 0.1
#        while i < 1:
#            scale.append(df[columnname].quantile(i))
#            i += 0.2
#    else:
    i = 0
    while i < 1:
        scale.append(df[columnname].quantile(i))
        i += 0.2

    map_.choropleth(geo_data=geojson, data=df,
                    columns=['OBJECTID', columnname],
                    key_on='feature.properties.OBJECTID',
                    threshold_scale=scale,    
                    fill_color= color,
                     fill_opacity = 0.75,
                     line_opacity = 0.2,
                     legend_name = name,
                     reset=False,
                     name = name)


def get_marker(map_, df, columnname):
    df = df.groupby('MUN_NAME')[columnname].sum()
    gdf = gpd.read_file('delegacion.geojson')
    gdf['centroid'] = gdf.geometry.centroid
    gdf = gdf[['NOM_MUN','centroid']]
    rowlength = len(gdf.index)
    for i in range(rowlength):
        name = gdf.iat[i, 0].upper()
        centroid = gdf.iat[i, 1]
        if name == 'GUSTAVO A. MADERO':
            name = 'GUSTAVO A MADERO'
        message = '{} is {} in {}'.format(columnname, df[name], name)
        folium.Marker(location=[centroid.y, centroid.x],
                        popup=message,
                        icon=folium.Icon(color='green',icon='info-sign')
                        ).add_to(map_)


def check_open(url):
    page = ''
    while page == '':
        try:
            webbrowser.open(url)
            page = url
        except:
            print("Connection refused.")
            print("Let me try in 5 seconds")
            print("ZZzzzz...")
            time.sleep(5)
            print("Was a nice sleep, now let me continue...")
            continue
    return page


if __name__ == "__main__":
    main() 