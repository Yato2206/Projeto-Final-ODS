from unittest.mock import patch, MagicMock, AsyncMock
import asyncio
import pytest
from pathlib import Path
import json
import scraper_info_docentes as scraper
from urllib.error import HTTPError
from datetime import datetime
from bs4 import BeautifulSoup

def test_extract_name_comum_com_title():
    html = '<p><a href="https://example.com/orcid/123456" title="ORCID"></a></p>'
    soup = BeautifulSoup(html, "html.parser")
    selector = soup.find("a")
    result = scraper.extract_name(selector)
    assert result == "ORCID"

def test_extract_name_comum_sem_title_com_texto_colado_antes_do_link():
    html = '<p>ORCID:<a href="https://example.com/orcid/123456"></a></p>'
    soup = BeautifulSoup(html, "html.parser")
    selector = soup.find("a")
    result = scraper.extract_name(selector)
    assert result == "ORCID"

def test_extract_name_texto_diretamente_do_link():
    html = '<a href="https://example.com/orcid/123456">ORCID</a>'
    soup = BeautifulSoup(html, "html.parser")
    selector = soup.find("a")
    result = scraper.extract_name(selector)
    assert result == "ORCID"

def test_extract_name_ligação_mais_ID():
    html = '<p><a href="https://example.com/orcid/123456">ORCID ID</a></p>'
    soup = BeautifulSoup(html, "html.parser")
    selector = soup.find("a")
    result = scraper.extract_name(selector)
    assert result == "ORCID"

def test_parse_element():
    html = '<div><p><a href="https://example.com/orcid/123456" title="ORCID"></a></p></div>'
    soup = BeautifulSoup(html, "html.parser")
    element = soup.find("div")
    result = scraper.parse_element(element)
    assert len(result) == 1
    assert result[0][0] == "ORCID"
    assert result[0][1]["link"] == "https://example.com/orcid/123456"
    assert "dateChecked" in result[0][1]

def test_parse_element_more_than_one_element():
    html = '''
    <div>
        <p><a href="https://example.com/orcid/123456" title="ORCID"></a></p>
        <p><a href="https://example.com/cienciavitae/789012" title="Ciência Vitae"></a></p>
    </div>
    '''
    soup = BeautifulSoup(html, "html.parser")
    element = soup.find("div")
    result = scraper.parse_element(element)
    assert len(result) == 2
    assert result[0][0] == "ORCID"
    assert result[0][1]["link"] == "https://example.com/orcid/123456"
    assert "dateChecked" in result[0][1]
    assert result[1][0] == "Ciência Vitae"
    assert result[1][1]["link"] == "https://example.com/cienciavitae/789012"
    assert "dateChecked" in result[1][1]

def test_parse_element_no_href():
    html = '<div><p><a>No links here</a></p></div>'
    soup = BeautifulSoup(html, "html.parser")
    element = soup.find("div")
    result = scraper.parse_element(element)
    assert result == []

def test_parse_element_no_valid_href():
    html = '''
    <div>
        <p><a href="?not/valid"></a></p>
        <p><a href="mailto:test@example.com"></a></p>
    </div>
    '''
    soup = BeautifulSoup(html, "html.parser")
    element = soup.find("div")
    result = scraper.parse_element(element)
    assert result == []

def test_parse_element_no_links_found():
    html = '<div><p><a href="https://example.com/nonexistent"></a></p></div>'
    soup = BeautifulSoup(html, "html.parser")
    element = soup.find("div")
    result = scraper.parse_element(element)
    assert result == []

@pytest.mark.parametrize("html, escola, expected", [
    (
        "<div><p><a href='https://example.com/orcid/123456' title='ORCID'></a></p></div>",
        "ESCS",
        {}
    ),
    (
        """
        <div class="field field--name-field-investigacao">
            <div>
                <p><a href='https://example.com/orcid/123456' title='ORCID'></a></p>
                <p><a href='https://example.com/cienciavitae/789012' title='Ciência Vitae'></a></p>
            </div>
        </div>
        """,
        "ESD",
        {
            "ORCID": {
                "link": "https://example.com/orcid/123456",
                "dateChecked": datetime.now().isoformat(),
            },
            "Ciência Vitae": {
                "link": "https://example.com/cienciavitae/789012",
                "dateChecked": datetime.now().isoformat(),
            }
        }
    ),
    (
        """
        <div class="field field--name-field-investigacao">
            <div>
                <p><a href='https://example.com/orcid/123456' title='ORCID'></a></p>
                <p><a href='https://example.com/cienciavitae/789012' title='Ciência Vitae'></a></p>
            </div>
        </div>
        """,
        "ESELX",
        {
            "ORCID": {
                "link": "https://example.com/orcid/123456",
                "dateChecked": datetime.now().isoformat(),
            },
            "Ciência Vitae": {
                "link": "https://example.com/cienciavitae/789012",
                "dateChecked": datetime.now().isoformat(),
            }
        }
    ),
    (
        "<div><p><a href='https://example.com/orcid/123456' title='ORCID'></a></p></div>",
        "ESML",
        {}
    ),
    (
        "<div><p><a href='https://example.com/orcid/123456' title='ORCID'></a></p></div>",
        "ESTC",
        {}
    ),
    (
        """
        <div class="node__content">
            <div>
                <p><a href='https://example.com/orcid/123456' title='ORCID'></a></p>
                <p><a href='https://example.com/cienciavitae/789012' title='Ciência Vitae'></a></p>
            </div>
        </div>
        """,
        "ESSL",
        {
            "ORCID": {
                "link": "https://example.com/orcid/123456",
                "dateChecked": datetime.now().isoformat(),
            },
            "Ciência Vitae": {
                "link": "https://example.com/cienciavitae/789012",
                "dateChecked": datetime.now().isoformat(),
            }
        }
    ),
    (   
        """
        <div class="node__content">
            <div>
                <p><a href='https://example.com/orcid/123456' title='ORCID'></a></p>
                <p><a href='https://example.com/cienciavitae/789012' title='Ciência Vitae'></a></p>
            </div>
        </div>
        """,
        "ISCAL",
        {
            "ORCID": {
                "link": "https://example.com/orcid/123456",
                "dateChecked": datetime.now().isoformat(),
            },
            "Ciência Vitae": {
                "link": "https://example.com/cienciavitae/789012",
                "dateChecked": datetime.now().isoformat(),
            }
        }),
    (   
        """
        <div class="node__content">
            <div>
                <p><a href='https://example.com/orcid/123456' title='ORCID'></a></p>
                <p><a href='https://example.com/cienciavitae/789012' title='Ciência Vitae'></a></p>
            </div>
        </div>
        """,
        "ISEL",
        {
            "ORCID": {
                "link": "https://example.com/orcid/123456",
                "dateChecked": datetime.now().isoformat(),
            },
            "Ciência Vitae": {
                "link": "https://example.com/cienciavitae/789012",
                "dateChecked": datetime.now().isoformat(),
            }
        }
    ),
    (
        "inexistent",
        "inexistent",
        {}
    )
])

