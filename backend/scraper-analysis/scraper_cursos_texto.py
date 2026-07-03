import asyncio
import json
import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime
from pathlib import Path
import sys
from urllib.parse import urlparse
import re

# Configuração
BASE_PATH = Path("documents/cursos/")
INPUT_FILE = BASE_PATH / "cursos_links.json"
OUTPUT_FILE = BASE_PATH / "cursos_content.json"
CONCURRENT_REQUESTS = 5
RETRIES = 3
NUM_SCRAPERS = 5

semaphore = asyncio.Semaphore(CONCURRENT_REQUESTS)


#esta funcao ficara num ficheiro utils e sera importada para os outros scrapers, para evitar a duplicacao de codigo
def load_cursos_links():
    """Load cursos links from file"""
    if not Path(INPUT_FILE).exists():
        print(f"Error: {INPUT_FILE} not found")
        return []

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Extract links and their publication dates
    links = []
    for title, info in data.items():
        links.append({
            "titulo": info.get("curso"),
            "link": title,
            "tipoCurso": info.get("tipoCurso"),
            "escola": info.get("escola")
        })

    return links


#esta funcao ficara num ficheiro utils e sera importada para os outros scrapers, para evitar a duplicacao de codigo
def load_existing_data():
    """Load existing curso content"""
    if Path(OUTPUT_FILE).exists():
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


#esta funcao ficara num ficheiro utils e sera importada para os outros scrapers, para evitar a duplicacao de codigo
def save_data(data):
    """Save curso content to file, sorted by publication date"""
    # Sort by publication date (newest first)
    sorted_data = dict(sorted(
        data.items(),
        key=lambda x: x[1].get("dataPublicacao") or "",
        reverse=True
    ))

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(sorted_data, f, ensure_ascii=False, indent=2)
    print(f"Newsletter content saved! Total items: {len(sorted_data)}")


#esta funcao ficara num ficheiro utils e sera importada para os outros scrapers, para evitar a duplicacao de codigo
async def fetch(session, url):
    """Fetch page with retries"""
    for attempt in range(RETRIES):
        try:
            async with semaphore:
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        return await response.text()
                    else:
                        print(f"Error fetching {url}: Status {response.status}")
        except Exception as e:
            if attempt < RETRIES - 1:
                await asyncio.sleep(2 ** attempt)
            else:
                print(f"Failed to fetch {url}: {e}")
                return None
    return None

def parse_newsletter_content(html, titulo, tipoCurso, escola, link):
    """Parse newsletter HTML and extract content"""
    soup = BeautifulSoup(html, 'html.parser')

    def normalize_text(raw_text):
        if not raw_text:
            return ""
        text = raw_text.replace("\xa0", " ")
        text = re.sub(r"\s+", " ", text).strip()
        text = re.sub(r"\s+([,.;:!?])", r"\1", text)
        text = re.sub(r"\(\s+", "(", text)
        text = re.sub(r"\s+\)", ")", text)
        return text

    content_main = soup.select_one(".node__content.clearfix")
    if not content_main:
        return None

    texto = content_main.select_one(".field--name-body")
    if not texto:
        return None

    return {
        "curso": titulo,
        "link": link,
        "escola": escola,
        "texto": texto.get_text(separator="\n", strip=True),
        "tipoCurso": tipoCurso,
        "dateChecked": datetime.now().isoformat()
    }

async def scrape_newsletter(session, link_info, existing_data):
    """Scrape a single newsletter"""
    url = link_info["link"]
    titulo = link_info.get("titulo", "")
    tipoCurso = link_info.get("tipoCurso", "")
    escola = link_info.get("escola", "")
    html = await fetch(session, url)
    if not html:
        return None

    content = parse_newsletter_content(html, titulo, tipoCurso, escola, url)
    if content:
        curso = content["link"]
        if curso not in existing_data:
            return curso, content

    return None

async def _scrape_chunk(session, chunk, existing_data, all_data_shared, prefix=""):
    """Scrape a chunk of newsletters"""
    for link_info in chunk:
        try:
            result = await scrape_newsletter(session, link_info, existing_data)
            if result:
                titulo, content = result
                all_data_shared[titulo] = content
                print(f"  {prefix} Added: {titulo}")
        except Exception as e:
            print(f"  {prefix} Error scraping {link_info['link']}: {e}")


async def scrape_newsletters_parallel(links, num_scrapers=NUM_SCRAPERS, force_full=False):
    """Scrape newsletters with parallel scrapers"""
    if force_full and Path(OUTPUT_FILE).exists():
        Path(OUTPUT_FILE).unlink()
        print(f"Removed existing {OUTPUT_FILE} before full scrape")

    previous_data = load_existing_data()
    existing_data = {} if force_full else previous_data
    print(f"Loaded {len(previous_data)} existing items")

    all_data = {} if force_full else dict(previous_data)

    if not links:
        print("No links to scrape.")
        save_data(all_data)   # garante que o ficheiro fica gravado mesmo sem novos links (ex.: vazio, se force_full)
        return

    # Split links into chunks for parallel scrapers
    chunk_size = (len(links) + num_scrapers - 1) // num_scrapers
    chunks = [links[i:i + chunk_size] for i in range(0, len(links), chunk_size)]

    async with aiohttp.ClientSession() as session:
        tasks = []
        for i, chunk in enumerate(chunks):
            prefix = f"[Scraper {i+1}/{num_scrapers}]"
            task = _scrape_chunk(session, chunk, existing_data, all_data, prefix)
            tasks.append(task)

        print(f"Starting {len(chunks)} parallel scrapers...\n")
        await asyncio.gather(*tasks)

    # Save all data
    save_data(all_data)

    # Summary
    new_count = len(all_data) - len(previous_data)
    print(f"\n{'='*50}")
    print(f"Parallel scraping completed!")
    print(f"Previous items: {len(previous_data)}")
    print(f"New items: {new_count}")
    print(f"Total items: {len(all_data)}")
    print(f"{'='*50}")

async def main():
    print(f"\n{'='*50}")
    print(f"Curso Content Scraper")
    print(f"{'='*50}\n")

    # Load cursos to scrape
    links = load_cursos_links()

    if not links:
        print("No links to scrape")
        return

    # Optional force mode: py .\scraper-python-newsletter-each.py true
    force_full = len(sys.argv) > 1 and sys.argv[1].strip().lower() == "true"
    if force_full:
        print("Force mode enabled: full scrape from page 0 (ignoring existing items)")

    print(f"Found {len(links)} cursos to process\n")

    # Scrape in parallel
    await scrape_newsletters_parallel(links, NUM_SCRAPERS, force_full=force_full)

if __name__ == "__main__":
    # Ensure documents directory exists
    BASE_PATH.mkdir(parents=True, exist_ok=True)
    asyncio.run(main())
