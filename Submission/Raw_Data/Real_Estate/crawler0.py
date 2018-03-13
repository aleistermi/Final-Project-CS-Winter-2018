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
starting_url = "http://century21mexico.com/casa/venta/Ciudad-De-Mexico"


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
    limiting_domain = "http://century21mexico.com"
    q_url_found = queue.Queue()
    q_url_waiting = queue.Queue()
    dic = {}
    q_url_found.put(starting_url)
    while not q_url_found.empty():
        url_to_crawl = q_url_found.get()
        q_url_waiting.put(url_to_crawl)
        r_object = check(url_to_crawl)
        if r_object:                
            html = r_object.text.encode(r_object.encoding)              
            soup = bs4.BeautifulSoup(html, "html.parser")    
            pages_div = soup.find("div", {'class': 'col-sm-12 text-center'})
            for a in pages_div.find_all("a"):
                new_url = a.get("href")
                if new_url:
                    lst = [limiting_domain]
                    lst.append(new_url)     
                    new_url = ''.join(lst)
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
    limiting_domain = "http://century21mexico.com"
    dic = {}
    output_lst = []
    while not q_url_waiting.empty():
        url_to_crawl = q_url_waiting.get()
        r_object = check(url_to_crawl)
        if r_object:
            html = r_object.text.encode(r_object.encoding)              
            soup = bs4.BeautifulSoup(html, "html.parser")    
            for thumbnail_div in soup.find_all("div", {'class': 'thumbnail'}):
                new_url = thumbnail_div.a['href']
                if new_url:
                    lst = [limiting_domain]
                    lst.append(new_url)     
                    new_url = ''.join(lst)
                    print(new_url)
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
        padding_div = soup.find_all("div", {'style': 'padding: 0px 15px;'})
        for div in padding_div:
            if div.find('h4'):
                name  = div.find('h4').getText().strip()
        # collecting price information
        price = soup.find("meta",{'name':"precio"}).get("content")
        currency = soup.find("meta",{'name':"moneda"}).get("content")
        if currency == "MXN":
            currency = 11
        else:
            currency = 12
        # collecting address information
        address_div = soup.find("div", {'itemprop': 'address'})
        sub_lst = []
        for span in address_div.find_all('span'):
            sub_lst.append(span.getText())
        address = ','.join(sub_lst)
        # collecting geographical (latitude and lontitude) information
        geo_div = soup.find("div", {'itemprop': 'geo'})
        sub_lst = []
        if geo_div:
            for geo in geo_div.find_all('meta'):
                sub_lst.append(geo.get("content"))
            gps_lat = sub_lst[0]
            gps_lon = sub_lst[1]
        else:
            gps_lat = ""
            gps_lon = ""
        # collecting size information
        size = soup.find("meta",{'name':"MC"}).get("content")
        # collecting type, operation, bath-, bed-room, parking lot information
        tipo = soup.find("meta",{'name':"tipoInmueble"}).get("content")
        operation = soup.find("meta",{'name':"tipoOperacion"}).get("content")
        banio = soup.find("meta",{'name':"banio"}).get("content")
        mediobanio = soup.find("meta",{'name':"mediobanio"}).get("content")
        recamaras = soup.find("meta",{'name':"recamaras"}).get("content")
        estacionamiento = soup.find("meta",{'name':"estacionamiento"}).get("content")            
        if operation == "venta":
            operation = 1
        elif operation == "renta":
            operation = 2
        for i in [name, gps_lat, gps_lon, address, size, operation, price, 
                    currency, tipo, banio, mediobanio, recamaras, estacionamiento]:
            lst.append(i)
        print(lst)
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