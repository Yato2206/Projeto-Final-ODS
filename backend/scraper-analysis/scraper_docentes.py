import asyncio
import aiohttp
import aiofiles
import json
from bs4 import BeautifulSoup
from datetime import datetime
from pathlib import Path
import sys
from time import sleep
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from utilis import fetch_async, _print_summary

# Schools can be processed one by one. Keep this list aligned with the current scrape scope.
escolas = ["ESCS", "ESD", "ESELX", "ESML", "ESTC", "ESSL", "ISCAL", "ISEL"]
#escolas = ["ESCS"]

INPUT_FILE = "escolas/departamentos.json"
OUTPUT_FILE = "escolas/docentes.json"
RETRIES = 3
MAX_CONCURRENT  = 5 
MAX_PER_PAGE_ISCAL = 10
MAX_PER_PAGE_ISEL = 51
START_PAGE = 0
ISCAL_PAGE_URL = "https://www.iscal.ipl.pt/docentes?page="
ISEL_PAGE_URL = "https://www.isel.pt/docentes?page="

DIRECT_URLS = {
    "ESD": "https://www.esd.ipl.pt/docentes",
    "ESTC": "https://www.estc.ipl.pt/docentes",
    "ESSL": "https://www.essl.ipl.pt/estesl/departamentos",
}

PAGINATED_SCHOOLS = {
    "ISCAL": {
        "page_url": ISCAL_PAGE_URL,
        "max_per_page": MAX_PER_PAGE_ISCAL,
    },
    "ISEL": {
        "page_url": ISEL_PAGE_URL,
        "max_per_page": MAX_PER_PAGE_ISEL,
    },
}

LINK_TRANSFORMS = {
    "ESCS": lambda link: link,
    "ESELX": lambda link: link,
    "ESML": lambda link: link,
    "ISEL": lambda link: link + "/docentes?page=",
    "ESD": lambda link: link,
    "ESTC": lambda link: link,
    "ESSL": lambda link: link,
    "ISCAL": lambda link: link,
}

BASE_URLS = {
    "ESCS": "https://www.escs.ipl.pt",
    "ESD":   "https://www.esd.ipl.pt",
    "ESELX": "https://www.eselx.ipl.pt",
    "ESML":  "https://www.esml.ipl.pt",
    "ESTC":  "https://www.estc.ipl.pt",
    "ESSL":  "https://www.essl.ipl.pt",
    "ISCAL": "https://www.iscal.ipl.pt",
    "ISEL":  "https://www.isel.pt",
}

#seletores CSS para achar os docentes de cada escola
SELECTORS = {
    "ESCS": ".item div",
    "ESD":   ".content-main span",
    "ESELX": ".container-bg div",
    "ESML":  ".t3-content h2",
    "ESTC":  ".content-main tr",
    "ESSL":  ".table tr",
    "ISCAL": ".mt-5 tr",
    "ISEL":  ".gva-view-grid span",
}
REQUEST_TIMEOUT = 10

