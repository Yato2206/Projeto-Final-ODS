import asyncio
import json
import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from urllib.parse import urljoin, urlsplit, urlunsplit
import re
import glob
from pathlib import Path

CONCURRENT_REQUESTS = 50
CONCURRENT_SCRAPPES = 15
RETRIES = 3
ITEMS_PER_FILE = 1000
BATCH_SIZE = 100

semaphore = asyncio.Semaphore(CONCURRENT_REQUESTS)
scrape_semaphore = asyncio.Semaphore(CONCURRENT_SCRAPPES)
failed_urls = {}
current_file_index = 1
items_in_current_file = 0
file_lock = asyncio.Lock()

async def fetch(session, url):
    for attempt in range(RETRIES):
        try:
            async with semaphore:
                async with session.get(url, timeout=10) as response:
                    text = await response.text()

                    if "alert alert-info" in text:
                        print(" Página vazia (alert-info):", url)
                        return text

                    if "alert alert-danger" in text:
                        failed_urls[url] = failed_urls.get(url, 0) + 1
                        print(f"️ Alert-danger em {url} (tentativa {failed_urls[url]})")

                        if failed_urls[url] <= 3:
                            await asyncio.sleep(2 ** attempt)
                            continue
                        else:
                            print("Falha definitiva:", url)
                            return None

                    return text

        except asyncio.TimeoutError:
            print(f"Timeout em {url} (tentativa {attempt + 1})")
            await asyncio.sleep(2 ** attempt)
        except Exception as e:
            print(f" Erro ao fazer fetch {url}: {e}")
            await asyncio.sleep(2 ** attempt)

    print(f"Esgotadas tentativas para {url}")
    return None

def get_data_filename(index):
    return f"repo_cientifico_{index}.json"

def get_current_file_index():
    existing_files = glob.glob("repo_cientifico_*.json")
    if not existing_files:
        return 1
    indices = []
    for file in existing_files:
        try:
            idx = int(file.replace("repo_cientifico_", "").replace(".json", ""))
            indices.append(idx)
        except:
            pass
    return max(indices) if indices else 1

def load_all_existing_data():
    done_links = set()
    total_count = 0

    existing_files = glob.glob("repo_cientifico_*.json")
    for file in existing_files:
        try:
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    done_links.update(data.keys())
                    total_count += len(data)
        except:
            pass

    return done_links, total_count

async def save_to_rotating_file(data_batch):
    global current_file_index, items_in_current_file

    async with file_lock:
        remaining_items = dict(data_batch)

        while remaining_items:
            current_filename = get_data_filename(current_file_index)

            try:
                with open(current_filename, "r", encoding="utf-8") as f:
                    current_data = json.load(f)
            except:
                current_data = {}

            items_in_current_file = len(current_data)
            space_available = ITEMS_PER_FILE - items_in_current_file

            if space_available <= 0:
                current_file_index += 1
                print(f" Rotacionando para {get_data_filename(current_file_index)}")
                continue

            items_to_add = dict(list(remaining_items.items())[:space_available])
            current_data.update(items_to_add)

            with open(current_filename, "w", encoding="utf-8") as f:
                json.dump(current_data, f, ensure_ascii=False, indent=2)

            print(f" Guardado em {current_filename} ({len(current_data)} items)")

            for key in items_to_add:
                del remaining_items[key]

            if len(current_data) >= ITEMS_PER_FILE:
                current_file_index += 1
                print(f" Ficheiro cheio → Rotacionando para {get_data_filename(current_file_index)}")

def save_failed():
    with open("failed_or_missed_urls.json", "w", encoding="utf-8") as f:
        json.dump(failed_urls, f, indent=2)

def extract_item_data(element, base_url):
    """Extrai dados completos de um elemento"""
    a = element.select_one('a')
    if not a:
        return None, None

    rawA = a.get_text(strip=True)
    titulo = re.split(r'\d{4}', rawA)[0].strip()

    href = a.get('href')
    link = urljoin("https://repositorio.ipl.pt", href) if href else None

    if not link:
        return None, None

    tag_elements = element.select('.tag_elements a')

    data = {
        "titulo": titulo,
        "colectionOrigin": base_url,
        "autores": (
            element.select_one('.clamp-default-2 .item-list-authors')
            .get_text(strip=True)
            if element.select_one('.clamp-default-2 .item-list-authors')
            else ""
        ),
        "texto": (
            element.select_one('.clamp-default-3 .content span')
            .get_text(strip=True)
            if element.select_one('.clamp-default-3 .content span')
            else ""
        ),
        "dataPublicacao": tag_elements[0].get_text(strip=True) if len(tag_elements) > 0 else "",
        "tipo": tag_elements[1].get_text(strip=True) if len(tag_elements) > 1 else "",
        "acesso": (
            element.select_one('.access-status-list-element-badge a')
            .get_text(strip=True)
            if element.select_one('.access-status-list-element-badge a')
            else ""
        ),
        "dateChecked": datetime.now(timezone.utc).isoformat()
    }

    return link, data

def parse_page(html, base_url, seen_links):
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.select(".mt-4.mb-4.d-flex")
    news = {}

    for element in items:
        link, data = extract_item_data(element, base_url)
        
        if not link or link in news:
            continue
        if link in seen_links:
            continue
        seen_links.add(link)
        
        news[link] = data

    return news

async def scrape_item_details(session, item_link, base_url):
    """Acede a um item individual e extrai dados completos via .row .entity-publication"""
    html = await fetch(session, item_link)
    if not html:
        return {}
    
    soup = BeautifulSoup(html, 'html.parser')
    detail_items = soup.select(".row .entity-publication")
    details = {}
    
    for element in detail_items:
        link, data = extract_item_data(element, base_url)
        
        if link and link not in details:
            details[link] = data
    
    return details

