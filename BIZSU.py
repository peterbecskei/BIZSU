import csv
import requests
#from bs4 import BeautifulSoup
import os
import html
import json
import re
import time


#url = "https://zsu.hu/header-search/api/start-product-name-search"
#payload = {"searchString": "302540"}

#url = "https://zsu.hu/header-search/api/getHeaderSearches"
#payload = {"searchString": "302540"}



#response = requests.post(url, json=payload)
#response = requests.post(url)


#print("Státusz kód:", response.status_code)
#print("Válasz:", response.text)
#system.exit()

# fájlnevek
INPUT_FILE = "URL_LIST.csv"
OUTPUT_FILE = "ADAT.csv"

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
i=0
#timestamp = time.time()
for url in url_list:
    try:
        i=i+1
        print(f"Feldolgozás alatt: {url}")


        #def myfunc(a):
        #    return len(a)
        #x = map(myfunc, ('apple', 'banana', 'cherry'))
        #print(x)
        #print(type(x))
        # convert the map into a list, for readability:
        #print(list(x))

        resp = requests.get(url, timeout=5)
        #print(type(resp))
        #print(type(resp.text))
        #print(type(resp))
        #print(dir(resp))
        print(resp.elapsed)
        #print(resp.headers)

        #print(dir(resp.cookies))

        #print(map(resp))
        #print("resp.cookies.get_dict")
        #print(resp.cookies.get_dict)
        #print(resp.cookies.items)
        #print(resp.cookies.values)

        #print(resp.is_redirect)

        #print(resp._content)
        #print(resp.json)
        #print(resp.links)

        #print(resp.next)

        #print(resp.__sizeof__())
        #print(resp.__static_attributes__)
        #print(resp.__str__)
        #print(resp.headers['Content-Length'])

        #product_search = str(resp.text[1000:2000])
        #print(product_search)
        #print(type(product_search))
        #print(resp.text[154416:3000])

        start_index0 = resp.text.find("productnumbers=")
        start_index1 = resp.text.find("filtersconfig=")
        #start_index = resp.text.find("headerContent")
        start_product_list = resp.text.find("product-list-gate")+18
        end_product_list = resp.text.find("> </product-list-gate")
        #print(start_index)
        procuct_list_content = resp.text[start_product_list:end_product_list]

        extracted_content = resp.text[start_product_list:end_product_list]

        #st = search_content.find('e',0) #  product_search_results_container")
       # print(st)
        print(extracted_content)
        #content = resp.content.replace('e9', 'é')
        #resp.encoding = resp.apparent_encoding  # helyes kódolás felismerése
        #print(resp.content.decode('utf-8'))
        #content = resp.content.decode('utf-8', errors='ignore')
        #content = decode(resp.content)
        #print(content)
        # HTML elemzés

        #soup = BeautifulSoup(resp.text, "html.parser")


        # oldal szöveg (title + body)
        #title = soup.title.string if soup.title else ""
        #body_text = soup.get_text(separator=" ", strip=True)
        #full_text = (title + " " + body_text).strip()

        # csak az első 200 karakter
        # url_texts.append(full_text[:12000])

        #search_results = soup.find(id="product_search_results_container")
        #search_content = str(search_results)
        #print(search_content)
        # speciális karakterek javítása
        #st=1000
        #search_content = resp.text[st:st+1000]
        content = (extracted_content.replace('\\u00c1', 'Á').
                   replace('\\u0151', 'ö').
                   replace('\\u00fc', 'ü').
                   replace('\\u00e9', 'é').
                   replace('\\u00ed', 'í').
                   replace('\\u0171', 'ű').
                   replace('\\u00f3', 'ó').
                   replace('\\u00e1', 'á').
                   replace('\\u00e7', 'ç').
                   replace('\\u00f6', 'ö').
                   replace('\\u00fc', 'ü').
                   replace('\\u00e4', 'ä'))
        content = (content.replace('&quot;', "'").
        replace("\\u0150", "✅").
        replace("\\u00d6", "Ö").
        replace("lt;", "<").
        replace("&gt;", ">"))  # .replace("&gt;", ">").replace("&amp;", "&")
        print(content)
        # A fix kulcsok listája
        keys = ['productNumber', "CikkKod", 'stock_html', 'tcd_artnr_seo', 'tcd_gyarto_seo','seo', 'Keszlet', 'Gyarto', 'KiskerAr', 'TCD_ID', 'ArDatum', 'RefeKeszlet', 'AlapEgys', 'Suly', 'Kep1','CnevText','TCD_ARTNR','TCD_DLNR','TCD_GYARTO','TCD_ARTNR_SAJAT','TCD_DLNR_SAJAT','gyarto','tcd_gyarto','br_price','customStockOrder','netFullPrice','br_full_price','discountPercent'
                ,'ADV_TCD_ARTNR','CUSTOM_TCD_ARTNR','alternative_products','askForInformation','cikkkod','productImages','firstImageExt'] #,'upmValue','tcd_artnr_seo','tcd_gyarto_seo','seo','stock_html']
