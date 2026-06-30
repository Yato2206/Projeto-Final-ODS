from unittest.mock import patch, MagicMock, AsyncMock
import asyncio
import pytest
from pathlib import Path
import json
import scraper_onde_docente as scraper
from urllib.error import HTTPError
from datetime import datetime
from bs4 import BeautifulSoup

def test_define_base_url_success():
    assert scraper.define_base_url("ESELX") == "https://www.eselx.ipl.pt/eselx/orgaos-cientificos-pedagogicos/departamentos"
    assert scraper.define_base_url("ESML") == "https://www.esml.ipl.pt/home/pessoas/corpo-docente"
    assert scraper.define_base_url("ISEL") == "https://www.isel.pt/isel/quem-somos/departamentos"
    assert scraper.define_base_url("ESD") is None
    assert scraper.define_base_url("UNKNOWN") is None

def test_define_base_url_invalid():
    assert scraper.define_base_url("ESD") is None
    assert scraper.define_base_url("UNKNOWN") is None
    assert scraper.define_base_url("") is None
    assert scraper.define_base_url(None) is None

@pytest.mark.parametrize("escola, html, nome_esperado, link_esperado, expected_count", [
    (
        "ESELX",
        '<p><a href="/TEST/ESELX">TEST ESELX</a></p>',
        "TEST ESELX",
        "https://www.eselx.ipl.pt/TEST/ESELX",
        1
    ),
    (
        "ESML",
        '<p><a href="/TEST/ESML">TEST ESML</a></p>',
        "TEST ESML",
        "https://www.esml.ipl.pt/TEST/ESML",
        1
    ),
    (
        "ISEL",
        '<p><div class="be-desc"><a href="/TEST/ISEL">TEST ISEL</a></div></p>',
        "TEST ISEL",
        "https://www.isel.pt/TEST/ISEL",
        1
    ),
])

def test_departamento_parse(escola, html, nome_esperado, link_esperado, expected_count):
    soup = BeautifulSoup(html, "html.parser")
    items = soup.select("p")

    resultado = scraper.departamento_parse(items, escola)

    assert len(resultado) == expected_count
    if expected_count > 0:
        assert nome_esperado in resultado
        assert resultado[nome_esperado]["link"] == link_esperado
        assert resultado[nome_esperado]["escola"] == escola
        assert "dateChecked" in resultado[nome_esperado]

def test_departamento_parse_no_nome_element():
    html = '<p></p>'
    soup = BeautifulSoup(html, "html.parser")
    items = soup.select("p")
    escola = "ESELX"

    resultado = scraper.departamento_parse(items, escola)

    assert len(resultado) == 0

def test_departamento_parse_no_nome_in_element():
    html = '<p><a href="/TEST/ESELX"></a></p>'
    soup = BeautifulSoup(html, "html.parser")
    items = soup.select("p")
    escola = "ESELX"

    resultado = scraper.departamento_parse(items, escola)

    assert len(resultado) == 0

def test_departamento_parse_no_href_in_element():
    html = '<p><a>TEST ESELX</a></p>'
    soup = BeautifulSoup(html, "html.parser")
    items = soup.select("p")
    escola = "ESELX"

    resultado = scraper.departamento_parse(items, escola)

    assert len(resultado) == 0

@pytest.mark.parametrize("escola, html, expected_count", [
    #CASOS DE SUCESSO
    ("ESELX", '<div class="content-main"><p><div class="views-field-title"><a href="/TEST/ESELX">TEST ESELX</a></div></p></div>', 1),
    ("ESML", '<div class="category-desc"><h3><a href="/TEST/ESML">TEST ESML</a></h3></div>', 1),
    ("ISEL", '<div class="gsc-column col-lg-2"><div class="be-desc"><a href="/TEST/ISEL">TEST ISEL</a></div></div>', 1),
    #CASOS DE ERRO
    ("ESD", '<div class="content-main"><p><div class="views-field-title"><a href="/TEST/ESD">TEST ESD</a></div></p></div>', 0),
    ("UNKNOWN", '<div class="content-main"><p><div class="views-field-title"><a href="/TEST/UNKNOWN">TEST UNKNOWN</a></div></p></div>', 0),
])

