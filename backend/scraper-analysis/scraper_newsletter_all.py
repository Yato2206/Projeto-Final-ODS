import json
from bs4 import BeautifulSoup
from datetime import datetime
from pathlib import Path
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from time import sleep
from utilis import load_existing_data, save_data, fetch, _print_summary, _scrape_sequential

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

def scrape_newsletters(force_full=False):
    """Scrape all newsletter pages"""
    if force_full and Path(OUTPUT_FILE).exists():
        Path(OUTPUT_FILE).unlink()
        print(f"Removed existing {OUTPUT_FILE} before full scrape")

    previous_data = load_existing_data(OUTPUT_FILE)
    existing_data = {} if force_full else previous_data
    print(f"Loaded {len(existing_data)} existing items")

    all_news = {} if force_full else dict(existing_data)

    _scrape_sequential(BASE_URL, parse_page, 0, existing_data, all_news, MIN_ITEMS_PER_PAGE)

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
