import requests
from bs4 import BeautifulSoup
import aiohttp
import asyncio
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from loguru import logger
import pandas as pd
import json
import time

logger.add("crawler.log", level="INFO")

# Selenium setup for handling dynamic content
def get_selenium_driver():
    options = Options()
    options.headless = True  # Running headless mode (no GUI)
    driver = webdriver.Chrome(options=options)
    return driver

def get_html(url, dynamic=False):
    if dynamic:
        driver = get_selenium_driver()
        driver.get(url)
        time.sleep(2)  
        html = driver.page_source
        driver.quit()
    else:
        response = requests.get(url)
        html = response.text
    return html

# Extract product URLs from HTML content
def find_product_urls(html):
    soup = BeautifulSoup(html, 'html.parser')
    product_urls = set()
    
    for a_tag in soup.find_all('a', href=True):
        link = a_tag['href']
        if '/product/' in link or '/item/' in link or '/p/' in link:
            if link.startswith('/'):
                link = "https://" + link[1:]
            product_urls.add(link)
    
    return product_urls

# Crawl a single domain
async def crawl_site(domain, session, dynamic=False):
    logger.info(f"Crawling {domain}...")
    product_urls = set()
    html = await fetch_page(domain, session, dynamic)
    new_urls = find_product_urls(html)
    product_urls.update(new_urls)
    
    return product_urls

# Fetch page asynchronously
async def fetch_page(domain, session, dynamic=False):
    url = f"https://{domain}"
    html = await get_html(url, dynamic)
    return html

# Crawl all sites
async def crawl_all_sites(domains):
    all_product_urls = {}
    async with aiohttp.ClientSession() as session:
        for domain in domains:
            domain_product_urls = await crawl_site(domain, session, dynamic=True)
            all_product_urls[domain] = domain_product_urls
    return all_product_urls

# Save the results to CSV/JSON
def save_results(results):
    # Option 1: Save to CSV
    df = pd.DataFrame.from_dict(results, orient='index').transpose()
    df.to_csv("discovered_product_urls.csv", index=False)
    
    # Option 2: Save to JSON
    with open('discovered_product_urls.json', 'w') as f:
        json.dump(results, f)

# Main execution
async def main():
    domains = ["example1.com", "example2.com", "example3.com"]
    results = await crawl_all_sites(domains)
    save_results(results)

if __name__ == "__main__":
    asyncio.run(main())
