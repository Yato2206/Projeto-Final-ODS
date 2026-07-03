import json
from bs4 import BeautifulSoup
from datetime import datetime
from pathlib import Path
import sys
from time import sleep
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from utilis import load_existing_data, save_data, fetch, _print_summary

# Configuração
BASE_URL = "https://www.ipl.pt/estudar/cursos/"
OUTPUT_FILE = "documents/cursos/cursos_links.json"
RETRIES = 3
MIN_ITEMS_PER_PAGE = 12

def parse_page(html):
    """Parse page and extract cursos items"""
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.select(".view-content-wrap .item")

    cursos = {}
    for element in items:
        titulo_elem = element.select_one(".views-field-title a")
        if not titulo_elem:
            continue

        titulo = titulo_elem.get_text(strip=True)
        if not titulo:
            continue

        href = titulo_elem.get('href')
        link = f"https://www.ipl.pt{href}" if href and href.startswith('/') else href

        if not link:
            continue

        escola_img = element.select_one(".views-field-field-logo img")
        if not escola_img:
            continue
        escola_raw = escola_img.get("alt")
        if not escola_raw:
            continue
        
        escola_map = {
            "Escola Superior de Comunicação Social": "ESCS",
            "Logotipo ESD": "ESD",
            "Escola Superior de Educação de Lisboa": "ESELX",
            "Escola Superior de Música de Lisboa": "ESML",
            "Escola Superior de Teatro e Cinema": "ESTC",
            "logotipo_essl": "ESSL",
            "Instituto Superior de Contabilidade e Administração de Lisboa": "ISCAL",
            "Logotipo ISEL - Versão acrónimo": "ISEL",
            }
        escola_map_select = escola_map.get(escola_raw)
        escola = escola_map_select if escola_map_select else "Desconhecido"

        cursos[link] = {
            "curso": titulo,
            "escola": escola,
            "dateChecked": datetime.now().isoformat(),
            "tipoCurso": "Licenciatura" if "licenciaturas" in link else "Mestrado" if "mestrados" in link else "Pos-Graduação" if "pos-graduacoes" in link else "Desconhecido"
        }

    return cursos

def _scrape_sequential(start_page, existing_data, curso, all_shared, prefix="[Sequential]"):
    """Core sequential scraping logic"""
    page = start_page
    first_item_key = None

    while True:
        url = f"{BASE_URL}{curso}?page={page}"
        print(f"  {prefix} Scraping page {page}...")

        html = fetch(url)
        if not html:
            print(f"  {prefix} No response from page {page}")
            break

        cursos = parse_page(html)

        if not cursos:
            print(f"  {prefix} No items found on page {page} → End of pagination")
            break

        if not first_item_key:
            first_item_key = list(cursos.keys())[0]
            if first_item_key in existing_data:
                print(f"  {prefix} First item already scraped → Stopping (no new updates)")
                break

        new_items = 0
        for key, value in cursos.items():
            if key not in all_shared:
                all_shared[key] = value
                new_items += 1

        print(f"  {prefix} Page {page}: {len(cursos)} items ({new_items} new)")

        if len(cursos) < MIN_ITEMS_PER_PAGE:
            print(f"  {prefix} Page {page} has fewer than {MIN_ITEMS_PER_PAGE} items → Stopping")
            break

        if new_items == 0:
            print(f"  {prefix} No new items found → All updates already scraped, stopping")
            break

        page += 1
        sleep(1)

def scrape_cursos(force_full=False):
    """Scrape all cursos pages"""
    if force_full and Path(OUTPUT_FILE).exists():
        Path(OUTPUT_FILE).unlink()
        print(f"Removed existing {OUTPUT_FILE} before full scrape")

    previous_data = load_existing_data(OUTPUT_FILE)
    existing_data = {} if force_full else previous_data
    print(f"Loaded {len(existing_data)} existing items")

    all_cursos = {} if force_full else dict(existing_data)

    for curso in ["licenciaturas", "mestrados", "pos-graduacoes"]:
        _scrape_sequential(0, existing_data, curso, all_cursos, prefix=f"[{curso.capitalize()}]")

    sort_key = "dateChecked"
    save_data(all_cursos, sort_key, OUTPUT_FILE)
    _print_summary(existing_data, all_cursos)


def main():
    print(f"\n{'='*50}")
    print(f"Cursos Scraper")
    print(f"{'='*50}\n")

    force_full = len(sys.argv) > 1 and sys.argv[1].strip().lower() == "true"
    if force_full:
        print("Force mode enabled: full scrape from page 0 (ignoring existing items)")

    scrape_cursos(force_full=force_full)


if __name__ == "__main__":
    # Ensure documents directory exists
    Path("documents/cursos/").mkdir(parents=True, exist_ok=True)
    main()