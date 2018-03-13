#Cleaning data for final project

import pandas as pd 
import csv
import numpy as np
import jellyfish as jelly
from operator import itemgetter
from fuzzywuzzy import fuzz                                    
from fuzzywuzzy import process


EXCHANGE_RATE = 18.82
THRESHOLD_FUZZY = 80
path = '/home/student/capp30122-win-18-aleisterm/Final Project/'
# Change the path to where the datasets are located

def get_neighborhood (data, hoods):
    '''
    It matches the official list of neighborhoods (coming from the neighorhoods
    shapefile), with the neighborhoods obtained in the dataset.
    It uses fuzzywuzzy to make the record linkage
    '''

    dic_ids = {}

    for i, r in hoods.iterrows():

        dic_ids[r.SETT_NAME] = r.OBJECTID

    results = []
    for index, rowdf1 in data.iterrows():
        if rowdf1.neighborhood in dic_ids.keys():
            results.append( [dic_ids[rowdf1.neighborhood],rowdf1.delegacion, \
                rowdf1.neighborhood , rowdf1.type,rowdf1.transaction, \
                rowdf1.price_dollars, rowdf1.surface])
        elif 'Polanco' in rowdf1.neighborhood: # somehow we could not link all 
                                               #differerent versions of this neighborhood
            results.append( [dic_ids[rowdf1.neighborhood],rowdf1.delegacion,\
             'Polanco', rowdf1.type, rowdf1.transaction, rowdf1.price_dollars,\
              rowdf1.surface])     
        else:
            candidates = {}
            for colonia in dic_ids.keys():
                score = fuzz.partial_ratio(rowdf1.neighborhood, colonia)
                if score >= THRESHOLD_FUZZY:
                    candidates[score] = colonia
                    
        if len(candidates) > 0:     
            results.append([dic_ids[candidates[max(candidates.keys())]], rowdf1.delegacion, \
                candidates[max(candidates.keys())], rowdf1.type,rowdf1.transaction, \
                rowdf1.price_dollars, rowdf1.surface])
    return results

def get_last_and_second_to_last(list_):
    '''
    It extracts the last, and second to last elements of a list
    that contains the address of a property. These elements correspond
    to the name of delegaciones (municipalities) and city
    Inputs: List
    Returns: tuple 
    '''
    last_items = []
    second_to_last_items = [] 
    for element in list_:
        if element != None:                            
            last_items.append(element[-1])
            second_to_last_items.append(element[-2])
    return last_items, second_to_last_items 


def median_price_to_csv(transaction_type, building_type ):
    '''
    Creates a csv file.
    Inputs: (strings)
        transaction_type: 'sale' or 'rent'
        building_type: 'house' or 'appartment'
    '''

    if building_type == 'house':
        buildt = 'Casa'
    elif building_type == 'appartment':
        buildt = 'Departamento'
    if transaction_type == 'sale':
        trans = 1
    else:
        trans = 2
        df = dataframe [(all_delegaciones.transaction == trans) & (all_delegaciones.type == buildt)]
        df = df.groupby(['delegacion', 'barrio_ID', 'neighborhood'])['price'].median()
        house_rent_median.to_csv (building_type + "_" + transaction_type + "_" + "median" )

### FIRST PART OF CLEANING ###

files = ['appartmentsale.csv', 'appartmentrent.csv', 'houserent.csv', \
        'housesale.csv']
for doc in files:
    df = pd.read_csv(path + doc, sep = ',')
    #df['name'] = df['Description'][:20]
    df['lat'] = 0
    df['long'] = 0
    df= df.rename(columns = {'Transaction Type': 'transaction', \
                            'Location (Address)':'address', \
                            'Surface (built)': 'surface','Name': \
                            'name','Delegacion': 'delegacion', \
                            'Rooms': 'rooms', 'Type': 'type',\
                            'Neighborhood':'neighborhood'})

    df['transaction']= df['transaction'].fillna(method = 'ffill')
    conditions_1 = [
        (df['Sale price pesos'] > 0),
        (df['Sale price dollars'] > 0),
        (df['Rent price pesos'] > 0),
        (df['Rent price dollars'] > 0)]

    vals1 = [ round(df['Sale price pesos'] / EXCHANGE_RATE ,2), \
    df['Sale price dollars'], round(df['Rent price pesos'] / EXCHANGE_RATE,2),\
    df['Rent price dollars']]
    df['price_dollars'] = np.select(conditions_1, vals1)

    conditions_2 = [(df['transaction'] == 'Rent'),
                  (df['transaction'] == 'Sale')]
    vals2 = [2,1]
    df['transaction'] = np.select(conditions_2,vals2)
    columns_to_drop= ['Rent price dollars','Rent price pesos', 'Maintenance Cost',\
    'Building Age', 'Description','Sale price pesos', \
    'Sale price dollars','Surface (total)', 'Half bathrooms']
    
    for column in columns_to_drop:
        df.drop(column, axis = 1, inplace = True)

    cols = ['type', 'delegacion', 'address', 'neighborhood', 'price_dollars',\
           'transaction', 'lat','long','surface', 'rooms']
    df = df[cols]
    df.to_csv('clean_'+ doc)

#### Second part of cleaning ####

col_names = ['name', 'lat','long','address', 'surface','transaction', 'price', \
'currency', 'type','bathroom','halfb','rooms','parkinglot']
df = pd.read_csv( path + '54903_properties.csv', names = col_names, sep = ',')

ls = []                                                            
for i, r in df.iterrows():
    one_address = r ['address'].split(',')
    if len(one_address) > 2: 
        if (one_address[-1] != one_address[-2]): # These guys only have info for delegacion
            ls.append([one_address])
        else:
            ls.append([None])
    else:
        ls.append([None])


