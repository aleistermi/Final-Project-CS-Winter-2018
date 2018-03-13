# CS122: Course Search Engine Part 1
#
# Keisuke Yokota
#

import re
import bs4
import queue
import json
import csv
import requests
import time


# necessary to run this statring url in 4 combinations as follows
# (renta, casa), (renta, departamento), (venta, casa), (venta, departamento)
starting_url = ("https://inmuebles.metroscubicos.com/"
                "casas/renta/distrito-federal/_Desde_49")


#  "Original"
def go(filename, starting_url=starting_url):
    '''
    Crawl a real estate web page and generates a CSV file.

    Inputs:
        filename: a name for the CSV as an output (string)
        starting_url: a URL to start crawling

    Outputs:
        CSV file.
    '''
    q_url_waiting = get_page_url(starting_url)
    lst = get_properties_data(q_url_waiting)
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
def get_properties_data(q_url_waiting):
    '''
    get a queue of properties'URLs to crawl.

    Inputs:
        q_url_waiting: queue of URLs to crawl

    Outputs:
        output_lst: a list of list of the real estate data
    '''
    dic = {}
    output_lst = []
    while not q_url_waiting.empty():
        url_to_crawl = q_url_waiting.get()
        r_object = check(url_to_crawl)
        if r_object:
            r_object.encoding = r_object.apparent_encoding
            html = r_object.text.encode(r_object.encoding)
            soup = bs4.BeautifulSoup(html, "html.parser")            
            for div in soup.find_all("div", {'class': 'item-title'}):
                new_url = div.a['href']
                if new_url:
                    if new_url not in dic.keys():             
                        dic[new_url] = True  
                        l = get_data(new_url)
                        output_lst.append(l)
        else:
            break
    return output_lst


#  "Original"
def get_data(url):
    '''
    get property's data.

    Inputs:
        url: a property's URL (string)

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
        # collecting name information
        name_div = soup.find("div",
                            {'class': 'vip-product-info__development__info'})
        name  = name_div.find('h1').getText().strip()
        # collecting price information
        article = soup.find("article",
                            {'class': 'vip-price ch-price'})
        currency_price = article.find('strong').getText()
        price_lst = currency_price.split()
        price = price_lst[1]
        if price_lst[0].strip() == '$':
            currency = 11
        else:
            currency = 12
        # collecting address information
        address_tag = soup.find("section",
                                {'class': 'vip-section-map container'})
        address = address_tag.find('h2').getText().strip()
        # collecting geographical (latitude and lontitude) information
        # (In this web site we cannot have access to them)         
        gps_lat = ""
        gps_lon = ""
        # collecting type and operation information
        li = soup.find("li",
                        {'class': 'vip-title-breadcrumb'})
        title = li.get("title")
        if 'venta' in title.lower().split():
            operation = 1
        elif 'renta' in title.lower().split():
            operation = 2
        if 'departamentos' in title.lower().split():
            tipo = 'Departamento'
        elif 'casas' in title.lower().split():
            tipo = 'Casa'                            
        # collecting size, bedroom, bathroom information
        size = ''
        recamaras = ''
        banio = ''
        square_word = ['m² construidos' ,'m² de terreno']
        if soup.find("ul",
                            {'class': 'vip-product-info__attributes-list'}):
            ul = soup.find("ul",
                            {'class': 'vip-product-info__attributes-list'})
            for li in ul.find_all("li", 
                            {'class': 'vip-product-info__attribute_element'}):

                if li.find('p').getText().strip() in square_word:
                    size_lst = li.find('span').getText().strip().split()
                    size = size_lst[0]
                elif li.find('p').getText().strip() == 'Recámaras':
                    recamaras_lst = li.find('span').getText().strip().split()
                    recamaras = recamaras_lst[0]
                elif li.find('p').getText().strip() == 'Baños':
                    banio_lst = li.find('span').getText().strip().split()
                    banio = banio_lst[0]
        else:
            size = ''
            recamaras = ''
            banio = ''
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