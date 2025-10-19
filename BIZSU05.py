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
    print("extract_product_data called")
    print(html_content[:500])  # Csak az első 500 karaktert jeleníti meg a hosszú tartalmak esetén
    # Regex minta a products adatok kinyerésére
    products_pattern = r'products="({.*?})"'
    products_match = re.search(products_pattern, html_content, re.DOTALL)
    print("products_match:", products_match)
    if not products_match:
        return {}


        # JSON dekódolás (HTML entity-k helyettesítése)
    products_json = products_match.group(1)
    products_json = products_json.replace('&quot;', '"')
    products_data = json.loads(products_json)
    print("products_data keys:", products_data["data"])
    try:
        for product in products_data["data"]:
            print( BASE_URL + product[0]["seo"], product[0]["CikkKod"], product[0]["CnevText"])
            termek_urls.append(BASE_URL + product[0]["seo"])
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
    for page in range(2, products_data['last_page'] + 1):
        print(f"Oldal: {page}" ,url + f"&page={page}")
        resp = requests.get(url + f"&page={page}", timeout=5)

        more_products_data = extract_product_data(str(resp.text))
        result['products'] = parse_products(more_products_data)
    if products_data:
        result['products'] = parse_products(products_data)
        result['pagination'] = {
            'current_page': products_data.get('current_page', 1),
            'last_page': products_data.get('last_page', 1),
            'total': products_data.get('total', 0),
            'per_page': products_data.get('per_page', 10),
            'next_page_url': products_data.get('next_page_url', '')
        }

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

            # Adatok kinyerése
            extracted_data = extract_all_variables(resp.text)

            # Eredmények megjelenítése
            #print("=== KINYERT ADATOK ===")
            #print(f"Termékek száma: {len(extracted_data.get('products', []))}")
            #print(f"Oldal információs: {extracted_data.get('pagination', {})}")
            #print(f"Keresési paraméterek: {extracted_data.get('searchquery', '')}")

            # Első termék részletei
            #if extracted_data.get('products'):
             #   first_product = extracted_data['products'][0]
                #print("\n=== ELŐSŐ TERMÉK ===")
                #for key, value in first_product.items():
                    #print(f"{key}: {value}")
            #print("ok")

        except Exception as e:
           print(f"Hiba: {e}")


    with open(TERMEK_FILE, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            for termek_url in termek_urls:
                writer.writerow([termek_url])

print(f"✅ 🚀 IlKész! Az eredmény az {os.path.abspath(OUTPUT_FILE)} fájlban található.")