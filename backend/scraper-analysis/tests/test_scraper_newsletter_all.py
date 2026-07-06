from unittest.mock import patch, MagicMock
import pytest
from pathlib import Path
import json
import scraper_newsletter_all as scraper
from urllib.error import HTTPError
import time

def test_parse_newsletter_page_item_valido():
    html = """
        <div class="view-content-wrap">
        <div class="item">
            <div class="views-field-title"><a href="/newsletter/123">Notícias Politécnico de Lisboa #123</a></div>
            <div class="views-field-field-data-envio">2026-06-20</div>
        </div>
    </div>
    """
    resultado = scraper.parse_newsletter_page(html)
    assert "Notícias Politécnico de Lisboa #123" in resultado
    assert resultado["Notícias Politécnico de Lisboa #123"]["link"] == "https://www.ipl.pt/newsletter/123"
    assert resultado["Notícias Politécnico de Lisboa #123"]["dataPublicacao"] == "2026-06-20"

def test_parse_newsletter_page_item_sem_elemento_titulo():
    html = """
        <div class="view-content-wrap">
        <div class="item">
            <div class="views-field-field-data-envio">2026-06-20</div>
        </div>
    </div>
    """
    resultado = scraper.parse_newsletter_page(html)
    assert resultado == {}

def test_parse_newsletter_page_item_sem_titulo():
    html = """
        <div class="view-content-wrap">
        <div class="item">
            <div class="views-field-title"><a href="/newsletter/123"></a></div>
            <div class="views-field-field-data-envio">2026-06-20</div>
        </div>
    </div>
    """
    resultado = scraper.parse_newsletter_page(html)
    assert resultado == {}

def test_parse_newsletter_page_item_sem_href():
    html = """
        <div class="view-content-wrap">
        <div class="item">
            <div class="views-field-title">Notícias Politécnico de Lisboa #123</div>
            <div class="views-field-field-data-envio">2026-06-20</div>
        </div>
    </div>
    """
    resultado = scraper.parse_newsletter_page(html)
    assert resultado == {}

def test_parse_newsletter_page_html_vazio():
    assert scraper.parse_newsletter_page("") == {}

def test_scrape_newsletters_force_full_apaga_ficheiro(tmp_path, monkeypatch):
    ficheiro = tmp_path / "file.json"
    ficheiro.write_text('{"Antigo": {}}', encoding="utf-8")

    monkeypatch.setattr(scraper, "OUTPUT_FILE", str(ficheiro))
    monkeypatch.setattr(scraper, "_scrape_sequential", lambda *a, **k: None)

    scraper.scrape_newsletters(force_full=True)
    assert ficheiro.exists() and ficheiro.read_text(encoding="utf-8") == '{}'