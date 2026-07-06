from unittest.mock import patch, MagicMock, AsyncMock
import asyncio
import pytest
from pathlib import Path
import json
import scraper_cursos_texto as scraper
from urllib.error import HTTPError
from datetime import datetime

def test_parse_content_sucesso():
        html = """
        <html>
          <body>
            <div class="node__content clearfix">
              <div class="field--name-body">
                <p>Linha 1</p>
                <p>Linha 2</p>
              </div>
            </div>
          </body>
        </html>
        """
        result = scraper.parse_curso_content(
            html,
            "Licenciatura em Informática",
            "Licenciatura",
            "Escola Superior de Tecnologia",
            "https://exemplo.pt/curso/1",
        )
 
        assert result is not None
        assert result["curso"] == "Licenciatura em Informática"
        assert result["link"] == "https://exemplo.pt/curso/1"
        assert result["escola"] == "Escola Superior de Tecnologia"
        assert result["tipoCurso"] == "Licenciatura"
        assert "Linha 1" in result["texto"]
        assert "Linha 2" in result["texto"]
        datetime.fromisoformat(result["dateChecked"])
 
def test_parse_content_sem_node_content():
    html = "<html><body><div class='outra-classe'>Texto</div></body></html>"
    result = scraper.parse_curso_content(html, "curso", "tipo", "escola", "link")
    assert result is None

def test_parse_content_sem_field_body():
    html = """
    <html>
        <body>
        <div class="node__content clearfix">
            <div class="outra-coisa">Texto</div>
        </div>
        </body>
    </html>
    """
    result = scraper.parse_curso_content(html, "curso", "tipo", "escola", "link")
    assert result is None

def test_parse_content_campo_texto_vazio():
    html = """
    <html>
        <body>
            <div class="node__content clearfix">
                <div class="field--name-body"></div>
            </div>
        </body>
    </html>
    """
    resultado = scraper.parse_curso_content(html, "curso", "tipo", "escola", "link")

    assert resultado is not None   # field--name-body existe, não devolve None
    assert resultado["texto"] == ""

def test_parse_content_html_vazio():
    result = scraper.parse_curso_content("", "curso", "tipo", "escola", "link")
    assert result is None

def test_parse_content_preserva_quebras_linha():
    html = """
    <div class="node__content clearfix">
        <div class="field--name-body">
        <p>Primeiro parágrafo</p>
        <p>Segundo parágrafo</p>
        </div>
    </div>
    """
    result = scraper.parse_curso_content(html, "curso", "tipo", "escola", "link")
    assert "\n" in result["texto"]

@pytest.mark.asyncio
async def test_scrape_cursos_fetch_falha(monkeypatch):
    monkeypatch.setattr(scraper, "fetch_async", AsyncMock(return_value=None))

    link_info = {"link": "http://x.com/curso", "curso": "Engenharia", "tipoCurso": "Licenciatura", "escola": "1"}
    resultado = await scraper.scrape_cursos(None, link_info, {}, None)

    assert resultado is None


@pytest.mark.asyncio
async def test_scrape_cursos_parse_devolve_none(monkeypatch):
    monkeypatch.setattr(scraper, "fetch_async", AsyncMock(return_value="<html></html>"))
    monkeypatch.setattr(scraper, "parse_curso_content", lambda html, curso, tipoCurso, escola, url: None)

    link_info = {"link": "http://x.com/curso", "curso": "Engenharia", "tipoCurso": "Licenciatura", "escola": "1"}
    resultado = await scraper.scrape_cursos(None, link_info, {}, None)

    assert resultado is None


@pytest.mark.asyncio
async def test_scrape_cursos_sucesso(monkeypatch):
    monkeypatch.setattr(scraper, "fetch_async", AsyncMock(return_value="<html></html>"))
    monkeypatch.setattr(scraper, "parse_curso_content", lambda html, curso, tipoCurso, escola, url: {
        "link": "http://x.com/curso",
        "curso": "Engenharia",
        "tipoCurso": "Licenciatura",
    })

    link_info = {"link": "http://x.com/curso", "curso": "Engenharia", "tipoCurso": "Licenciatura", "escola": "1"}
    resultado = await scraper.scrape_cursos(None, link_info, {}, None)

    assert resultado is not None
    curso, content = resultado
    assert curso == "http://x.com/curso"
    assert content["curso"] == "Engenharia"


@pytest.mark.asyncio
async def test_scrape_cursos_ja_existe_em_existing_data(monkeypatch):
    monkeypatch.setattr(scraper, "fetch_async", AsyncMock(return_value="<html></html>"))
    monkeypatch.setattr(scraper, "parse_curso_content", lambda html, curso, tipoCurso, escola, url: {
        "link": "http://x.com/curso",
        "curso": "Engenharia",
    })

    link_info = {"link": "http://x.com/curso", "curso": "Engenharia", "tipoCurso": "Licenciatura", "escola": "1"}
    existing_data = {"http://x.com/curso": {}} 

    resultado = await scraper.scrape_cursos(None, link_info, existing_data, None)

    assert resultado is None


@pytest.mark.asyncio
async def test_scrape_cursos_campos_em_falta_em_link_info(monkeypatch):
    monkeypatch.setattr(scraper, "fetch_async", AsyncMock(return_value="<html></html>"))

    chamadas = {}
    def fake_parse(html, curso, tipoCurso, escola, url):
        chamadas["curso"] = curso
        chamadas["tipoCurso"] = tipoCurso
        chamadas["escola"] = escola
        return None

    monkeypatch.setattr(scraper, "parse_curso_content", fake_parse)

    link_info = {"link": "http://x.com/curso"} 
    await scraper.scrape_cursos(None, link_info, {}, None)

    assert chamadas["curso"] == ""
    assert chamadas["tipoCurso"] == ""
    assert chamadas["escola"] == ""


@pytest.mark.asyncio
async def test_scrape_cursos_usa_link_do_content_como_chave(monkeypatch):
    """
    Confirma que a chave devolvida é content["link"], não link_info["link"]
    — podem ser diferentes se parse_content normalizar o URL.
    """
    monkeypatch.setattr(scraper, "fetch_async", AsyncMock(return_value="<html></html>"))
    monkeypatch.setattr(scraper, "parse_curso_content", lambda html, curso, tipoCurso, escola, url: {
        "link": "http://x.com/curso-normalizado", 
        "curso": "Engenharia",
    })

    link_info = {"link": "http://x.com/curso-original", "curso": "Engenharia", "tipoCurso": "", "escola": "1"}
    resultado = await scraper.scrape_cursos(None, link_info, {}, None)

    assert resultado is not None
    chave, _ = resultado
    assert chave == "http://x.com/curso-normalizado"