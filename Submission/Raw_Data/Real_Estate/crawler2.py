# CS122: Project (Web scraping for properties data)
#
# Keisuke Yokota

import re
import bs4
import queue
import json
import csv
import requests
import time


# necessary to run this statring url in 4 combinations as follows
# (renta, casa), (renta, departamento), (venta, casa), (venta, departamento)
starting_url = ("https://www.icasas.mx/renta/habitacionales-departamentos"
                "-distrito-federal-2_3_1_0_0_0/t_casas,casas-condominio#")


#  "Original"
def go(filename, room_operation, room_type, starting_url=starting_url):
    '''
    Crawl a real estate web page and generates a CSV file.

    Inputs:
        room_type: 'Casa'(house) or 'Departamento' (string)
        room_operation: 'venta'(for sale) or 'renta'(for rent) (string)
        filename: a name for the CSV as an output (string)
        starting_url: a URL to start crawling

    Outputs:
        CSV file.
    '''
    q_url_waiting = get_page_url(starting_url)
    lst = get_properties_data(q_url_waiting,
                             room_operation,
                             room_type)
    return create_csv_file(lst, filename)


#  "Modified"
def check(url):
    '''
    Check the connection with the server and continue to connect
    with the server if the connection refused.

    Inputs:
        url: Web page's URL where we try to get information (string)

    Outputs:
        r_object: Request object
    '''
    r_object = ''
    while r_object == '':
        try:
            r_object = requests.get(url)
        except:
            print()
            print("Connection is refused by the server..")
            print("Wait for 5 seconds")
            print()
            time.sleep(5)
            print("Let me continue")
            print()
            continue
    return r_object


#  "Original"
def get_page_url(starting_url):
    '''
    get a queue of pages'URLs to crawl.

    Inputs:
        starting_url: A URL to start crawling

    Outputs:
        q_url_waiting: a queue of the URLs to crawl in order
    '''
    q_url_found = queue.Queue()
    q_url_waiting = queue.Queue()
    dic = {}
    q_url_found.put(starting_url)
    while not q_url_found.empty():
        url_to_crawl = q_url_found.get()
        q_url_waiting.put(url_to_crawl)
        r_object = check(url_to_crawl)
        if r_object:
            r_object.encoding = r_object.apparent_encoding
            html = r_object.text.encode(r_object.encoding)              
            soup = bs4.BeautifulSoup(html, "html.parser")
            link = soup.find("link", {'rel': 'next'})
            if link:
                new_url = link.get("href")
                if new_url:
                    if new_url not in dic.keys():             
                        dic[new_url] = True
                        q_url_found.put(new_url)
        else:
            break
    return q_url_waiting


#  "Original"
def get_properties_data(q_url_waiting, room_operation, room_type):
    '''
    get a queue of properties'URLs to crawl.

    Inputs:
        q_url_waiting: queue of URLs to crawl (queue)
        room_type: 'Casa'(house) or 'Departamento' (string)
        room_operation: 'venta'(for sale) or 'renta'(for rent) (string)

    Outputs:
        output_lst: a list of list of the real estate data
    '''
    limiting_domain = "https://www.icasas.mx"
    dic = {}
    output_lst = []
    while not q_url_waiting.empty():
        url_to_crawl = q_url_waiting.get()
        r_object = check(url_to_crawl)
        if r_object:
            r_object.encoding = r_object.apparent_encoding
            html = r_object.text.encode(r_object.encoding)              
            soup = bs4.BeautifulSoup(html, "html.parser")
            for H2 in soup.find_all("h2", {'itemprop':'name'}):
                new_url = H2.a['href']
                if new_url:
                    new_url = util.remove_fragment(new_url)
                    lst = [limiting_domain]
                    lst.append(new_url)     
                    new_url = ''.join(lst)
                    if new_url not in dic.keys():             
                        dic[new_url] = True       
                        l = get_data(new_url,
                                     room_operation,
                                     room_type)
                        output_lst.append(l)
        else:
            break
    return output_lst


#  "Original"
def get_data(url, room_operation, room_type):
    '''
    get property's data.

    Inputs:
        url: a property's URL (string)
        room_type: 'Casa'(house) or 'Departamento' (string)
        room_operation: 'venta'(for sale) or 'renta'(for rent) (string)

    Outputs:
        lst: a list of the real estate data in the URL
            [name, gps_lat, gps_lon, address, size, operation, price, 
                currency, tipo, banio, mediobanio, recamaras, estacionamiento]
    '''
    lst = []
    url_to_crawl = url
    r_object = check(url_to_crawl)
    if r_object:
        r_object.encoding = r_object.apparent_encoding
        html = r_object.text.encode(r_object.encoding)
        soup = bs4.BeautifulSoup(html, "html.parser")
        section = soup.find("section",{'class':'detail_scroll'})
        # collecting name information
        name_lst = re.findall(r"[\w']+", section.find('span').getText())
        name  = ' '.join(name_lst)
        # collecting price information
        price_lst = section.find("p").getText().lstrip('Desde').split()
        price = price_lst[0]
        if price_lst[1].strip() == 'MX$':
            currency = 11
        else:
            currency = 12
        if room_operation == 'venta':
            operation = 1
        elif room_operation == 'renta':
            operation = 2
        # collecting room type information
        tipo = room_type   
        # collecting address information
        address_tag = soup.find("input", {'id': 'locationShown'})
        address = address_tag.get("value")
        # collecting geographical (latitude and lontitude) information
        if soup.find("button", {'id': 'see-map'}):
            gps_lat = soup.find("button", {'id': 'see-map'}).get("data-x")
            gps_lon = soup.find("button", {'id': 'see-map'}).get("data-y")
        else:
            gps_lat = ""
            gps_lon = ""               
        # collecting size information
        if section.find("li",{'class':"dimensions"}):
            size = section.find("li",
                                {'class':"dimensions"}).getText().rstrip('m2')
        else:
            size = 0
        # collecting room information
        if section.find("li",{'class':"bedrooms"}):
            recamaras = re.findall("\d*",section.find("li",
                                {'class':"bedrooms"}).getText())[0]
        else:
            recamaras = 0
        if section.find("li",{'class':"bathrooms"}):
            banio = re.findall("\d*",section.find("li",
                                {'class':"bathrooms"}).getText())[0]
        else:
            banio = 0
        # collecting middle bathroom and parking lot information
        # (In this web site we cannot have access to them)                
        mediobanio = ''
        estacionamiento = ''
        lst.append([name, gps_lat, gps_lon, address, size, operation, price, 
                currency, tipo, banio, mediobanio, recamaras, estacionamiento])
    return lst


#  "Original"
def create_csv_file(lst, filename):
    '''
    Create a csv file.

    Inputs:
        list: list of list
        filename: the name for the CSV.

    Outputs:
        CSV file.
    '''
    with open(index_filename, "w", newline="") as f:
        writer = csv.writer(f, delimiter="|")
        writer.writerows(lst)
        f.close()