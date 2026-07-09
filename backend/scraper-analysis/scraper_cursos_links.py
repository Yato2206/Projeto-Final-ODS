import json
from bs4 import BeautifulSoup
from datetime import datetime
from pathlib import Path
import sys
from time import sleep
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from utilis import load_existing_data, save_data, fetch, _print_summary, _scrape_sequential

# Configuração
BASE_URL = "https://www.ipl.pt/estudar/cursos/"
OUTPUT_FILE = "documents/cursos/cursos_links.json"
RETRIES = 3
MIN_ITEMS_PER_PAGE = 12

def parse_curso_page(html):
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

        mapeamento_graus = {
            "licenciaturas": "Licenciatura",
            "mestrados": "Mestrado",
            "pos-graduacoes": "Pos-Graduação"
        }

        grau = "Desconhecido"
        for chave, valor in mapeamento_graus.items():
            if chave in link:
                grau = valor
                break 

        cursos[link] = {
            "curso": titulo,
            "escola": escola,
            "dateChecked": datetime.now().isoformat(),
            "tipoCurso": grau
        }

    return cursos

def scrape_cursos():
    existing_data = {}
    all_cursos = {} 

    for curso in ["licenciaturas", "mestrados", "pos-graduacoes"]:
        _scrape_sequential(BASE_URL, parse_curso_page, 0, existing_data, all_cursos, MIN_ITEMS_PER_PAGE, curso, prefix=f"[{curso.capitalize()}]")

    sort_key = "dateChecked"
    save_data(all_cursos, sort_key, OUTPUT_FILE)
    _print_summary(existing_data, all_cursos)


def main():
    print(f"\n{'='*50}")
    print(f"Cursos Scraper")
    print(f"{'='*50}\n")

    scrape_cursos()


if __name__ == "__main__":
    # Ensure documents directory exists
    Path("documents/cursos/").mkdir(parents=True, exist_ok=True)
    main()