def _load_json(path):
    p = Path(path)
    if not p.exists():
        return {}
    with open(p, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            print(f"Could not parse {path} — starting fresh")
            return {}

async def save_data(new_data):
    existing = _load_json(OUTPUT_FILE)
    merged   = {**existing, **new_data}
 
    sorted_data = dict(sorted(
        merged.items(),
        key=lambda item: (item[1].get("dateChecked", "") if isinstance(item[1], dict) else ""),
        reverse=True,
    ))
 
    async with aiofiles.open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        await f.write(json.dumps(sorted_data, ensure_ascii=False, indent=2))
 
    print(f"Saved — total records in file: {len(sorted_data)}")

#NOTA: este e um pouco diferente. Nota para lembrar
def load_existing_data(escola):
    """Load scraped docentes data."""
    data = _load_json(OUTPUT_FILE)
    if not data:
        return {}
 
    if escola in PAGINATED_SCHOOLS:
        if escola in data and isinstance(data[escola], dict):
            return data[escola]
        merged: dict = {}
        for key, value in data.items():
            if key.startswith(f"{escola}::page-") and isinstance(value, dict):
                for docent_name, docente_info in value.items():
                    if docent_name != "sourceUrl":
                        merged[docent_name] = docente_info
        return merged
 
    return {key: value for key, value in data.items() if isinstance(value, dict) and value.get("escola") == escola}

#================================================
# PARSING
#================================================

#recebe um elemento BS, extraindo o conteúdo relevante
def parse_element(element, escola):
    base_url = BASE_URLS[escola]
 
    if escola == "ESSL":
        nome_elem = element.select_one("td")
    elif escola == "ESCS":
        nome_elem = element.select_one(".views-field.views-field-view-node a")
        #print(f"nome_elem: {nome_elem}")
    else:
        nome_elem = element.select_one("a")
 
    if not nome_elem:
        return None
 
    nome = nome_elem.get_text(strip=True)
    #CASO ESPECIAL NO ESELX
    if not nome or "Departamento" in nome:
        return None
    #CASO ESPECIAL ESCS    
    if escola == "ESCS":
        nome_span = element.select_one(".views-field.views-field-title span")
        nome = nome_span.get_text(strip=True) if nome_span else nome
        #print(f"dfndnd {nome}")
    # CASO ESPECIAL ATE ARRANJAR UMA MANEIRA MELHOR DE SE RESOLVER
    if escola == "ESSL":
        tag_a = element.select_one("a")
        href  = tag_a.get("href") if tag_a else None
        if not href:
            return None
        href = "LINK NAO DISPONIVEL" if "mailto:" in href else href
    else:
        href = nome_elem.get("href")
 
    if not href:
        return None
    if href.startswith("?") or "mailto:" in href:
        return None
 
    link = (base_url + href) if href.startswith("/") else href
 
    return nome, {
        "escola":       escola,
        "link":         link,
        "dateChecked":  datetime.now().isoformat(),
    }
 
#Faz o parse do conteúdo do html para uma dada escola
def parse_docentes(html, escola):
    if escola not in SELECTORS:
        print(f"No selector configured for escola '{escola}'")
        return {}
 
    soup  = BeautifulSoup(html, "html.parser")
    items = soup.select(SELECTORS[escola])
 
    docentes = {}
    for element in items:
        #print(element)
        result = parse_element(element, escola)
        if result:
            nome, record = result
            docentes[nome] = record
 
    return docentes

#================================================
# Carregar links do fichero departamento.json
#================================================

# Carregar os links dos departamentos a partir do ficheiro JSON, filtrando por escola
def load_departamentos_links(escola):
    data = _load_json(INPUT_FILE)
    if not data:
        print(f"No data found in {INPUT_FILE}")
        return []

    transform = LINK_TRANSFORMS.get(escola, lambda value: value)
    links = []
    for title, info in data.items():
        if info.get("escola") != escola:
            continue

        link = info.get("link")
        if not link:
            continue

        links.append({
            "escola": escola,
            "title": title,
            "link": transform(link),
        })

    return links

# Retorna uma lista de links para fazer scrape para uma escola
def build_link_sources(escola):
    direct = DIRECT_URLS.get(escola)
    if direct:
        return [{"escola": escola, "title": escola, "link": direct, "source": "direct"}]
    return load_departamentos_links(escola)

#================================================
# SCRAPPING - COM PAGINAÇÃO
#================================================

# Faz fetch das paginas comecando em *start_page* até encontra uma página com menos items que *max_per_page*
# Os resultados são colocados em *accumulated*
# Retorna o numero de items novos encontrados
async def scrape_paginated_source(session, semaphore, escola, page_url, max_per_page, accumulated, start_page = START_PAGE, source_title = None):
    page = start_page
    new_items = 0

    while True:
        url = f"{page_url}{page}"
        html = await fetch_async(session, semaphore, url, debug_tag=escola)
        if not html:
            print(f"[{escola}] No content on page {page}")
            break

        record = parse_docentes(html, escola)
        if not record:
            print(f"[{escola}] No content on page {page}")
            break

        page_item_count = len(record)
        accumulated.update(record)
        accumulated["escola"] = escola
        accumulated["sourceUrl"] = url
        accumulated["dateChecked"] = datetime.now().isoformat()
        new_items += page_item_count

        print(f"[{escola}] Page {page}: {page_item_count} items")

        if page_item_count < max_per_page:
            print(f"[{escola}] Page {page} has fewer than {max_per_page} items, stopping")
            break

        page += 1

    return new_items

#================================================
# SCRAPPING - DIRETO COM A ESCOLA
#================================================

async def scrape_one(session, semaphore, escola, link_info, existent_keys):
    url = link_info["link"]
    key = f"{escola}::{link_info.get('title') or url}"
 
    if key in existent_keys:
        print(f"[{escola}] Already scraped: {key}")
        return {}
 
    print(f"[{escola}] Scraping {url}...")
    html = await fetch_async(session, semaphore, url, debug_tag=escola)
    if not html:
        return {}
 
    records = parse_docentes(html, escola)
    if not records:
        return {}
 
    records["sourceUrl"] = url
    return {key: records}

# Faz scrape de uma escola end-to-end. Não escreve nada no ficheiro, apenas retorna os dados encontrados.
async def scrape_escola(session, semaphore, escola):
    existing_data = load_existing_data(escola)
    if escola in PAGINATED_SCHOOLS:
        print(f"\n{'='*50}")
        print(f"Scraping escola: {escola}")
        print(f"{'='*50}\n")
        config = PAGINATED_SCHOOLS[escola]
        accumulated = dict(existing_data)

        if escola == "ISEL":
            link_sources = load_departamentos_links(escola)           
            if not link_sources:
                print(f"[{escola}] No department links found")
                return {}

            tasks = [
                scrape_paginated_source(
                    session, semaphore, escola,
                    source["link"], config["max_per_page"],
                    accumulated, START_PAGE, source.get("title"),
                )
                for source in link_sources
            ]
            total_new_items = await asyncio.gather(*tasks)
            print(f"\n[{escola}] Completed")
            print(f"[{escola}] New items: {total_new_items}")
        else:
            new_items = await scrape_paginated_source(
                session, semaphore, escola,
                config["page_url"], config["max_per_page"],
                accumulated, START_PAGE
            )
            print(f"\n[{escola}] Completed")
            print(f"[{escola}] New items: {new_items}")
        return {escola: accumulated}
        
    link_sources = build_link_sources(escola)
    if not link_sources:
        print(f"[{escola}] No links found to scrape")
        return {}
    print(f"[{escola}] Found {len(link_sources)} link(s) to scrape")

    existent_keys = set(existing_data.keys())

    results = await asyncio.gather(*[scrape_one(session, semaphore, escola, source, existent_keys) for source in link_sources])

    all_data = dict(existing_data)
    for chunk in results:
        all_data.update(chunk)
 
    new_count = len(all_data) - len(existing_data)
    _print_summary(existing_data, all_data)
    print(f"\n[{escola}] Completed")
    return all_data

async def main():
    print(f"\n{'='*50}")
    print("Docentes Scraper")
    print(f"{'='*50}\n")
    
    semaphore = asyncio.Semaphore(MAX_CONCURRENT)

    connector = aiohttp.TCPConnector(limit=MAX_CONCURRENT)
    headers   = {"User-Agent": "Mozilla/5.0"}
 
    async with aiohttp.ClientSession(connector=connector, headers=headers) as session:
        tasks   = [scrape_escola(session, semaphore, escola) for escola in escolas]
        results = await asyncio.gather(*tasks)
    merged: dict = {}
    for chunk in results:
        merged.update(chunk)
 
    await save_data(merged)
    print(f"{'='*50}\n")
    print("ACABADO")
    print(f"{'='*50}\n")

if __name__ == "__main__":
    Path("escolas").mkdir(parents=True, exist_ok=True)
    asyncio.run(main())
