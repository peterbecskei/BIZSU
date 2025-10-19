import csv
import requests
#from bs4 import BeautifulSoup
import os
import html
import time
import sys
from datetime import datetime
import json
import re
from typing import List, Dict, Any

#html_content = ""
# fájlnevek
INPUT_FILE = "URL_LIST.csv"
OUTPUT_FILE = "ADAT.csv"
TERMEK_FILE = "TERMEK_URL.csv"
BASE_URL = "https://zsu.hu/termeklap/"
termek_urls = []

def extract_product_data(html_content: str) -> Dict[str, Any]:
    """
    Kinyeri a termékadatokt a HTML-ből
    """
    # Regex minta a products adatok kinyerésére
    products_pattern = r'products="({.*?})"'
    products_match = re.search(products_pattern, html_content, re.DOTALL)

    if not products_match:
        return {}


        # JSON dekódolás (HTML entity-k helyettesítése)
    products_json = products_match.group(1)
        #print(products_json)
    products_json = products_json.replace('&quot;', '"')
        #print(products_json)
    products_data = json.loads(products_json)
        #print(products_data)
        #print(products_data["data"]["current_page"])
    #print("product_data:",   products_data["data"] )
    #print("type:",   type(products_data["data"]) )
    #print("map:",   map( lambda x: type(x), products_data["data"]) )
    #print("len:",   len(products_data["data"]) )
    #print("data[0]:",   products_data["data"][0] )
    #print("type data[0]:",   type(products_data["data"][0]) )
        #'from': 11, 'last_page': 13, 'next_page_url': 'https://zsu.hu/cikkszamkereso?page=3', 'path': 'https://zsu.hu/cikkszamkereso', 'per_page': 10, 'prev_page_url': 'https://zsu.hu/cikkszamkereso?page=1', 'to': 20, 'total': 127}
    #print( "last_page:", products_data["last_page"] )
    #print( "current_page:", products_data["current_page"] )
    #print( "per_page:", products_data["per_page"] )
    print( "total:", products_data["total"] )
    print( "from:", products_data["from"] )
    print( "to:", products_data["to"] )

    if products_data["current_page"]==1:
        for product in products_data["data"]:
            print( BASE_URL + product[0]["seo"], product[0]["CikkKod"], product[0]["CnevText"])
            termek_urls.append(BASE_URL + product[0]["seo"])
    else:
        #dik= products_data["current_page"] -1
        #dik2= dik * products_data["per_page"]
        #print("dik:", dik)
        #print("dik2:", dik2)
        #key1 = list(products_data["data"].keys())[0]
        #keys = list(products_data["data"].keys())

        #print("keys:", keys)
        #value1 = products_data["data"][key1]
        #ezek a values kellenek
        values = list(products_data["data"].values())
        print("values:", values)
        #for _ in range(dik2):
        #    products_data["data"].pop(0)
        for product in values:
            #print(product)
            print(BASE_URL + product[0]["seo"], product[0]["CikkKod"], product[0]["CnevText"])
            termek_urls.append(BASE_URL + product[0]["seo"])
        #with open(TERMEK_FILE, "w", encoding="utf-8", newline="") as f:
        #    writer = csv.writer(f)
        #    writer.writerow(["TERMEK_URL"])  # fejléc
    try:
        print("End of extact:")
        #for product in products_data["data"]:
        #    print( BASE_URL + product[0]["seo"], product[0]["CikkKod"], product[0]["CnevText"])
        #    termek_urls.append(BASE_URL + product[0]["seo"])
            #print(dir(product))
            #print(f"{key}: {products_data[key]}")
        #print(len(products_data), products_data["data"][1] )
        #print(dir(products_data.data))

        return products_data
    except json.JSONDecodeError as e:
        print(f"JSON dekódolási hiba: {e}")
        return {}


