# scraper.py
import csv
import requests
import os
import html
import time
import sys
from datetime import datetime
import json
import re
from typing import List, Dict, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ProductScraper:
    """Main class for scraping product data from ZSU website"""

    def __init__(self, base_url: str = "https://zsu.hu/termeklap/"):
        self.base_url = base_url
        self.termek_urls = []

    def extract_product_data(self, html_content: str) -> Dict[str, Any]:
        """
        Extract product data from HTML content
        """
        print("Extracting product data...")
        products_pattern = r'products="({.*?})"'
        products_match = re.search(products_pattern, html_content, re.DOTALL)

        if not products_match:
            return {}

        try:
            products_json = products_match.group(1).replace('&quot;', '"')
            products_data = json.loads(products_json)

            for product in products_data.get("data", []):
                if product and len(product) > 0:
                    seo_url = product[0].get("seo", "")
                    cikk_kod = product[0].get("CikkKod", "")
                    cnev_text = product[0].get("CnevText", "")

                    logger.info(f"Found product: {cikk_kod} - {cnev_text}")
                    self.termek_urls.append(self.base_url + seo_url)
            #print(products_data)
            return products_data
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            logger.error(f"Error extracting product data: {e}")
            return {}

    def parse_products(self, products_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Parse product data into structured format
        """
        products = []

        if 'data' not in products_data:
            return products

        for product_group in products_data['data']:
            for product in product_group:
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
                    'seo_url': product.get('seo', '')
                }
                products.append(product_info)

        return products

    def extract_pagination_info(self, products_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract pagination information from products data
        """
        pagination_info = {
            'current_page': products_data.get('current_page'),
            'last_page': products_data.get('last_page'),
            'total': products_data.get('total', 0),
            'per_page': products_data.get('per_page', 10),
            'next_page_url': products_data.get('next_page_url', '')
        }
        print(pagination_info)
        return pagination_info

    def extract_all_variables(self, html_content: str) -> Dict[str, Any]:
        """
        Extract all variables from HTML content
        """
        result = {}

        # Products data
        products_data = self.extract_product_data(html_content)
        if products_data:
            result['products'] = self.parse_products(products_data)
            #pagination info
            result['pagination'] = {
                'current_page': products_data.get('current_page', 1),
                'last_page': products_data.get('last_page', 1),
                'total': products_data.get('total', 0),
                'per_page': products_data.get('per_page', 10),
                'next_page_url': products_data.get('next_page_url', '')
            }

        # Other variables
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
                        json_str = match.group(1).replace('&quot;', '"')
                        result[key] = json.loads(json_str)
                    elif key == 'productnumbers':
                        json_str = match.group(1).replace('&quot;', '"')
                        result[key] = json.loads(json_str)
                    else:
                        result[key] = match.group(1)
                except json.JSONDecodeError:
                    result[key] = match.group(1)

        return result

    def fetch_url_content(self, url: str, timeout: int = 10) -> Optional[str]:
        """
        Fetch content from URL with error handling
        """
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            return None
    def process_urls1(self, input_file: str, output_file: str, termek_file: str) -> bool:
        """
        Process all URLs from input file and save results
        """
        try:
            # Load URLs
            url_list = self.load_urls(input_file)
            if not url_list:
                logger.error("No URLs found in input file")
                return False

            # Process URLs
            results = []
            for i, url in enumerate(url_list, 1):
                logger.info(f"Processing {i}/{len(url_list)}: {url}")
                print(i,url)
                html_content = self.fetch_url_content(url)
                if html_content:
                    #extracted_data = self.extract_all_variables(html_content)
                    extracted_page_data = self.extract_product_data(html_content)
                    print(extracted_page_data)
                    #pagination_info = self.extract_pagination_info(extracted_data)
                    #last_page = pagination_info.get('last_page', 1)
                    #print(last_page)
                    last_page = extracted_page_data['last_page']
                    print(last_page)
                    for page in range(1, last_page + 1):
                        logger.info(f"Fetching page {page} for URL: {url}")
                        paged_url = f"{url}&page={page}" if "?" in url else f"{url}?page={page}"
                        print(paged_url)
                        paged_content = self.fetch_url_content(paged_url)
                        #print(paged_content)
                        if paged_content:
                            extracted_page_data1 = self.extract_all_variables(paged_content)
                            print(extracted_page_data1)
                    #extracted_data = self.extract_all_variables(html_content)
                    #results.append((url, html_content[:100] + "..." if len(html_content) > 100 else html_content,
                    #                str(extracted_data)))
                else:
                    results.append((url, f"Error fetching URL", ""))

            # Save results
            self.save_results(output_file, results)
            self.save_termek_urls(termek_file)

            logger.info(f"Processing complete. Results saved to {output_file} and {termek_file}")
            return True

        except Exception as e:
            logger.error(f"Error processing URLs: {e}")
            return False

    def process_urls(self, input_file: str, output_file: str, termek_file: str) -> bool:
        """
        Process all URLs from input file and save results
        """
        try:
            # Load URLs
            url_list = self.load_urls(input_file)
            if not url_list:
                logger.error("No URLs found in input file")
                return False

            # Process URLs
            results = []
            for i, url in enumerate(url_list, 1):
                logger.info(f"Processing {i}/{len(url_list)}: {url}")
                print(i,url)
                html_content = self.fetch_url_content(url)
                if html_content:
                    #extracted_data = self.extract_all_variables(html_content)
                    extracted_page_data = self.extract_product_data(html_content)
                    print(extracted_page_data)
                    #pagination_info = self.extract_pagination_info(extracted_data)
                    #last_page = pagination_info.get('last_page', 1)
                    #print(last_page)
                    last_page = extracted_page_data['last_page']
                    print(last_page)
                    for page in range(1, last_page + 1):
                        logger.info(f"Fetching page {page} for URL: {url}")
                        paged_url = f"{url}&page={page}" if "?" in url else f"{url}?page={page}"
                        print(paged_url)
                        paged_content = self.fetch_url_content(paged_url)
                        #print(paged_content)
                        if paged_content:
                            extracted_page_data1 = self.extract_all_variables(paged_content)
                            print(extracted_page_data1)
                    #extracted_data = self.extract_all_variables(html_content)
                    #results.append((url, html_content[:100] + "..." if len(html_content) > 100 else html_content,
                    #                str(extracted_data)))
                else:
                    results.append((url, f"Error fetching URL", ""))

            # Save results
            self.save_results(output_file, results)
            self.save_termek_urls(termek_file)

            logger.info(f"Processing complete. Results saved to {output_file} and {termek_file}")
            return True

        except Exception as e:
            logger.error(f"Error processing URLs: {e}")
            return False

    def load_urls(self, input_file: str) -> List[str]:
        """
        Load URLs from CSV file
        """
        url_list = []
        try:
            with open(input_file, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                for row in reader:
                    if row and row[0].strip():
                        url_list.append(row[0].strip())
        except FileNotFoundError:
            logger.error(f"Input file not found: {input_file}")
        except Exception as e:
            logger.error(f"Error reading input file: {e}")

        return url_list

    def save_results(self, output_file: str, results: List[tuple]) -> None:
        """
        Save results to CSV file
        """
        try:
            with open(output_file, "w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["URL", "Content_Preview", "Extracted_Data"])
                for url, content, extracted in results:
                    writer.writerow([url, content, extracted])
        except Exception as e:
            logger.error(f"Error saving results: {e}")

    def save_termek_urls(self, termek_file: str) -> None:
        """
        Save product URLs to CSV file
        """
        try:
            with open(termek_file, "w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                for termek_url in self.termek_urls:
                    writer.writerow([termek_url])
        except Exception as e:
            logger.error(f"Error saving product URLs: {e}")


def main():
    """Main execution function"""
    INPUT_FILE = "URL_LIST.csv"
    OUTPUT_FILE = "ADAT.csv"
    TERMEK_FILE = "TERMEK_URL.csv"

    scraper = ProductScraper()
    success = scraper.process_urls(INPUT_FILE, OUTPUT_FILE, TERMEK_FILE)

    if success:
        print("✅ 🚀 Processing complete!")
    else:
        print("❌ Processing failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()