def test_parse_info(html, escola, expected):
    result = scraper.parse_info(html, escola)
    resultado_keys = list(result.keys())
    compare_keys = list(expected.keys())
    resultado_links = [sub_dict["link"] for sub_dict in result.values()]
    compare_links = [sub_dict["link"] for sub_dict in expected.values()]
    assert len(resultado_keys) == len(compare_keys)
    assert resultado_keys == compare_keys
    assert resultado_links == compare_links

@pytest.mark.asyncio
async def test_scrape_one_ja_scraped(monkeypatch):
    mock_fetch = AsyncMock()
    monkeypatch.setattr(scraper, "fetch_async", mock_fetch)

    entry = {"name": "Docente A", "escola": "ISEL", "link": "http://x.com/1"}
    resultado = await scraper.scrape_one(None, None, entry, {"Docente A"})

    assert resultado is None
    mock_fetch.assert_not_called()


@pytest.mark.asyncio
async def test_scrape_one_url_invalida_devolve_base_record(monkeypatch):
    entry = {"name": "Docente A", "escola": "ISEL", "link": "LINK NAO DISPONIVEL"}

    resultado = await scraper.scrape_one(None, None, entry, set())

    assert resultado is not None
    name, record = resultado
    assert name == "Docente A"
    assert record["escola"] == "ISEL"
    assert record["sourceUrl"] == "LINK NAO DISPONIVEL"
    assert "dateChecked" in record


@pytest.mark.asyncio
async def test_scrape_one_fetch_falha(monkeypatch):
    monkeypatch.setattr(scraper, "fetch_async", AsyncMock(return_value=None))

    entry = {"name": "Docente A", "escola": "ISEL", "link": "http://x.com/1"}
    resultado = await scraper.scrape_one(None, None, entry, set())

    assert resultado is None


@pytest.mark.asyncio
async def test_scrape_one_sucesso_com_parsed(monkeypatch):
    monkeypatch.setattr(scraper, "fetch_async", AsyncMock(return_value="<html></html>"))
    monkeypatch.setattr(scraper, "parse_info", lambda html, escola: {
        "ORCID": "http://orcid.org/123456",
        "Ciência Vitae": "http://cienciavitae.pt/789012",
    })

    entry = {"name": "Docente A", "escola": "ISEL", "link": "http://x.com/1"}
    resultado = await scraper.scrape_one(None, None, entry, set())

    assert resultado is not None
    name, record = resultado
    assert name == "Docente A"
    assert record["escola"] == "ISEL"
    assert record["sourceUrl"] == "http://x.com/1"
    assert record["ORCID"] == "http://orcid.org/123456"
    assert record["Ciência Vitae"] == "http://cienciavitae.pt/789012"
    assert "dateChecked" in record


@pytest.mark.asyncio
async def test_scrape_one_sem_parsed_devolve_base_record(monkeypatch):
    monkeypatch.setattr(scraper, "fetch_async", AsyncMock(return_value="<html></html>"))
    monkeypatch.setattr(scraper, "parse_info", lambda html, escola: {})

    entry = {"name": "Docente A", "escola": "ISEL", "link": "http://x.com/1"}
    resultado = await scraper.scrape_one(None, None, entry, set())

    assert resultado is not None
    name, record = resultado
    assert name == "Docente A"
    assert record["escola"] == "ISEL"
    assert record["sourceUrl"] == "http://x.com/1"
    assert "dateChecked" in record
    assert "ORCID" not in record


@pytest.mark.asyncio
async def test_scrape_one_base_record_nao_e_sobrescrito_por_parse(monkeypatch):
    """Confirma que campos do base_record (escola, sourceUrl) não são sobrescritos pelo parse."""
    monkeypatch.setattr(scraper, "fetch_async", AsyncMock(return_value="<html></html>"))
    monkeypatch.setattr(scraper, "parse_info", lambda html, escola: {
        "escola": "VALOR_ERRADO",      
        "sourceUrl": "http://errado",
    })

    entry = {"name": "Docente A", "escola": "ISEL", "link": "http://x.com/1"}
    resultado = await scraper.scrape_one(None, None, entry, existing_keys=set())

    name, record = resultado
    assert record["escola"] == "ISEL"
