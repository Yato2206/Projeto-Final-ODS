from unittest.mock import patch, MagicMock
import pytest
from pathlib import Path
import json
import scraper_newsletter_all as scraper
from urllib.error import HTTPError
import time

def test_parse_page_item_valido():
    html = """
        <div class="view-content-wrap">
        <div class="item">
            <div class="views-field-title"><a href="/newsletter/123">Notícias Politécnico de Lisboa #123</a></div>
            <div class="views-field-field-data-envio">2026-06-20</div>
        </div>
    </div>
    """
    resultado = scraper.parse_page(html)
    assert "Notícias Politécnico de Lisboa #123" in resultado
    assert resultado["Notícias Politécnico de Lisboa #123"]["link"] == "https://www.ipl.pt/newsletter/123"
    assert resultado["Notícias Politécnico de Lisboa #123"]["dataPublicacao"] == "2026-06-20"

def test_parse_page_item_sem_elemento_titulo():
    html = """
        <div class="view-content-wrap">
        <div class="item">
            <div class="views-field-field-data-envio">2026-06-20</div>
        </div>
    </div>
    """
    resultado = scraper.parse_page(html)
    assert resultado == {}

def test_parse_page_item_sem_titulo():
    html = """
        <div class="view-content-wrap">
        <div class="item">
            <div class="views-field-title"><a href="/newsletter/123"></a></div>
            <div class="views-field-field-data-envio">2026-06-20</div>
        </div>
    </div>
    """
    resultado = scraper.parse_page(html)
    assert resultado == {}

def test_parse_page_item_sem_href():
    html = """
        <div class="view-content-wrap">
        <div class="item">
            <div class="views-field-title">Notícias Politécnico de Lisboa #123</div>
            <div class="views-field-field-data-envio">2026-06-20</div>
        </div>
    </div>
    """
    resultado = scraper.parse_page(html)
    assert resultado == {}

def test_parse_page_html_vazio():
    assert scraper.parse_page("") == {}

def test_scrape_sequential(monkeypatch):
    html_page_0 = "<div class='view-content-wrap'>" + \
        "".join(f'<div class="item"><div class="views-field-title"><a href="/n{i}">Newsletter {i}</a></div></div>' for i in range(10)) + \
        "</div>" # simula uma página com 10 itens
    html_page_1 = """
        <div class="view-content-wrap">
            <div class="item"><div class="views-field-title"><a href="/n10">Newsletter 10</a></div></div>
        </div>
    """
    chamadas = {"n": 0}
    
    def mock_fetch(url):
        chamadas["n"] += 1
        return html_page_0 if chamadas["n"] == 1 else html_page_1

    all_news = {}
    monkeypatch.setattr(scraper, 'fetch', mock_fetch)
    monkeypatch.setattr(scraper, 'sleep', lambda x: None)  # Evita delays durante o teste
    scraper._scrape_sequential(0, {}, all_news)
    assert len(all_news) == 11
    assert chamadas["n"] == 2

def test_scrape_sequential_sem_items_novos(monkeypatch):
    html = """
        <div class="view-content-wrap">
            <div class="item"><div class="views-field-title"><a href="/ja/existe">Newsletter Já Existente</a></div></div>
        </div>
    """

    monkeypatch.setattr(scraper, 'fetch', lambda url: html)
    existing_data = {"Newsletter Já Existente": {"link": "https://www.ipl.pt/ja/existe"}}
    all_news = dict(existing_data)  # Copia para simular o estado inicial

    scraper._scrape_sequential(0, existing_data, all_news)
    assert len(all_news) == 1  # Nenhum novo item deve ser adicionado

def test_scrape_sequential_com_items_novos_e_existentes_mesma_pagina(monkeypatch):
    html_existente = """
        <div class="view-content-wrap">
            <div class="item"><div class="views-field-title"><a href="/ja/existe">Newsletter Já Existente</a></div></div>
        </div>
    """

    html_novo = """
        <div class="view-content-wrap">
            <div class="item"><div class="views-field-title"><a href="/novo">Newsletter Nova</a></div></div>
        </div>
    """

    existing_data = {"Newsletter Já Existente": {"link": "https://www.ipl.pt/ja/existe"}}
    all_news = dict(existing_data)  # Copia para simular o estado inicial

    chamadas = {"n": 0}
    
    def mock_fetch(url):
        chamadas["n"] += 1
        return html_novo if chamadas["n"] == 1 else html_existente

    monkeypatch.setattr(scraper, 'fetch', mock_fetch)
    monkeypatch.setattr(scraper, 'sleep', lambda x: None)  # Evita delays durante o teste
    scraper._scrape_sequential(0, existing_data, all_news)
    assert chamadas["n"] == 1
    assert len(all_news) == 2  # Um item existente e um novo
    
def test_scrape_sequential_pagina_com_items_novos_e_existentes(monkeypatch):
    items_html = "".join(
        f'<div class="item"><div class="views-field-title"><a href="/item{i}">Newsletter {i}</a></div></div>'
        for i in range(9, -1, -1)
    )
    html_pagina_0 = f'<div class="view-content-wrap">{items_html}</div>'
    html_pagina_1 = '<div class="view-content-wrap"></div>'

    existing_data = {
        "Newsletter 0": {"link": "https://www.ipl.pt/item0"},
        "Newsletter 1": {"link": "https://www.ipl.pt/item1"},
    }
    all_news = dict(existing_data)

    chamadas = {"n": 0}
    def mock_fetch(url):
        chamadas["n"] += 1
        return html_pagina_0 if chamadas["n"] == 1 else html_pagina_1

    monkeypatch.setattr(scraper, 'fetch', mock_fetch)
    monkeypatch.setattr(scraper, 'sleep', lambda x: None)
    scraper._scrape_sequential(0, existing_data, all_news)

    assert len(all_news) == 10          # 2 existentes + 8 novos
    assert chamadas["n"] == 2           # avançou para a página 1 (10 itens == MIN_ITEMS_PER_PAGE)

def test_scrape_newsletters_force_full_apaga_ficheiro(tmp_path, monkeypatch):
    ficheiro = tmp_path / "file.json"
    ficheiro.write_text('{"Antigo": {}}', encoding="utf-8")

    monkeypatch.setattr(scraper, "OUTPUT_FILE", str(ficheiro))
    monkeypatch.setattr(scraper, "_scrape_sequential", lambda *a, **k: None)

    scraper.scrape_newsletters(force_full=True)
    assert ficheiro.exists() and ficheiro.read_text(encoding="utf-8") == '{}'