from unittest.mock import patch, MagicMock
import pytest
from pathlib import Path
import json
import scraper_cursos_links as scraper
from urllib.error import HTTPError
import time

def test_parse_curso_page_item_valido():
    html = """
        <div class="view-content-wrap">
        <div class="item">
            <div class="views-field-title"><a href="/licenciaturas/leic">LEIC</a></div>
            <div class="views-field-field-logo"><img alt="Logotipo ISEL - Versão acrónimo" /></div>
        </div>
    </div>
    """
    resultado = scraper.parse_curso_page(html)
    link = "https://www.ipl.pt/licenciaturas/leic"
    assert link in resultado
    assert resultado[link]["curso"] == "LEIC"
    assert resultado[link]["escola"] == "ISEL"
    assert resultado[link]["tipoCurso"] == "Licenciatura"

def test_parse_curso_page_item_sem_elemento_titulo():
    html = """
        <div class="view-content-wrap">
        <div class="item">
            <div class="views-field-field-logo"><img alt="Logotipo ISEL - Versão acrónimo" /></div>
        </div>
    </div>
    """
    resultado = scraper.parse_curso_page(html)
    assert resultado == {}

def test_parse_curso_page_item_sem_titulo():
    html = """
        <div class="view-content-wrap">
        <div class="item">
            <div class="views-field-title"><a href="/licenciaturas/leic"></a></div>
            <div class="views-field-field-logo"><img alt="Logotipo ISEL - Versão acrónimo" /></div>
        </div>
    </div>
    """
    resultado = scraper.parse_curso_page(html)
    assert resultado == {}

def test_parse_curso_page_item_sem_href():
    html = """
        <div class="view-content-wrap">
        <div class="item">
            <div class="views-field-title">LEIC</div>
            <div class="views-field-field-logo"><img alt="Logotipo ISEL - Versão acrónimo" /></div>
        </div>
    </div>
    """
    resultado = scraper.parse_curso_page(html)
    assert resultado == {}

def test_parse_curso_page_html_vazio():
    assert scraper.parse_curso_page("") == {}

def test_scrape_cursos_force_full_apaga_ficheiro(tmp_path, monkeypatch):
    ficheiro = tmp_path / "file.json"
    ficheiro.write_text('{"Antigo": {}}', encoding="utf-8")

    monkeypatch.setattr(scraper, "OUTPUT_FILE", str(ficheiro))
    monkeypatch.setattr(scraper, "_scrape_sequential", lambda *a, **k: None)

    scraper.scrape_cursos(force_full=True)
    assert ficheiro.exists() and ficheiro.read_text(encoding="utf-8") == '{}'