def parse_products(products_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Feldolgozza a termékadatokat
    """
    products = []

    if 'data' not in products_data:
        return products

    for product_group in products_data['data']:
        for product in product_group:
            # Alap termék információk
            product_info = {
                'cikkszam': product.get('CikkKod', ''),
                'termek_nev': product.get('CnevText', ''),
                'gyarto': product.get('Gyarto', ''),
                'ar_netto': product.get('KiskerAr', ''),
                'ar_brutto': product.get('br_full_price', ''),
                'keszlet': product.get('Keszlet', ''),
                'kep': product.get('Kep1', ''),
                'tcd_artnr': product.get('TCD_ARTNR', ''),
                'tcd_gyarto': product.get('TCD_GYARTO', ''),
                'seo_url': product.get('seo', ''),
                'keszlet_info': product.get('stock_html', '')
            }
            products.append(product_info)

    return products


def extract_all_variables(html_content: str) -> Dict[str, Any]:
    """
    Minden változót kinyer a HTML-ből
    """
    result = {}

    # Products adatok
    products_data = extract_product_data(html_content)
    print(products_data['last_page'])
    #print(url.find("?page="))
    print(url)
    #if url.find("?page=") >0 :
    #    page_sign = "&page=1"
    #    print("page_sign &page=1")
    if url.find("?page=")  < 0:
        print("page_sign no ")
        for page in range(2, products_data['last_page'] +1):
            print(f"Oldal: {page}" ,url + f"&page={page}")
            with open(OUTPUT_FILE, "a", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
            # writer.writerow(["URL_LIST", "URL_TEXT"])  # fejléc
            #for url, text, extract in zip(url_list, url_texts, url_extracted):
                writer.writerow([url + f"&page={page}"])
    #    resp = requests.get(url + f"&page={page}", timeout=5)
    #    more_products_data = extract_product_data(resp.text)
    #    result['products'] = parse_products(more_products_data)


    # Egyéb változók kinyerése
    patterns = {
        'productnumbers': r'productnumbers="(\[.*?\])"',
        'manufacturers': r'manufacturers="({.*?})"',
        'filtersconfig': r'filtersconfig="({.*?})"',
        'searchtype': r'searchtype="(\d+)"',
        'searchquery': r'searchquery="([^"]*)"'
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, html_content, re.DOTALL)
        if match:
            try:
                if key in ['manufacturers', 'filtersconfig']:
                    # JSON objektumok
                    json_str = match.group(1).replace('&quot;', '"')
                    result[key] = json.loads(json_str)
                elif key == 'productnumbers':
                    # JSON tömb
                    json_str = match.group(1).replace('&quot;', '"')
                    result[key] = json.loads(json_str)
                else:
                    # Egyszerű string értékek
                    result[key] = match.group(1)
            except json.JSONDecodeError:
                result[key] = match.group(1)

    return result


# Használat
if __name__ == "__main__":
    # A HTML tartalmat ide kell beilleszteni


    # --- 1. URL_LIST betöltése ---
    url_list = []
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if row:  # ne vegye fel az üres sorokat
                url_list.append(row[0].strip())

    # --- 2. Site view lekérése ---
    url_texts = []
    url_extracted = []
    i = 0
    timestamp = time.time()
    for url in url_list:
        try:
            i = i + 1
            print(f"Feldolgozás alatt: {url}")

            resp = requests.get(url, timeout=5)
            # print(type(resp))
            #print(resp.text)
            # Adatok kinyerése
            extracted_data = extract_all_variables(resp.text)

            # Eredmények megjelenítése
            #print("=== KINYERT ADATOK ===")
            #print(f"Termékek száma: {len(extracted_data.get('products', []))}")
            #print(f"Oldal információs: {extracted_data.get('pagination', {})}")
            #print(f"Keresési paraméterek: {extracted_data.get('searchquery', '')}")

            # Első termék részletei
            #if extracted_data.get('products'):
            #    first_product = extracted_data['products'][0]
                #print("\n=== ELŐSŐ TERMÉK ===")
                #for key, value in first_product.items():
                    #print(f"{key}: {value}")
            #print("ok")
            url_extracted.append(extracted_data['products'][0])
            url_texts.append("https://zsu.hu/termeklap/" + extracted_data['products'][0]['seo_url'])


        except Exception as e:
            url_texts.append(f"Hiba: {e}")

    #with open(OUTPUT_FILE, "w", encoding="utf-8", newline="") as f:
    #        writer = csv.writer(f)
            # writer.writerow(["URL_LIST", "URL_TEXT"])  # fejléc
    #        for url, text, extract in zip(url_list, url_texts, url_extracted):
    #            writer.writerow([url, text, extract])
    with open(TERMEK_FILE, "a", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            for termek_url in termek_urls:
                writer.writerow([termek_url])

print(f"✅ 🚀 IlKész! Az eredmény az {os.path.abspath(OUTPUT_FILE)} fájlban található.")