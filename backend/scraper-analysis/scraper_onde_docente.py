import json
from bs4 import BeautifulSoup
from datetime import datetime
from pathlib import Path
import sys
from time import sleep
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from utilis import load_existing_data, save_data, fetch, _print_summary

#Provavelmente sera partilhado
escolas = ["ESCS", "ESD", "ESELX", "ESML", "ESTC", "ESSL", "ISCAL", "ISEL"]
#escolas = ["ESCS"]

ESCS_DEPARTAMENTOS = [
    "audiovisual-e-multimedia",
    "ciencias-da-comunicacao",
    "ciencias-humanas",
    "ciencias-sociais",
    "estatistica",
    "media-e-jornalismo",
    "publicidade-e-marketing",
    "relacoes-publicas-e-comunicacao-organizacional",
]

OUTPUT_FILE = "escolas/departamentos.json"
RETRIES = 3

def define_base_url(escola):
    match escola:
        case "ESELX":
            return "https://www.eselx.ipl.pt/eselx/orgaos-cientificos-pedagogicos/departamentos"
        case "ESML":
            return "https://www.esml.ipl.pt/home/pessoas/corpo-docente"
        case "ISEL":
            return "https://www.isel.pt/isel/quem-somos/departamentos"
        case _:
            return None


"""
    o ESD, o ESTC, ESSL e o ISCAL não possuem uma secção de departamento como as demais escolas para poder depois buscar os docentes por departamento
"""
def departamento_parse(items, escola):
    #print(items)
    departamentos = {}
    for element in items:
        #print(f"Processing element: {element}")
        match escola:
            case "ESELX":
                nome_elem = element.select_one("a")
                base_link = f"https://www.eselx.ipl.pt"
            case "ESML":
                nome_elem = element.select_one("a")
                base_link = f"https://www.esml.ipl.pt"
            case "ISEL":
                nome_elem = element.select_one(".be-desc a")
                base_link = f"https://www.isel.pt"
        
        #print(f"Nome element: {nome_elem}")
        if not nome_elem:
            print(f"  [Departamento Scrape] No nome element found in item, skipping")
            continue
        nome = nome_elem.get_text(strip=True)
        if not nome:
            print(f"  [Departamento Scrape] Empty nome found, skipping")
            continue
        href = nome_elem.get('href')
        if not href:
            print(f"  [Departamento Scrape] No href found for {nome}, skipping")
            continue
        link = base_link + href if href.startswith('/') else href
        #print(f"Link: {link}")
       
        departamentos[nome] = {
            "escola": escola,
            "link": link,
            "dateChecked": datetime.now().isoformat()
        }

        #print(f"  [Departamento Scrape] Found: {nome} - {link}")

    return departamentos

def choose_departamento_parse_html(html, escola):
    """Parse page and extract newsletter items"""
    soup = BeautifulSoup(html, 'html.parser')
    match escola:
        case "ESELX":
            items = soup.select(".content-main p")
            return departamento_parse(items, escola)
        case "ESML":
            items = soup.select(".category-desc h3")
            return departamento_parse(items, escola)
        case "ISEL":
            items = soup.select(".gsc-column.col-lg-2")
            #print(items)
            return departamento_parse(items, escola)
        case _:
            return {}

def scrape_sequential(escola, existing_data, all_deps_shared, prefix="[Sequential]"):
    """Core sequential scraping logic"""
    first_item_key = None

    url = define_base_url(escola)
    if not url:
        print(f"Os docentes podem ser obtidos direto. Não precisa de scrap dos departamentos para a escola {escola}")
        return

    html = fetch(url)
    if not html:
        print(f"  {prefix} No response")
        return

    departamentos = choose_departamento_parse_html(html, escola)

    if not departamentos:
        print(f"  {prefix} No items found")
        return

    if not first_item_key:
        first_item_key = list(departamentos.keys())[0]
        if first_item_key in existing_data:
            print(f"  {prefix} First item already scraped → Stopping (no new updates)")
            return

    new_items = 0
    for key, value in departamentos.items():
        if key not in all_deps_shared:
            all_deps_shared[key] = value
            new_items += 1

    print(f"  {prefix} {len(departamentos)} items ({new_items} new)")

    if new_items == 0:
        print(f"  {prefix} No new items found → All updates already scraped, stopping")
        return

#    o ESCS é um caso especial. Apesar de possuir departamentos, não é possível realizar o scrape desses departamentos, pelo que têm de ser
#    fornecidos diretamente.
def scrape_departamentos(escola):
    """Scrape departamentos for all schools"""
    existing_data = load_existing_data(OUTPUT_FILE)
    print(f"Loaded {len(existing_data)} existing items")

    all_deps = dict(existing_data)

    if escola == "ESCS":
        for dep in ESCS_DEPARTAMENTOS:
            all_deps[dep] = {
                "escola": escola,
                "link": f"https://www.escs.ipl.pt/escola/departamentos/{dep}",
                "dateChecked": datetime.now().isoformat()
            }
        print(f"  [Sequential] {len(ESCS_DEPARTAMENTOS)} items added for ESCS")

    scrape_sequential(escola, existing_data, all_deps)

    sort_key = "dateChecked"
    save_data(all_deps, sort_key, OUTPUT_FILE)
    _print_summary(existing_data, all_deps) #NOTA para cada link diferente, o ficheiro e aberto e fechado por isso o numero no final de novos items pode nao corresponder com o de facto adicionado

def main():
    print(f"\n{'='*50}")
    print(f"Departamentos Scraper")
    print(f"{'='*50}\n")

    for escola in escolas:
        print(f"\n{'-'*50}")
        print(f"Scraping {escola}...")
        print(f"{'-'*50}\n")
        scrape_departamentos(escola)

if __name__ == "__main__":
    Path("escolas").mkdir(parents=True, exist_ok=True)
    main()