flatten = lambda ls: [item for sublist in ls for item in sublist]  
#(Source: https://stackoverflow.com/questions/952914/making-a-flat-list-out-of-list-of-lists-in-python)
flat_list = flatten(ls)                                                      

last_items = get_last_and_second_to_last(flat_list)[0]

city = list(set(last_items))
for element in flat_list:
    if element != None:
        if element[-1] in city:
            element[-1] = 'Mexico City'
        element[-2] = (element[-2]).lstrip()
        if element[-2] == 'Coyoacán':
             element[-2] = 'Coyoacan'
        if element[-2] == 'Cuajimalpa De Morelos':
             element[-2] = 'Cuajimalpa de Morelos'

second_to_last = get_last_and_second_to_last(flat_list)[1]
city_correct = set(get_last_and_second_to_last(flat_list)[0])
delegaciones = set(second_to_last) - {'Ciudad De México'}

list_clean_addresses = []
for element in flat_list:
    if element == None:
        element = ['NaN']
    list_clean_addresses.append(element)

list_delegaciones = [] 
for element in list_clean_addresses:
    if (element[0] == 'NaN') & (len(element) == 1):
        list_delegaciones.append('NaN')
    elif element[-2] in delegaciones:
         list_delegaciones.append(element[-2])
    elif element[-2] =='Ciudad De México':
        list_delegaciones.append('NaN')

list_neighborhoods =[] 
for element in list_clean_addresses:
    if (element[0] == 'NaN') & (len(element) == 1):
        list_neighborhoods.append('NaN')
    else:
        list_neighborhoods.append(element[-3])

dataframe_neighborhoods = pd.DataFrame(list_neighborhoods, columns=['neighborhood'])
dataframe_delegaciones = pd.DataFrame(list_delegaciones, columns=['delegacion']) 
df['neighborhood'] = dataframe_neighborhoods
df['delegacion']=dataframe_delegaciones
conditions_3 = [(df['currency'] == 11), (df['currency'] == 12)]

vals_3 = [ round(df['price']/ EXCHANGE_RATE,2), df['price']]
df['price_dollars'] = np.select(conditions_3, vals_3)

cols = ['type', 'delegacion', 'address', 'neighborhood', 'price_dollars', 'transaction',\
       'lat','long','surface', 'rooms']
df = df[cols]
df.to_csv('clean_kei_part.csv')

### INTEGRATE PART 1 and PART 2 ###

list_csv = ['clean_kei_part.csv', 'clean_appartmentrent.csv','clean_appartmentsale.csv', \
            'clean_houserent.csv','clean_housesale.csv']

list_of_dataframes = []
for csv in list_csv:
    df = pd.read_csv(csv, sep = ',')
    list_of_dataframes.append(df)
all_data = pd.concat(list_of_dataframes, names = cols)

all_data.neighborhood = all_data.neighborhood.str.normalize('NFKD').str.encode\
                     ('ascii', errors='ignore').str.decode('utf-8').str.upper()

all_data.delegacion = all_data.delegacion.str.normalize('NFKD').str.encode\
                     ('ascii', errors='ignore').str.decode('utf-8').str.upper()

neighborh = pd.read_csv(path +'neighborhoods.csv',\
                         sep = ',', encoding='ISO-8859-1')
neighborh.MUN_NAME = neighborh.MUN_NAME.str.normalize('NFKD').str.encode \
                    ('ascii', errors='ignore').str.decode('utf-8').str.upper()


# This is the data with non missing values
data_nomissingv = all_data[all_data.neighborhood.notnull()]

neighborhoods_list = list(neighborh['SETT_NAME'])
delegaciones_list = list (set((neighborh['MUN_NAME'])))
data_frame_set = []
column_names = ['barrio_ID','delegacion', 'neighborhood', 'type', 'transaction',\
 'price', 'surface']
for delegacion in delegaciones_list:
    neighborhoods_delegacion = neighborh.loc[neighborh['MUN_NAME'] == \
    delegacion]
    delegacion_data = data_nomissingv.loc[data_nomissingv['delegacion'] ==\
     delegacion]
    data_frame_pair = delegacion_data, neighborhoods_delegacion
    matches_by_delegacion = get_neighborhood(data_frame_pair[0],data_frame_pair[1])
    df_delegacion = pd.DataFrame(matches_by_delegacion, columns = column_names)
    data_frame_set.append(df_delegacion)

all_delegaciones = pd.concat(data_frame_set)
all_delegaciones = all_delegaciones.drop_duplicates()



house_rent = all_delegaciones[(all_delegaciones.transaction == 2) & (all_delegaciones.type == 'Casa')]
house_rent_median = house_rent.groupby(['delegacion', 'barrio_ID', 'neighborhood'])['price'].median()
house_rent_median.to_csv ('house_rent_median.csv')

house_sale= all_delegaciones[(all_delegaciones.transaction == 1) & (all_delegaciones.type == 'Casa')]
house_sale_median = house_sale.groupby(['delegacion', 'barrio_ID', 'neighborhood'])['price'].median()
house_sale_median.to_csv('house_sale_median.csv')

appartment_rent= all_delegaciones[(all_delegaciones.transaction == 2) & (all_delegaciones.type == 'Departamento')]
appartment_rent_median = appartment_rent.groupby(['delegacion', 'barrio_ID', 'neighborhood'])['price'].median()
appartment_rent_median.to_csv('appartment_rent_median.csv')

appartment_sale= all_delegaciones[(all_delegaciones.transaction == 1) & (all_delegaciones.type == 'Departamento')]
appartment_sale_median = appartment_sale.groupby(['delegacion', 'barrio_ID', 'neighborhood'])['price'].median()
appartment_sale_median.to_csv('appartment_sale_median.csv')


