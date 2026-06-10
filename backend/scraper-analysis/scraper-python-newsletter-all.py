import json
from bs4 import BeautifulSoup
from datetime import datetime
from pathlib import Path
import sys
from time import sleep
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

# Configuração
BASE_URL = "https://www.ipl.pt/en/politecnico/comunicacao/newsletter"
OUTPUT_FILE = "documents/newsletter_links.json"
RETRIES = 3
MIN_ITEMS_PER_PAGE = 10

# Ensure documents directory exists
Path("documents").mkdir(exist_ok=True)

#esta funcao ficara num ficheiro utils e sera importada para os outros scrapers, para evitar a duplicacao de codigo
def load_existing_data():
    """Load existing newsletter data"""
    if Path(OUTPUT_FILE).exists():
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

#esta funcao ficara num ficheiro utils e sera importada para os outros scrapers, para evitar a duplicacao de codigo
def save_data(data):
    """Save newsletter data to file, sorted by publication date"""
    sorted_data = dict(sorted(
        data.items(),
        key=lambda item: item[1].get("dataPublicacao", ""),
        reverse=True
    ))

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(sorted_data, f, ensure_ascii=False, indent=2)
    print(f"Newsletter saved! Total items: {len(sorted_data)}")

#esta funcao ficara num ficheiro utils e sera importada para os outros scrapers, para evitar a duplicacao de codigo
def fetch(url):
    """Fetch page with retries"""
    for attempt in range(RETRIES):
        try:
            request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urlopen(request, timeout=10) as response:
                return response.read().decode("utf-8")
        except (HTTPError, URLError, TimeoutError) as e:
            if attempt < RETRIES - 1:
                sleep(2 ** attempt)
            else:
                print(f"Failed to fetch {url}: {e}")
                return None
    return None


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

#esta funcao ficara num ficheiro utils e sera importada para os outros scrapers, para evitar a duplicacao de codigo
def _print_summary(existing_data, all_news):
    """Print scraping summary"""
    new_count = len(all_news) - len(existing_data)
    print(f"\n{'='*50}")
    print(f"Scraping completed!")
    print(f"Previous items: {len(existing_data)}")
    print(f"New items: {new_count}")
    print(f"Total items: {len(all_news)}")
    print(f"{'='*50}")


def scrape_newsletters(force_full=False):
    """Scrape all newsletter pages"""
    if force_full and Path(OUTPUT_FILE).exists():
        Path(OUTPUT_FILE).unlink()
        print(f"Removed existing {OUTPUT_FILE} before full scrape")

    previous_data = load_existing_data()
    existing_data = {} if force_full else previous_data
    print(f"Loaded {len(existing_data)} existing items")

    all_news = {} if force_full else dict(existing_data)

    _scrape_sequential(0, existing_data, all_news)

    save_data(all_news)
    _print_summary(existing_data, all_news)


def main():
    print(f"\n{'='*50}")
    print(f"Newsletter Scraper")
    print(f"{'='*50}\n")

    # Optional force mode: py .\scraper-python-newsletter-all.py true
    force_full = len(sys.argv) > 1 and sys.argv[1].strip().lower() == "true"
    if force_full:
        print("Force mode enabled: full scrape from page 0 (ignoring existing items)")

    scrape_newsletters(force_full=force_full)


if __name__ == "__main__":
    main()
