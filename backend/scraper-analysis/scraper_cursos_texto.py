import asyncio
import json
import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime
from pathlib import Path
import sys
from urllib.parse import urlparse
import re
from utilis import load_existing_data, load_links, save_data, fetch_async, normalize_text, _print_summary, _scrape_chunk, scrape_parallel

# Configuração
BASE_PATH = Path("documents/cursos/")
INPUT_FILE = BASE_PATH / "cursos_links.json"
OUTPUT_FILE = BASE_PATH / "cursos_content.json"
CONCURRENT_REQUESTS = 5
RETRIES = 3
NUM_SCRAPERS = 5

#semaphore = asyncio.Semaphore(CONCURRENT_REQUESTS)

def parse_curso_content(html, curso, tipoCurso, escola, link):
    """Parse curso HTML and extract content"""
    soup = BeautifulSoup(html, 'html.parser')

    content_main = soup.select_one(".node__content.clearfix")
    if not content_main:
        return None

    texto = content_main.select_one(".field--name-body")
    if not texto:
        return None

    return {
        "curso": curso,
        "link": link,
        "escola": escola,
        "texto": texto.get_text(separator="\n", strip=True),
        "tipoCurso": tipoCurso,
        "dateChecked": datetime.now().isoformat()
    }

async def scrape_cursos(session, link_info, existing_data, semaphore):
    """Scrape a single curso"""
    url = link_info["link"]
    curso = link_info.get("curso", "")
    tipoCurso = link_info.get("tipoCurso", "")
    escola = link_info.get("escola", "")
    html = await fetch_async(session, semaphore, url)
    if not html:
        return None

    content = parse_curso_content(html, curso, tipoCurso, escola, url)
    if content:
        curso = content["link"]
        if curso not in existing_data:
            return curso, content

    return None

async def main():
    print(f"\n{'='*50}")
    print(f"Curso Content Scraper")
    print(f"{'='*50}\n")

    semaphore = asyncio.Semaphore(CONCURRENT_REQUESTS)

    # Load cursos to scrape
    curso_fields = {
        "curso":          "curso",           
        "link":           None,           
        "tipoCurso":      "tipoCurso",
        "escola":         "escola",
    }
    links = load_links(INPUT_FILE, curso_fields)

    if not links:
        print("No links to scrape")
        return

    force_full = len(sys.argv) > 1 and sys.argv[1].strip().lower() == "true"
    if force_full:
        print("Force mode enabled: full scrape from page 0 (ignoring existing items)")

    print(f"Found {len(links)} cursos to process\n")

    sort_key = "dateChecked"
    # Scrape in parallel
    await scrape_parallel(OUTPUT_FILE, links, semaphore, sort_key, scrape_cursos, NUM_SCRAPERS, force_full=force_full)

if __name__ == "__main__":
    # Ensure documents directory exists
    BASE_PATH.mkdir(parents=True, exist_ok=True)
    asyncio.run(main())