def clean_url(url):
    parts = urlsplit(url)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))

async def scrape_collection(session, base_url):
    base_url = clean_url(base_url)
    page = 1
    batch = {}
    consecutive_empty_pages = 0
    max_consecutive_empty = 1
    seen_links = set()
    
    # Detectar se é a coleção especial - Projetos
    is_special_collection = "75734783-5a52-4f7c-9cb0-6831e738f280" in base_url

    while True:
        url = f"{base_url}?cp.page={page}"
        print("A processar:", url)

        html = await fetch(session, url)

        if not html:
            print(f"Página inacessível, pulando...")
            page += 1
            consecutive_empty_pages += 1
            if consecutive_empty_pages >= max_consecutive_empty:
                print(f" {max_consecutive_empty} páginas consecutivas inacessíveis → fim")
                break
            continue

        if "alert alert-info" in html:
            print(f"Página com alert-info (vazia), continuando...")
            consecutive_empty_pages += 1
            page += 1
            if consecutive_empty_pages >= max_consecutive_empty:
                print(f"{max_consecutive_empty} páginas vazias consecutivas → fim")
                break
            continue

        if "alert alert-danger" in html:
            print("Erro na página, a saltar...")
            page += 1
            consecutive_empty_pages += 1
            if consecutive_empty_pages >= max_consecutive_empty:
                print(f"{max_consecutive_empty} páginas com erro consecutivas → fim")
                break
            continue

        # Sempre usar o seletor normal para extrair items
        items = BeautifulSoup(html, "html.parser").select(".mt-4.mb-4.d-flex")

        if len(items) == 0:
            print(f"Nenhum item encontrado na página, continuando...")
            consecutive_empty_pages += 1
            page += 1
            if consecutive_empty_pages >= max_consecutive_empty:
                print(f"{max_consecutive_empty} páginas vazias → fim da coleção")
                break
            continue

        consecutive_empty_pages = 0
        
        # Usar função de parse apropriada
        if is_special_collection:
            # Para coleção especial (Projetos): scrape normal primeiro, depois acede a cada link
            news = parse_page(html, base_url, seen_links)
            
            # Para cada link extraído, aceder a ele e fazer scrape com campos completos
            # Fazer isso EM PARALELO com asyncio.gather
            if news:
                tasks = [scrape_item_details(session, link, base_url) for link in news.keys()]
                detailed_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                detailed_news = {}
                for result in detailed_results:
                    if isinstance(result, dict):
                        detailed_news.update(result)
                
                print(f"  → {len(detailed_news)} items obtidos em paralelo")
                news = detailed_news
            else:
                news = {}
        else:
            news = parse_page(html, base_url, seen_links)

        if len(items) > 0 and len(news) == 0:
            print(f"Página repetida, provavelmente cópia da última em {url}")
            print(f"Total na página: {len(items)} | Novos: {len(news)} | {url}")
            print(f"Fim da coleção detectado → parando")
            break
        print(f"Total na página: {len(items)} | Novos: {len(news)} | {url}")

        batch.update(news)

        if len(batch) >= BATCH_SIZE:
            await save_to_rotating_file(batch)
            batch = {}

        page += 1

    if batch:
        await save_to_rotating_file(batch)

    return True

async def limited_scrape(session, url):
    async with scrape_semaphore:
        return await scrape_collection(session, url)

async def main():
    global current_file_index

    current_file_index = get_current_file_index()

    done_links, total_existing = load_all_existing_data()
    print(f"Dados existentes: {total_existing} items em {len(glob.glob('repo_cientifico_*.json'))} ficheiros")
    print(f"Próximo ficheiro será: {get_data_filename(current_file_index)}")

    try:
        with open("results_links.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        
        if isinstance(data, list):
            all_links = [item["link"] for item in data]
        else:
            all_links = list(data.keys())
    except:
        print("Erro a carregar results_links.json")
        return

    try:
        with open("failed_or_missed_urls.json", "r") as f:
            failed = json.load(f)
    except:
        failed = {}

    retry_links = list(failed.keys())
    new_links = [url for url in all_links if url not in failed]

    print(f"\n{'='*100}")
    print(f"Links para retry: {len(retry_links)}")
    print(f"Links para processar: {len(new_links)}")
    print(f"{'='*100}\n")

    if not retry_links and not new_links:
        print("Nada para fazer!")
        return

    async with aiohttp.ClientSession() as session:
        if retry_links:
            print(f"\n FASE 1: Retry dos {len(retry_links)} links falhados ({CONCURRENT_SCRAPPES} em paralelo)\n")
            retry_tasks = [limited_scrape(session, url) for url in retry_links]
            await asyncio.gather(*retry_tasks, return_exceptions=True)

        if new_links:
            print(f"\nFASE 2: Scrap dos {len(new_links)} links ({CONCURRENT_SCRAPPES} em paralelo)\n")
            new_tasks = [limited_scrape(session, url) for url in new_links]
            await asyncio.gather(*new_tasks, return_exceptions=True)

    save_failed()

    all_files = glob.glob('repo_cientifico_*.json')
    total_items = 0
    for file in all_files:
        try:
            with open(file, "r", encoding="utf-8") as f:
                total_items += len(json.load(f))
        except:
            pass

    print(f"\n{'='*100}")
    print(f"Scrap completo!")
    print(f"Ficheiros: {len(all_files)}")
    print(f"Total de items: {total_items}")
    print(f"{'='*100}\n")

asyncio.run(main())