#'CnevText','TCD_ARTNR','TCD_DLNR','TCD_GYARTO','TCD_ARTNR_SAJAT','TCD_DLNR_SAJAT','gyarto','tcd_gyarto','br_price','customStockOrder','netFullPrice','br_full_price','discountPercent','tcd_artnr_seo':'30337_01','tcd_gyarto_seo':'lemf_rder','seo':'lem_3033701_br','stock_html':'&<div class=\'left\'> &<div class=\'display-flex margin-x-auto mb-5\'> &<img src=\'\/themes\/frontend\/images\/stock.png\' width=\'22\' height=\'22\'> &<i>Készlet&<\/i> &<div class=\'info-box-btn\'> &<img src=\'\/themes\/frontend\/images\/svg\/info.svg\' width=\'18\' height=\'18\'>         &<span>Munkanapokon megrendeléstöl számított 3-5 órán belül a kiválasztott üzletben átvehetö.&<\/span>  &<\/div> &<\/div> &<b class=\'display-flex flex-column flex-column-mobile\'> &<span class=\'display-flex margin-x-auto text-center\'>  &<span class=\'display-flex\'> &<img src=\'\/themes\/frontend\/images\/stock-narancs.svg\' class=\'ok beszallito\' width=\'20px\'> &<span class=\'stock-info\'>3-5 órán belül&<\/span>  &<\/span>  &<\/span> &<\/b> &<\/div> &<div class=\'right\'> &<div class=\'display-flex margin-x-auto mb-5\'> &<img src=\'\/themes\/frontend\/images\/svg\/shipping.svg\' width=\'24\' height=\'24\'> &<i>Szállítás&<\/i> &<div class=\'info-box-btn\'> &<img src=\'\/themes\/frontend\/images\/svg\/info.svg\' width=\'18\' height=\'18\'>  &<span>A termék beérkezésétöl számított 1-2 munkanapon belül átadjuk a rendelést a futárszolgálatnak.&<\/span>  &<\/div> &<\/div> &<b class=\'display-flex flex-column flex-column-mobile\'> &<span class=\'display-flex margin-x-auto text-center\'> &<img src=\'\/themes\/frontend\/images\/stock-narancs.svg\' class=\'ok beszallito\' width=\'20px\'>  &<span class=\'stock-info\'>&<p class='text-left'>1-2 munkanap&<\/p>&<\/span>  &<\/span> &<\/b> &<\/div>'}]],'from':1,'last_page':1,'next_page_url':null,'path':'https:\/\/zsu.hu\/cikkszamkereso','per_page':10,'prev_page_url':null,'to':1,'total':1}" searchquery="LEM_3033701" searchtype="10" type="1"> </product-list-gate> </div>
#{'productNumber': None, 'CikkKod': 'LEM 3033701 *BR', 'Keszlet': 'B', 'Gyarto': 'LEMFÖRDER', 'KiskerAr': '17770.6386', 'TCD_ID': '35', 'ArDatum': '2025-09-18 21:52:46', 'RefeKeszlet': 'I', 'AlapEgys': '1', 'Suly': '0',
        extracted = {}

        for key in keys:
            # Pattern: 'kulcs':'érték' – az érték single quote-ok között, és nem tartalmaz belső ' -et (ha igen, finomítsd a pattern-t)
            pattern = rf"'{key}':'([^']*)'"
            match = re.search(pattern,content)
            if match:
                extracted[key] = match.group(1)
            else:
                extracted[key] = None  # Ha nincs találat

        # Kiírás (vagy írd fájlba/Excelbe ha kell)
        #dt=  time.time() - timestamp


        #print(i,dt, url, extracted)
        print( extracted)
        url_extracted.append(extracted)
        url_texts.append(content)
        #print(search_results)
        #ss1 =ss.replace('\u0151', 'ö')
        #ss2 = ss1.replace('\u00fc', 'ü').strip()
        #print(ss)
        # HTML entity dekódolás
        #decoded = html.unescape(search_results)

        # UTF-8 karakterek javítása
        #fixed_text = decoded.encode('latin-1').decode('utf-8', errors='ignore')

        #print(fixed_text)
        # JSON-ként értelmezve
        #try:
        #    json_str = '{"' + search_results.replace('":"', '":"').replace('","', '","') + '}'
        #    data = json.loads(json_str)
        #    print(f"JSON adat: {data}")
        #except:
        #    print("Nem valid JSON formátum")
        #print(search_results.prettify())
        #url_texts.append(soup.find(id="product_search_results_container"))

    except Exception as e:
        url_texts.append(f"Hiba: {e}")

# --- 3. ADAT.csv kiírás ---
with open(OUTPUT_FILE, "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    #writer.writerow(["URL_LIST", "URL_TEXT"])  # fejléc
    for url, text, extract in zip(url_list, url_texts,url_extracted):
        writer.writerow([url, text,extract])




print(f"✅ 🚀 IlKész! Az eredmény az {os.path.abspath(OUTPUT_FILE)} fájlban található.")
