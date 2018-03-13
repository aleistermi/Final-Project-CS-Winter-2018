# CS122: Project (Web scraping for properties data)
#
# Keisuke Yokota

import json
import pandas as pd
import folium
import webbrowser
import geopandas as gpd
import os
import time
import csv
import numpy as np
import sys


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


intro = ('You can get a map with housing information and other information. '
         'As a housing information, we have housing data based on the type '
         '("house" or "apartment") and the operation ("sale" or "rent"). '
         'Besides you need to choose one inforamtion from ones written below.')

#  "Original" 
def show():
    '''
    Show information we can have access to
    '''
    print()
    print()
    print(intro)
    print()
    print("[other information]")
    for option in columns:
        print("'{}'".format(option))
    print()
    print()
    print('Please enter command line like following one;')
    print()
    print('python3 draw.py "house" "sale" "Number of murders"')
    print('or')
    print('python3 draw.py "apartment" "rent" "Number of Schools"')    
    print()


#  "Original" 
def draw(type_of_house, type_of_operation, other_info, store=False):
    '''
    Draw a map with house price data and other data.

    Inputs:
        type_of_house: "house" or "apartment" (string)
        type_of_operation: "sale" or "rent" (string)
        other_info: information other than price data such as
                    "Number of murders" or "Number of Schools" (string)
        store: HTML file as an output is stored if this is True and otherwise
               if this is False (Boolean)

    Outputs:
        HTML file
    '''
    # Identify filename of price data and other information
    filename = get_necessary_file(type_of_house, type_of_operation)
    if filename == None:
        return None
    if other_info not in columns:
        print()
        print('Select valid "other information"')
        print('Try it again by command "python3 draw.py"')
        return None

    # draw base map for data visualization
    cdmx_location = [19.4326077, -99.1332080]
    map_ = folium.Map(location=cdmx_location, zoom_start=12)

    # Read geojson file of neighbourhood unit (most minute ditrict) 
    # in Mexico City
    geojson = r'neighborhood.geojson'

    # draw choropleth map in neighbourhood unit (most minute ditrict)
    # based on price data 
    price_df = pd.read_csv(filename, 
                    header = None, 
                    names = ['OBJECTID', 'SETT_NAME','price']) 
    n = filename[:-4].split()
    name = 'The price of {} for {} (US$)'.format(n[0], n[1])
    get_choropleth_map(geojson, map_, price_df, 'price', 'YlGnBu', name)


    # draw choropleth map in neighbourhood unit (most minute ditrict)
    # based on information other than price data
    df = pd.read_csv('integrate.csv', encoding = "utf-8", header = 0)
    columnname = other_info
    get_choropleth_map(geojson, map_, df, columnname,'YlOrRd', columnname)

    # put markers in Munucipality unit
    # (deligacion unit, lager unit than neighbourhood unit)
    get_marker(map_, df, price_df, columnname)

    # read geojson file of neighbourhood unit (most minute ditrict) 
    # in Mexico City and draw outline of Munucipality unit
    # (deligacion unit, lager unit than neighbourhood unit)
    geojson3 = r'delegacion.geojson'
    map_.choropleth(geo_data=geojson3,    
                    fill_color='#3186cc',
                     fill_opacity = 0,
                     line_opacity = 1,
                     reset=False,
                     name='Municipality')

    # put layer controler in the map
    folium.LayerControl().add_to(map_)

    # Get the mapping as a html data
    lst = [type_of_house, type_of_operation,'.html']
    outfile = "".join(lst)
    map_.save(outfile=outfile)

    # show the map by opening FireFox
    webbrowser.open(outfile)

    # Delete the html file if store == False
    if not store:
        time.sleep(30)
        os.remove(outfile)


#  "Original" 
def get_necessary_file(type_of_house, type_of_operation):
    '''
    Get a necessary price data file for mapping.

    Inputs:
        type_of_house: "house" or "apartment" (string)
        type_of_operation: "sale" or "rent" (string)

    Outputs:
        name of CSV file (string)
    '''
    if not type_of_house in ['house', 'apartment']:
        print()
        print('Select either "house" or "apartment"')
        print('Try it again by command "python3 draw.py"')
        return None
    elif not type_of_operation in ['sale', 'rent']:
        print()
        print('Select either "sale" or "rent"')
        print('Try it again by command "python3 draw.py"')
        return None
    else:
        filename =  "{} {}.csv".format(type_of_house, type_of_operation)
        return filename


#  "Original" 
def get_choropleth_map(geojson, map_, df, columnname, color ,name):
    '''
    Draw a map with house price data and other data.

    Inputs:
        geojson: geojson file
        map_: map object
        df: data frame for the marker       
        columnname: column name in the dataframe
        color: color for the choropleth map (string)
        name: name for label(legend name) 

    Outputs:
        choropleth map
    '''
    df = df[['OBJECTID',columnname]]
    mini = df[columnname].min()
    df = df[df[columnname] != 0.0]
    scale = [mini]
    if columnname not in ['price']:
        i = 0.1
        while i <= 1:
            scale.append(df[columnname].quantile(i))
            i += 0.2
    else:
        i = 0.2
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


#  "Original" 
def get_marker(map_, df1, df2, columnname):
    '''
    put markers to a map.

    Inputs:
        map_: map object
        df1: data frame for the marker
        df2: data frame for the marker
        columnname: column name in the dataframe

    Outputs:
        map with markers
    '''
    name_pool = []
    if columnname == 'Average temperature':
        df1 = df1.groupby('MUN_NAME')[columnname].median()
    else:
        df1 = df1.groupby('MUN_NAME')[columnname].sum()
    gdf = gpd.read_file('delegacion.geojson')
    gdf['centroid'] = gdf.geometry.centroid
    gdf = gdf[['NOM_MUN','centroid']]
    rowlength = len(gdf.index)
    for i in range(rowlength):
        name = gdf.iat[i, 0].upper()
        centroid = gdf.iat[i, 1]
        if name == 'GUSTAVO A. MADERO':
            name = 'GUSTAVO A MADERO'
        words = '{} is {} in {}'.format(columnname, df1[name], name)
        folium.Marker(location=[centroid.y, centroid.x],
                        popup=words,
                        icon=folium.Icon(color='green',icon='info-sign')
                        ).add_to(map_)


#  "Original" 
if __name__ == "__main__":
    if len(sys.argv) != 4:
        show()
    else:
        draw(sys.argv[1], sys.argv[2], sys.argv[3])           