def test_choose_departamento_parse_html(escola, html, expected_count):
    resultado = scraper.choose_departamento_parse_html(html, escola)
    assert len(resultado) == expected_count
    if expected_count > 0:
        assert "dateChecked" in resultado[f"TEST {escola}"]
        assert resultado[f"TEST {escola}"]["escola"] == escola
        if escola == "ISEL":
            assert resultado[f"TEST {escola}"]["link"] == f"https://www.isel.pt/TEST/{escola}"
        else:
            assert resultado[f"TEST {escola}"]["link"] == f"https://www.{escola.lower()}.ipl.pt/TEST/{escola}"

def test_scrape_sequential_sem_url_base(monkeypatch, capsys):
    monkeypatch.setattr(scraper, "define_base_url", lambda escola: None)
    all_deps = {}
    scraper.scrape_sequential("ESD",{}, all_deps)
    assert all_deps == {}

def test_scrape_sequential_fetch_falha(monkeypatch):
    monkeypatch.setattr(scraper, "define_base_url", lambda escola: "http://x.com")
    monkeypatch.setattr(scraper, "fetch", lambda url: None)
    all_deps = {}
    scraper.scrape_sequential("ISEL", {}, all_deps)
    assert all_deps == {}


def test_scrape_sequential_sem_departamentos(monkeypatch):
    monkeypatch.setattr(scraper, "define_base_url", lambda escola: "http://x.com")
    monkeypatch.setattr(scraper, "fetch", lambda url: "<html></html>")
    monkeypatch.setattr(scraper, "choose_departamento_parse_html", lambda html, escola: {})
    all_deps = {}
    scraper.scrape_sequential("ISEL", {}, all_deps)
    assert all_deps == {}


def test_scrape_sequential_primeiro_item_ja_existe(monkeypatch):
    monkeypatch.setattr(scraper, "define_base_url", lambda escola: "http://x.com")
    monkeypatch.setattr(scraper, "fetch", lambda url: "<html></html>")
    monkeypatch.setattr(scraper, "choose_departamento_parse_html", lambda html, escola: {
        "Dep A": {"link": "/a"},
        "Dep B": {"link": "/b"},
    })
    existing_data = {"Dep A": {}}   # primeiro item ("Dep A") já existe
    all_deps = {}
    scraper.scrape_sequential("ISEL", existing_data=existing_data, all_deps_shared=all_deps)

    assert all_deps == {}   # parou logo, "Dep B" não foi adicionado


def test_scrape_sequential_adiciona_itens_novos(monkeypatch):
    monkeypatch.setattr(scraper, "define_base_url", lambda escola: "http://x.com")
    monkeypatch.setattr(scraper, "fetch", lambda url: "<html></html>")
    monkeypatch.setattr(scraper, "choose_departamento_parse_html", lambda html, escola: {
        "Dep A": {"link": "/a"},
        "Dep B": {"link": "/b"},
    })
    all_deps = {}
    scraper.scrape_sequential("ISEL", existing_data={}, all_deps_shared=all_deps)
    assert len(all_deps) == 2
    assert "Dep A" in all_deps
    assert "Dep B" in all_deps


def test_scrape_sequential_so_adiciona_os_que_faltam(monkeypatch):
    monkeypatch.setattr(scraper, "define_base_url", lambda escola: "http://x.com")
    monkeypatch.setattr(scraper, "fetch", lambda url: "<html></html>")
    monkeypatch.setattr(scraper, "choose_departamento_parse_html", lambda html, escola: {
        "Dep A": {"link": "/a"},
        "Dep B": {"link": "/b"},
    })
    all_deps = {"Dep A": {"link": "/a-antigo"}}   # já presente, não deve ser sobrescrito
    scraper.scrape_sequential("ISEL", existing_data={}, all_deps_shared=all_deps)
    assert all_deps["Dep A"]["link"] == "/a-antigo"   # manteve-se, não foi sobrescrito
    assert "Dep B" in all_deps