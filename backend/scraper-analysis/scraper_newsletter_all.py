import json
from bs4 import BeautifulSoup
from datetime import datetime
from pathlib import Path
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from time import sleep
from utilis import load_existing_data, save_data, fetch, _print_summary

# Configuração
BASE_URL = "https://www.ipl.pt/en/politecnico/comunicacao/newsletter"
OUTPUT_FILE = "documents/newsletter/newsletter_links.json"
RETRIES = 3
MIN_ITEMS_PER_PAGE = 10

def parse_page(html):
    """Parse page and extract newsletter items"""
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.select(".view-content-wrap .item")

    news = {}
    for element in items:
        titulo_elem = element.select_one(".views-field-title a")
        if not titulo_elem:
            continue

        titulo = titulo_elem.get_text(strip=True)
        if not titulo:
            continue

        data_elem = element.select_one(".views-field-field-data-envio")
        data = data_elem.get_text(strip=True) if data_elem else ""

        href = titulo_elem.get('href')
        link = f"https://www.ipl.pt{href}" if href and href.startswith('/') else href

        if not link:
            continue

        news[titulo] = {
            "dataPublicacao": data,
            "link": link,
            "dateChecked": datetime.now().isoformat()
        }

    return news

def _scrape_sequential(start_page, existing_data, all_news_shared, prefix="[Sequential]"):
    """Core sequential scraping logic"""
    page = start_page
    first_item_key = None

    while True:
        url = f"{BASE_URL}?page={page}"
        print(f"  {prefix} Scraping page {page}...")

        html = fetch(url)
        if not html:
            print(f"  {prefix} No response from page {page}")
            break

        news = parse_page(html)

        if not news:
            print(f"  {prefix} No items found on page {page} → End of pagination")
            break

        if not first_item_key:
            first_item_key = list(news.keys())[0]
            if first_item_key in existing_data:
                print(f"  {prefix} First item already scraped → Stopping (no new updates)")
                break

        new_items = 0
        for key, value in news.items():
            if key not in all_news_shared:
                all_news_shared[key] = value
                new_items += 1

        print(f"  {prefix} Page {page}: {len(news)} items ({new_items} new)")

        if len(news) < MIN_ITEMS_PER_PAGE:
            print(f"  {prefix} Page {page} has fewer than {MIN_ITEMS_PER_PAGE} items → Stopping")
            break

        if new_items == 0:
            print(f"  {prefix} No new items found → All updates already scraped, stopping")
            break

        page += 1
        sleep(1)

def scrape_newsletters(force_full=False):
    """Scrape all newsletter pages"""
    if force_full and Path(OUTPUT_FILE).exists():
        Path(OUTPUT_FILE).unlink()
        print(f"Removed existing {OUTPUT_FILE} before full scrape")

    previous_data = load_existing_data(OUTPUT_FILE)
    existing_data = {} if force_full else previous_data
    print(f"Loaded {len(existing_data)} existing items")

    all_news = {} if force_full else dict(existing_data)

    _scrape_sequential(0, existing_data, all_news)

    sort_key = "dataPublicacao"
    save_data(all_news, sort_key, OUTPUT_FILE)
    _print_summary(existing_data, all_news)


def main():
    print(f"\n{'='*50}")
    print(f"Newsletter Scraper")
    print(f"{'='*50}\n")

    force_full = len(sys.argv) > 1 and sys.argv[1].strip().lower() == "true"
    if force_full:
        print("Force mode enabled: full scrape from page 0 (ignoring existing items)")

    scrape_newsletters(force_full=force_full)


if __name__ == "__main__":
    # Ensure documents directory exists
    Path("documents/newsletter/").mkdir(parents=True, exist_ok=True)
    main()
