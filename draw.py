# CS122: Project
#
# Linux commands to get CDMX Geojson file are as follows
#
# wget http://datamx.io/dataset/8ac02ebd-3a48-4e82-8042-c283e3eee1d5/resource/7b5a3b0a-4405-48d6-a4eb-d9f13bb50d3a/download/coloniasmexico.zip
# unzip coloniasmexico.zip
# ogr2ogr -f GeoJSON -where 'ST_NAME = "DISTRITO FEDERAL"' CDMX.geojson Colonias/Colonias.shp


import json
import pandas as pd
import folium
import webbrowser
import geopandas as gpd
import os
import time  


def main(columnname_for_display='count'):

    # CDMX as a standard of Mexico's map, 
    cdmx_location = [19.4326077, -99.1332080]
    map_ = folium.Map(location=cdmx_location, zoom_start=11)

    # Necessary to create Geojson file for each neighborhood in units
    # for polygons in advance. 'r' means 'read' and the following string
    # is Geojson file
    geojson = r'CDMX.geojson'

    # Read csv file data
    df = pd.read_csv('robbery_by_colonia.csv', encoding = "ISO-8859-1",
                     header = None, 
                     names = ['OBJECTID','Delegacion','neighborhood','count'])

    # Read Geojson file data. Polygons corresponds to 'key_on' and 
    # columns' first element should be exactly same to the content of 'key_on'
    # The data to show should be put in the second element of the columns in
    # the csv file. Colors are defined by 'fill_color' and the gradation of 
    # the color is defined by the 'threshold_scale'.
    map_.choropleth(geo_data=geojson, data=df,
                    columns=['OBJECTID', columnname_for_display],
                    key_on='feature.properties.OBJECTID',
                    threshold_scale=[0, 100, 200, 300, 400, 500],    
                    fill_color='YlOrRd',
                     fill_opacity = 0.7,
                     line_opacity = 0.2,
                     legend_name = 'Number of crime incidents per district',
                     reset=True) 

    # build makers in the each district   
    gdf = gpd.read_file('CDMX.geojson')
    gdf['centroid'] = gdf.geometry.centroid
    gdf = gdf[['SETT_NAME','centroid']]
#    rowlength = len(gdf.index)
    rowlength = 200
    for i in range(rowlength):
        neighborhood = gdf.iat[i, 0]
        centroid = gdf.iat[i, 1]
        folium.Marker(location=[centroid.y, centroid.x],
                        popup=neighborhood).add_to(map_)

    # Get the mapping as a html data
    map_.save(outfile="map.html")

    # Open the html file and show the map
    url = "map.html"
    webbrowser.open(url)

    # Delete the html file
    time.sleep(3)
    os.remove("map.html")


if __name__ == "__main__":
    main() 