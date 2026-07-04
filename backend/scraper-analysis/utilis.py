from pathlib import Path
import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
import aiohttp
import asyncio
from time import sleep
import re

# Função para carregar dados existentes de um arquivo JSON
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
                "titulo": info.get("curso"),
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
