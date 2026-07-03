import asyncio
import json
import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime
from pathlib import Path
import sys
from urllib.parse import urlparse
import re
from utilis import load_existing_data, load_links, save_data, fetch_async, normalize_text, _print_summary

# Configuração
BASE_PATH = Path("documents/newsletter/")
INPUT_FILE = BASE_PATH / "newsletter_links.json"
OUTPUT_FILE = BASE_PATH / "newsletter_content.json"
CONCURRENT_REQUESTS = 5
RETRIES = 3
NUM_SCRAPERS = 5

#semaphore = asyncio.Semaphore(CONCURRENT_REQUESTS)

def extract_newsletter_id(url):
    """Extract newsletter ID from URL"""
    parsed = urlparse(url)
    parts = parsed.path.split("/")
    last_part = parts[-1] if parts else ""
    return last_part if last_part and last_part[-1].isdigit() else "unknown"

def parse_newsletter_content(html, newsletter_id, data_publicacao, link):
    """Parse newsletter HTML and extract content"""
    soup = BeautifulSoup(html, 'html.parser')

    content_main = soup.select_one(".content-main")
    if not content_main:
        return None

    # Extract main title and text
    titulo_elem = content_main.select_one(".title-body h1")
    titulo = normalize_text(titulo_elem.get_text(" ", strip=True) if titulo_elem else "")

    title_body = content_main.select_one(".title-body")
    if title_body:
        intro_paragraphs = []
        for p in title_body.select("p"):
            cleaned = normalize_text(p.get_text(" ", strip=True))
            if cleaned:
                intro_paragraphs.append(cleaned)
        texto = normalize_text(" ".join(intro_paragraphs))
    else:
        texto = ""

    # Extract campo aberto (news items)
    campo_aberto = []
    container = content_main.select_one(".field--name-field-campo-aberto-grupo-3")

    if container:
        for h2 in container.find_all("h2"):
            h2_titulo = normalize_text(h2.get_text(" ", strip=True))

            # Get all <p> tags until next <h2>
            paragraphs = []
            for sibling in h2.find_next_siblings():
                if sibling.name == "h2":
                    break
                if sibling.name == "p":
                    cleaned = normalize_text(sibling.get_text(" ", strip=True))
                    if cleaned:
                        paragraphs.append(cleaned)

            h2_texto = normalize_text(" ".join(paragraphs))

            campo_aberto.append({
                "titulo": h2_titulo,
                "texto": h2_texto
            })

    return {
        "titulo": f"Newsletter: {newsletter_id}",
        "link": link,
        "politecnicoTitulo": titulo,
        "politecnicoTexto": texto,
        "noticias": campo_aberto,
        "dataPublicacao": data_publicacao,
        "tipo": "Newsletter",
        "dateChecked": datetime.now().isoformat()
    }

async def scrape_newsletter(session, link_info, existing_data, semaphore):
    """Scrape a single newsletter"""
    url = link_info["link"]
    newsletter_id = extract_newsletter_id(url)
    data_publicacao = link_info.get("dataPublicacao", "")

    print(f"  Scraping newsletter {newsletter_id}...")

    html = await fetch_async(session, semaphore, url)
    if not html:
        return None

    content = parse_newsletter_content(html, newsletter_id, data_publicacao, url)
    if content:
        titulo = content["titulo"]
        if titulo not in existing_data:
            return titulo, content

    return None

async def _scrape_chunk(session, chunk, existing_data, all_data_shared, semaphore, prefix=""):
    """Scrape a chunk of newsletters"""
    for link_info in chunk:
        try:
            result = await scrape_newsletter(session, link_info, existing_data, semaphore)
            if result:
                titulo, content = result
                all_data_shared[titulo] = content
                print(f"  {prefix} Added: {titulo}")
        except Exception as e:
            print(f"  {prefix} Error scraping {link_info['link']}: {e}")


async def scrape_newsletters_parallel(links, semaphore, num_scrapers=NUM_SCRAPERS, force_full=False):
    """Scrape newsletters with parallel scrapers"""
    if force_full and Path(OUTPUT_FILE).exists():
        Path(OUTPUT_FILE).unlink()
        print(f"Removed existing {OUTPUT_FILE} before full scrape")

    previous_data = load_existing_data(OUTPUT_FILE)
    existing_data = {} if force_full else previous_data
    sort_key = "dataPublicacao"
    print(f"Loaded {len(previous_data)} existing items")

    all_data = {} if force_full else dict(previous_data)

    if not links:
        print("No links to scrape.")
        save_data(all_data, sort_key, OUTPUT_FILE)   # garante que o ficheiro fica gravado mesmo sem novos links (ex.: vazio, se force_full)
        return

    # Split links into chunks for parallel scrapers
    chunk_size = (len(links) + num_scrapers - 1) // num_scrapers
    chunks = [links[i:i + chunk_size] for i in range(0, len(links), chunk_size)]

    async with aiohttp.ClientSession() as session:
        tasks = []
        for i, chunk in enumerate(chunks):
            prefix = f"[Scraper {i+1}/{num_scrapers}]"
            task = _scrape_chunk(session, chunk, existing_data, all_data, semaphore, prefix)
            tasks.append(task)

        print(f"Starting {len(chunks)} parallel scrapers...\n")
        await asyncio.gather(*tasks)

    # Save all data
    save_data(all_data, sort_key, OUTPUT_FILE)

    # Summary
    new_count = len(all_data) - len(previous_data)
    _print_summary(previous_data, all_data)

async def main():
    print(f"\n{'='*50}")
    print(f"Newsletter Content Scraper")
    print(f"{'='*50}\n")

    semaphore = asyncio.Semaphore(CONCURRENT_REQUESTS)
    # Load newsletters to scrape
    links = load_links(INPUT_FILE)

    if not links:
        print("No links to scrape")
        return

    force_full = len(sys.argv) > 1 and sys.argv[1].strip().lower() == "true"
    if force_full:
        print("Force mode enabled: full scrape from page 0 (ignoring existing items)")

    print(f"Found {len(links)} newsletters to process\n")

    # Scrape in parallel
    await scrape_newsletters_parallel(links, semaphore, force_full=force_full)

if __name__ == "__main__":
    # Ensure documents directory exists
    BASE_PATH.mkdir(parents=True, exist_ok=True)
    asyncio.run(main())

