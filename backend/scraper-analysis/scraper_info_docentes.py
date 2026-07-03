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
from utilis import fetch_async


INPUT_FILE = "escolas/docentes.json"
OUTPUT_FILE = "escolas/docentes-info.json"
RETRIES = 3
MAX_CONCURRENT  = 5 
START_PAGE = 0

escolas = ["ESCS", "ESD", "ESELX", "ESML", "ESTC", "ESSL", "ISCAL", "ISEL"]
#escolas = ["ISEL"]
#seletores CSS para achar os links de cada docente
SELECTORS: dict[str, str] = {
    "ESCS": ".NAOTEMSELECTOR",  # Placeholder for ESCS
    "ESD":   ".field.field--name-field-investigacao div",
    "ESELX": ".field.field--name-field-investigacao div",
    "ESML":  ".NAOTEMSELECTOR",  # Placeholder for ESML
    "ESTC":  ".NAOTEMSELECTOR",  # Placeholder for ESTC
    "ESSL":  ".node__content",
    "ISCAL": ".node__content",
    "ISEL":  ".node__content",
}

REQUEST_TIMEOUT = 10

#FICHEIRO UTILIS
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
 
    async with aiofiles.open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        await f.write(json.dumps(merged, ensure_ascii=False, indent=2))

    print(f"Saved — total records: {len(merged)}")


def load_existing_keys():
    return set(_load_json(OUTPUT_FILE).keys())


def load_all_links():
    data = _load_json(INPUT_FILE)
    if not data:
        print(f"No data found in {INPUT_FILE}")
        return []

    links = []
    for escola, docentes in data.items():
        if not isinstance(docentes, dict):
            continue
        for nome, info in docentes.items():
            if not isinstance(info, dict):
                continue
            link = info.get("link")
            escola = info.get("escola", escola)
            if link:
                links.append({"name": nome, "link": link, "escola": escola})

    return links

#================================================
# PARSING
#================================================

#extração do nome da ligaçao, que pode vir de várias maneiras, dependendo da fonte
#selector é, normalmente, um elemento <a> do BeautifulSoup
def extract_name(selector):
    #primeira tentativa: usar o atributo title do link
    nome = (selector.get("title") or "").strip()
    if not nome:
        #segunda tentativa: usar o texto anterior ao link, que pode estar colado ao link
        nome_raw = selector.previous_sibling
        nome = str(nome_raw).strip() if nome_raw is not None else ""
        nome = nome.strip("|").rstrip(":").strip()
    if not nome:
        #terceira tentativa: usar o texto do link
        nome = selector.get_text(strip=True)
    #caso exemplo: ORCID ID, só se quer o ORCID, sem o ID
    if nome.endswith(" ID") or nome.endswith(" ID"):
        nome = nome[:-len(" ID")].strip()
    return nome

#Recebe um elemento BS, extraindo o conteúdo relevante. 
#Retorna todos os links associados ao docente
def parse_element(element):
    resultados = []

    for p in element.select("p"):
        for a in p.select("a"):
            href = a.get("href")
            #apesar de improvável, cobre os casos em que o seletor a não tem href
            if not href or href.startswith("?") or "mailto:" in href: 
                continue

            nome = extract_name(a)
            if not nome:
                continue

            resultados.append((nome, {
                "link":        href,
                "dateChecked": datetime.now().isoformat(),
            }))

    return resultados

#Faz o parse do conteúdo do html para uma dada escola
def parse_info(html, escola):
    if escola not in SELECTORS:
        print(f"[{escola}] No selector defined, skipping")
        return {}
    soup  = BeautifulSoup(html, "html.parser")
    items = soup.select(SELECTORS[escola])
 
    docentes = {}
    for element in items:
        for nome, record in parse_element(element):
            docentes[nome] = record

    return docentes


#================================================
# Scraping
#================================================

def base_record(escola, url):
    return {
        "sourceUrl": url,
        "escola": escola,
        "dateChecked": datetime.now().isoformat(),
    }

async def scrape_one(session, semaphore, entry, existing_keys):
    name = entry["name"]
    escola = entry["escola"]
    url  = entry["link"]

    if name in existing_keys:
        print(f"Already scraped: {name}")
        return None

    if urlparse(url).scheme not in ("http", "https"):
        return name, base_record(escola, url)

    print(f"Scraping {name} — {url}")
    html = await fetch_async(session, semaphore, url, debug_tag=name)
    if not html:
        return None

    record = base_record(escola, url)
    parsed = parse_info(html, escola)

    if parsed:
        merged = {**parsed, **record}   # base_record tem prioridade
        record.update(merged)
    else:
        print(f"[{name}] No data found — saving base record")

    return name, record

async def main():
    print(f"\n{'='*50}")
    print("Docentes-INFO Scraper")
    print(f"{'='*50}\n")

    semaphore = asyncio.Semaphore(MAX_CONCURRENT)

    entries = load_all_links()
    if not entries:
        print("Nothing to scrape.")
        return

    existing_keys = load_existing_keys()
    print(f"Total links: {len(entries)}  |  Already scraped: {len(existing_keys)}")

    connector = aiohttp.TCPConnector(limit=MAX_CONCURRENT)
    headers   = {"User-Agent": "Mozilla/5.0"}
 
    async with aiohttp.ClientSession(connector=connector, headers=headers) as session:
        tasks   = [scrape_one(session, semaphore, entry, existing_keys) for entry in entries]
        results = await asyncio.gather(*tasks)
    
    new_data = {name: record for result in results if result is not None for name, record in [result]}

    await save_data(new_data)
    print(f"{'='*50}\n")
    print("ACABADO")
    print(f"{'='*50}\n")

if __name__ == "__main__":
    Path("escolas").mkdir(parents=True, exist_ok=True)
    asyncio.run(main())
