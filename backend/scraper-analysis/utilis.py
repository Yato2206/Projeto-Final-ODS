from pathlib import Path
import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
import aiohttp
import asyncio
from time import sleep
import re

# Função para carregar dados existentes de um arquivo JSON
# O parametro output_file é o caminho do arquivo JSON que contém os dados existentes, já que 
# os scrapers podem ser executados várias vezes, e queremos preservar os dados já coletados.
# Carrega um ficheiro
def load_existing_data(output_file):
    if Path(output_file).exists():
        with open(output_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

# Função para salvar dados em um arquivo JSON, ordenados segundo sort_key
def save_data(data, sort_key, output_file):
    sorted_data = dict(sorted(
        data.items(),
        key=lambda item: item[1].get(sort_key, ""),
        reverse=True
    ))

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(sorted_data, f, ensure_ascii=False, indent=2)
    print(f"Data saved! Total items: {len(sorted_data)}")

# Função para carregar os links de ficheiros JSON. 
# Usada para os scrapers que acedem a links de ficheiros JSON, como o scraper de newsletters e cursos.
# Parametro newsletter é um booleano que indica se os links são de newsletters(true) ou de cursos (falso)
def load_links(input_file, newsletter=True):
    if not Path(input_file).exists():
        print(f"Error: {input_file} not found")
        return []

    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Extract links and their publication dates
    links = []
    for title, info in data.items():
        if newsletter:
            links.append({
                "titulo": title,
                "link": info.get("link"),
                "dataPublicacao": info.get("dataPublicacao")
            })
        else: 
            links.append({
                "curso": info.get("curso"),
                "link": title,
                "tipoCurso": info.get("tipoCurso"),
                "escola": info.get("escola")
            })

    return links

# Versão síncrona da função fetch, para uso em scrapers que não utilizam asyncio
# Esta função é usada para buscar páginas web com tentativas de repetição em caso de falha.
# Por default, ela tenta 3 vezes fazer a requisição, com um tempo limite de 10 segundos para cada tentativa.
def fetch(url, timeout=10, retries=3):
    for attempt in range(retries):
        try:
            request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urlopen(request, timeout=timeout) as response:
                return response.read().decode("utf-8")
        except (HTTPError, URLError, TimeoutError) as e:
            if attempt < retries - 1:
                sleep(2 ** attempt)
            else:
                print(f"Failed to fetch {url}: {e}")
                return None
    return None

# Versão assíncrona da função fetch, para uso em scrapers que utilizam asyncio
async def fetch_async(session, semaphore, url, timeout=10, retries=3, debug_tag=None):
    for attempt in range(retries):
        try:
            async with semaphore:
                async with session.get(url, timeout=timeout) as response:
                    if response.status == 200:
                        return await response.text()
                    else:
                        print(f"Error fetching {url}: Status {response.status}")
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            if attempt < retries - 1:
                await asyncio.sleep(2 ** attempt)
            else:
                prefix = f"[{debug_tag}] " if debug_tag else ""
                print(f"{prefix}Failed to fetch {url}: {e}")
                return None
    return None

# Função para normalizar texto, removendo espaços extras e caracteres especiais
def normalize_text(raw_text):
        if not raw_text:
            return ""
        text = raw_text.replace("\xa0", " ")
        text = re.sub(r"\s+", " ", text).strip()
        text = re.sub(r"\s+([,.;:!?])", r"\1", text)
        text = re.sub(r"\(\s+", "(", text)
        text = re.sub(r"\s+\)", ")", text)
        return text

def _print_summary(existing_data, all_files):
    """Print scraping summary"""
    new_count = len(all_files) - len(existing_data)
    print(f"\n{'='*50}")
    print(f"Scraping completed!")
    print(f"Previous items: {len(existing_data)}")
    print(f"New items: {new_count}")
    print(f"Total items: {len(all_files)}")
    print(f"{'='*50}")

# Função para realizar scraping sequencial de páginas, usada em scrapers que não utilizam asyncio
# recebe como parâmetros a URL base, a função de parsing da página, a página inicial, os dados existentes, 
# o dicionário compartilhado para armazenar todos os dados coletados, o número mínimo de itens por página e um prefixo para logs.
def _scrape_sequential(base_url, parse_page, start_page, existing_data, all_shared, min_items_per_page, curso=None, prefix="[Sequential]"):
    """Core sequential scraping logic"""
    page = start_page
    first_item_key = None

    while True:
        url = f"{base_url}{curso}?page={page}" if curso else f"{base_url}?page={page}"
        print(f"  {prefix} Scraping page {page}...")

        html = fetch(url)
        if not html:
            print(f"  {prefix} No response from page {page}")
            break

        elements = parse_page(html)

        if not elements:
            print(f"  {prefix} No items found on page {page} -> End of pagination")
            break

        if not first_item_key:
            first_item_key = list(elements.keys())[0]
            if first_item_key in existing_data:
                print(f"  {prefix} First item already scraped -> Stopping (no new updates)")
                break

        new_items = 0
        for key, value in elements.items():
            if key not in all_shared:
                all_shared[key] = value
                new_items += 1

        print(f"  {prefix} Page {page}: {len(elements)} items ({new_items} new)")

        if len(elements) < min_items_per_page:
            print(f"  {prefix} Page {page} has fewer than {min_items_per_page} items -> Stopping")
            break

        if new_items == 0:
            print(f"  {prefix} No new items found -> All updates already scraped, stopping")
            break

        page += 1
        sleep(1)

async def _scrape_chunk(session, chunk, existing_data, all_data_shared, semaphore, scrape_func, prefix=""):
    """Scrape a chunk of items (newsletters or cursos)"""
    for link_info in chunk:
        try:
            result = await scrape_func(session, link_info, existing_data, semaphore)
            if result:
                title, content = result
                all_data_shared[title] = content
                print(f"  {prefix} Added: {title}")
        except Exception as e:
            print(f"  {prefix} Error scraping {link_info['link']}: {e}")


async def scrape_parallel(output_file, links, semaphore, sort_key, scrape_func, num_scrapers, force_full=False):
    """Scrape with parallel scrapers"""
    if force_full and Path(output_file).exists():
        Path(output_file).unlink()
        print(f"Removed existing {output_file} before full scrape")

    previous_data = load_existing_data(output_file)
    existing_data = {} if force_full else previous_data
    print(f"Loaded {len(previous_data)} existing items")

    all_data = {} if force_full else dict(previous_data)

    if not links:
        print("No links to scrape.")
        save_data(all_data, sort_key, output_file)   # garante que o ficheiro fica gravado mesmo sem novos links (ex.: vazio, se force_full)
        return

    # Split links into chunks for parallel scrapers
    chunk_size = (len(links) + num_scrapers - 1) // num_scrapers
    chunks = [links[i:i + chunk_size] for i in range(0, len(links), chunk_size)]

    async with aiohttp.ClientSession() as session:
        tasks = []
        for i, chunk in enumerate(chunks):
            prefix = f"[Scraper {i+1}/{num_scrapers}]"
            task = _scrape_chunk(session, chunk, existing_data, all_data, semaphore, scrape_func, prefix)
            tasks.append(task)

        print(f"Starting {len(chunks)} parallel scrapers...\n")
        await asyncio.gather(*tasks)

    # Save all data
    save_data(all_data, sort_key, output_file)

    # Summary
    new_count = len(all_data) - len(previous_data)
    _print_summary(previous_data, all_data)
