import csv
import requests
from bs4 import BeautifulSoup
import os

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
for url in url_list:
    try:
        resp = requests.get(url, timeout=10)
        resp.encoding = resp.apparent_encoding  # helyes kódolás felismerése
        soup = BeautifulSoup(resp.text, "html.parser")

        # oldal szöveg (title + body)
        title = soup.title.string if soup.title else ""
        body_text = soup.get_text(separator=" ", strip=True)
        full_text = (title + " " + body_text).strip()

        # csak az első 200 karakter
        url_texts.append(full_text[:200])

    except Exception as e:
        url_texts.append(f"Hiba: {e}")

# --- 3. ADAT.csv kiírás ---
with open(OUTPUT_FILE, "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["URL_LIST", "URL_TEXT"])  # fejléc
    for url, text in zip(url_list, url_texts):
        writer.writerow([url, text])

print(f"✅ Kész! Az eredmény az {os.path.abspath(OUTPUT_FILE)} fájlban található.")
