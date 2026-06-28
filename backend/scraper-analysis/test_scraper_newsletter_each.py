from unittest.mock import patch, MagicMock, AsyncMock
import asyncio
import pytest
from pathlib import Path
import json
import scraper_newsletter_each as scraper
from urllib.error import HTTPError
from datetime import datetime

@pytest.mark.asyncio
async def test_fetch_sucesso():
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.text.return_value = "<html>conteudo</html>"
    mock_session = MagicMock()
    mock_session.get.return_value.__aenter__.return_value = mock_response
    resultado = await scraper.fetch(mock_session, "http://exemplo.com")
    assert resultado == "<html>conteudo</html>"

@pytest.mark.asyncio
async def test_fetch_status_diferente_de_200_tenta_novamente_e_falha(monkeypatch):
    monkeypatch.setattr(scraper.asyncio, "sleep", AsyncMock()) 

    mock_response = AsyncMock()
    mock_response.status = 404

    mock_session = MagicMock()
    mock_session.get.return_value.__aenter__.return_value = mock_response

    resultado = await scraper.fetch(mock_session, "http://exemplo.com")

    assert resultado is None
    assert mock_session.get.call_count == scraper.RETRIES  # tentou RETRIES vezes


@pytest.mark.asyncio
async def test_fetch_excecao_de_rede_com_retry_ate_sucesso(monkeypatch):
    monkeypatch.setattr(scraper.asyncio, "sleep", AsyncMock())

    mock_response_ok = AsyncMock()
    mock_response_ok.status = 200
    mock_response_ok.text.return_value = "ok"

    mock_session = MagicMock()
    # primeira chamada lança excepção, segunda funciona
    mock_session.get.side_effect = [
        Exception("falha de rede"),
        MagicMock(__aenter__=AsyncMock(return_value=mock_response_ok), __aexit__=AsyncMock(return_value=None)),
    ]

    resultado = await scraper.fetch(mock_session, "http://exemplo.com")

    assert resultado == "ok"
    assert mock_session.get.call_count == 2


@pytest.mark.asyncio
async def test_fetch_falha_todas_as_tentativas(monkeypatch):
    monkeypatch.setattr(scraper.asyncio, "sleep", AsyncMock())

    mock_session = MagicMock()
    mock_session.get.side_effect = Exception("timeout")

    resultado = await scraper.fetch(mock_session, "http://exemplo.com")

    assert resultado is None
    assert mock_session.get.call_count == scraper.RETRIES

def test_extract_newsletter_id():
    url = "https://www.ipl.pt/newsletter/123"
    newsletter_id = scraper.extract_newsletter_id(url)
    assert newsletter_id == "123"

def test_extract_newsletter_id_url_sem_id():
    url = "https://www.ipl.pt/newsletter/"
    newsletter_id = scraper.extract_newsletter_id(url)
    assert newsletter_id == "unknown"
    url2 = "https://www.ipl.pt/newsletter"
    newsletter_id2 = scraper.extract_newsletter_id(url2)
    assert newsletter_id2 == "unknown"

def test_parse_newsletter_content_normaliza_espacos_e_pontuacao():
    html = """
    <div class="content-main">
        <div class="title-body">
            <h1>Título   com\xa0espaços   estranhos</h1>
            <p>Texto com   espaço extra , e pontuação   .</p>
        </div>
    </div>
    """
    resultado = scraper.parse_newsletter_content(html, "1", "2026-06-20", "/noticia/1")

    assert resultado["politecnicoTitulo"] == "Título com espaços estranhos"
    assert resultado["politecnicoTexto"] == "Texto com espaço extra, e pontuação."

def test_parse_newsletter_content_normaliza_parenteses():
    html = """
    <div class="content-main">
        <div class="title-body">
            <h1>Título</h1>
            <p>Texto ( com espaço a mais )</p>
        </div>
    </div>
    """
    resultado = scraper.parse_newsletter_content(html, "1", "2026-06-20", "/x")
    assert resultado["politecnicoTexto"] == "Texto (com espaço a mais)"

def test_parse_newsletter_content_sem_content_main():
    html = "<html><body>Sem content-main</body></html>"
    resultado = scraper.parse_newsletter_content(html, "1", "2026-06-20", "/x")
    assert resultado is None

def test_parse_newsletter_content_sem_title_body():
    html = '<div class="content-main"><p>conteudo solto</p></div>'
    resultado = scraper.parse_newsletter_content(html, "1", "2026-06-20", "/x")
    assert resultado is not None
    assert resultado["politecnicoTitulo"] == ""
    assert resultado["politecnicoTexto"] == ""

def test_parse_newsletter_content_sem_h1():
    html = """
    <div class="content-main">
        <div class="title-body">
            <p>Só texto, sem h1</p>
        </div>
    </div>
    """
    resultado = scraper.parse_newsletter_content(html, "1", "2026-06-20", "/x")
    assert resultado["politecnicoTitulo"] == ""
    assert resultado["politecnicoTexto"] == "Só texto, sem h1"

def test_parse_newsletter_content_multiplos_paragrafos_intro():
    html = """
    <div class="content-main">
        <div class="title-body">
            <h1>Título</h1>
            <p>Parágrafo um.</p>
            <p>Parágrafo dois.</p>
            <p></p>
        </div>
    </div>
    """
    resultado = scraper.parse_newsletter_content(html, "1", "2026-06-20", "/x")
    assert resultado["politecnicoTexto"] == "Parágrafo um. Parágrafo dois."

def test_parse_newsletter_content_campo_aberto_multiplas_noticias():
    html = """
    <div class="content-main">
        <div class="title-body"><h1>T</h1></div>
        <div class="field--name-field-campo-aberto-grupo-3">
            <h2>Notícia 1</h2>
            <p>Texto da notícia 1.</p>
            <p>Continuação da notícia 1.</p>
            <h2>Notícia 2</h2>
            <p>Texto da notícia 2.</p>
        </div>
    </div>
    """
    resultado = scraper.parse_newsletter_content(html, "1", "2026-06-20", "/x")

    assert len(resultado["noticias"]) == 2
    assert resultado["noticias"][0]["titulo"] == "Notícia 1"
    assert resultado["noticias"][0]["texto"] == "Texto da notícia 1. Continuação da notícia 1."
    assert resultado["noticias"][1]["titulo"] == "Notícia 2"
    assert resultado["noticias"][1]["texto"] == "Texto da notícia 2."


def test_parse_newsletter_content_campo_aberto_h2_sem_paragrafos():
    html = """
    <div class="content-main">
        <div class="title-body"><h1>T</h1></div>
        <div class="field--name-field-campo-aberto-grupo-3">
            <h2>Notícia Vazia</h2>
            <h2>Notícia 2</h2>
            <p>Texto.</p>
        </div>
    </div>
    """
    resultado = scraper.parse_newsletter_content(html, "1", "2026-06-20", "/x")

    assert resultado["noticias"][0]["titulo"] == "Notícia Vazia"
    assert resultado["noticias"][0]["texto"] == ""

def test_parse_newsletter_content_campo_aberto_ausente():
    html = """
    <div class="content-main">
        <div class="title-body"><h1>T</h1></div>
    </div>
    """
    resultado = scraper.parse_newsletter_content(html, "1", "2026-06-20", "/x")
    assert resultado["noticias"] == []

def test_parse_newsletter_content_campo_aberto_para_em_elemento_nao_h2_nem_p():
    """Confirma que find_next_siblings ignora ou pára correctamente noutro tipo de tag."""
    html = """
    <div class="content-main">
        <div class="title-body"><h1>T</h1></div>
        <div class="field--name-field-campo-aberto-grupo-3">
            <h2>Notícia 1</h2>
            <p>Texto válido.</p>
            <div>Bloco estranho, não é p nem h2</div>
            <p>Este ainda deve contar.</p>
            <h2>Notícia 2</h2>
        </div>
    </div>
    """
    resultado = scraper.parse_newsletter_content(html, "1", "2026-06-20", "/x")
    assert resultado["noticias"][0]["texto"] == "Texto válido. Este ainda deve contar."

def test_parse_newsletter_content_campos_basicos_no_resultado():
    html = '<div class="content-main"><div class="title-body"><h1>T</h1></div></div>'
    resultado = scraper.parse_newsletter_content(html, "42", "2026-01-01", "/link/42")

    assert resultado["titulo"] == "Newsletter: 42"
    assert resultado["link"] == "/link/42"
    assert resultado["dataPublicacao"] == "2026-01-01"
    assert resultado["tipo"] == "Newsletter"
    assert "dateChecked" in resultado

def test_parse_newsletter_content_date_checked_e_iso_valido():
    html = '<div class="content-main"><div class="title-body"><h1>T</h1></div></div>'
    resultado = scraper.parse_newsletter_content(html, "1", "2026-06-20", "/x")
    datetime.fromisoformat(resultado["dateChecked"])

def test_parse_newsletter_content():
    html = Path("test_data/newsletter_sample.html").read_text(encoding="utf-8")
    newsletter_id = "123"
    data_publicacao = "2026-06-20"
    link = "https://www.ipl.pt/newsletter/123"

    resultado = scraper.parse_newsletter_content(html, newsletter_id, data_publicacao, link)

    assert resultado is not None
    assert resultado["titulo"] == f"Newsletter: {newsletter_id}"
    assert resultado["dataPublicacao"] == data_publicacao
    assert resultado["link"] == link
    assert resultado["tipo"] == "Newsletter"
    assert "politecnicoTitulo" in resultado
    assert "politecnicoTexto" in resultado
    assert "dateChecked" in resultado
    assert isinstance(resultado["noticias"], list)
    assert len(resultado["noticias"]) > 0

@pytest.mark.asyncio
async def test_scrape_newsletter(monkeypatch):
    monkeypatch.setattr(scraper, "fetch", AsyncMock(return_value="<html>...</html>"))
    monkeypatch.setattr(scraper, "extract_newsletter_id", lambda url: "123")
    monkeypatch.setattr(scraper, "parse_newsletter_content", lambda html, id, data, url: {
        "titulo": "Notícia Nova", "link": url
    })

    link_info = {"link": "/noticia/123", "dataPublicacao": "2026-06-20"}
    resultado = await scraper.scrape_newsletter(session=None, link_info=link_info, existing_data={})

    assert resultado is not None
    titulo, content = resultado
    assert titulo == "Notícia Nova"

@pytest.mark.asyncio
async def test_scrape_newsletter_item_ja_existente_devolve_none(monkeypatch):
    monkeypatch.setattr(scraper, "fetch", AsyncMock(return_value="<html>...</html>"))
    monkeypatch.setattr(scraper, "extract_newsletter_id", lambda url: "123")
    monkeypatch.setattr(scraper, "parse_newsletter_content", lambda html, id, data, url: {
        "titulo": "Já Existe", "link": url
    })

    link_info = {"link": "/noticia/123"}
    existing_data = {"Já Existe": {}}

    resultado = await scraper.scrape_newsletter(session=None, link_info=link_info, existing_data=existing_data)
    assert resultado is None

@pytest.mark.asyncio
async def test_scrape_newsletter_fetch_falha_devolve_none(monkeypatch):
    monkeypatch.setattr(scraper, "fetch", AsyncMock(return_value=None))

    link_info = {"link": "/noticia/x"}
    resultado = await scraper.scrape_newsletter(session=None, link_info=link_info, existing_data={})
    assert resultado is None

@pytest.mark.asyncio
async def test_scrape_newsletter_parse_content_devolve_none(monkeypatch):
    monkeypatch.setattr(scraper, "fetch", AsyncMock(return_value="<html></html>"))
    monkeypatch.setattr(scraper, "extract_newsletter_id", lambda url: "123")
    monkeypatch.setattr(scraper, "parse_newsletter_content", lambda html, id, data, url: None)

    link_info = {"link": "/noticia/x"}
    resultado = await scraper.scrape_newsletter(session=None, link_info=link_info, existing_data={})
    assert resultado is None

@pytest.mark.asyncio
async def test_scrape_chunk_adiciona_todos_os_resultados(monkeypatch):
    async def fake_scrape(session, link_info, existing_data):
        return (link_info["link"], {"titulo": link_info["link"]})

    monkeypatch.setattr(scraper, "scrape_newsletter", fake_scrape)

    chunk = [{"link": "/a"}, {"link": "/b"}, {"link": "/c"}]
    all_data_shared = {}

    await scraper._scrape_chunk(session=None, chunk=chunk, existing_data={}, all_data_shared=all_data_shared)

    assert len(all_data_shared) == 3
    assert "/a" in all_data_shared


@pytest.mark.asyncio
async def test_scrape_chunk_erro_num_item_nao_bloqueia_os_outros(monkeypatch):
    async def fake_scrape(session, link_info, existing_data):
        if link_info["link"] == "/falha":
            raise Exception("erro simulado")
        return (link_info["link"], {"titulo": link_info["link"]})

    monkeypatch.setattr(scraper, "scrape_newsletter", fake_scrape)

    chunk = [{"link": "/a"}, {"link": "/falha"}, {"link": "/c"}]
    all_data_shared = {}

    await scraper._scrape_chunk(session=None, chunk=chunk, existing_data={}, all_data_shared=all_data_shared)

    assert len(all_data_shared) == 2          # "/falha" não entrou, os outros sim
    assert "/falha" not in all_data_shared
    assert "/a" in all_data_shared
    assert "/c" in all_data_shared


@pytest.mark.asyncio
async def test_scrape_chunk_resultado_none_nao_adiciona_nada(monkeypatch):
    async def fake_scrape(session, link_info, existing_data):
        return None  # já existia, ou falhou o parse

    monkeypatch.setattr(scraper, "scrape_newsletter", fake_scrape)

    chunk = [{"link": "/a"}, {"link": "/b"}]
    all_data_shared = {}

    await scraper._scrape_chunk(session=None, chunk=chunk, existing_data={}, all_data_shared=all_data_shared)

    assert all_data_shared == {}

@pytest.mark.asyncio
async def test_scrape_parallel_divide_em_chunks_corretamente(monkeypatch):
    chunks_recebidos = []

    async def fake_scrape_chunk(session, chunk, existing_data, all_data_shared, prefix=""):
        chunks_recebidos.append(chunk)
        for item in chunk:
            all_data_shared[item["link"]] = {"titulo": item["link"]}

    monkeypatch.setattr(scraper, "_scrape_chunk", fake_scrape_chunk)
    monkeypatch.setattr(scraper, "load_existing_data", lambda: {})
    monkeypatch.setattr(scraper, "save_data", lambda data: None)
    monkeypatch.setattr(scraper, "aiohttp", type("FakeAiohttp", (), {
        "ClientSession": lambda *a, **k: _FakeSession()
    }))

    links = [{"link": f"/{i}"} for i in range(10)]

    await scraper.scrape_newsletters_parallel(links, num_scrapers=3, force_full=False)

    total_distribuido = sum(len(c) for c in chunks_recebidos)
    assert total_distribuido == 10
    assert len(chunks_recebidos) == 3   # ou 4, dependendo do arredondamento — confirma o teu chunk_size


class _FakeSession:
    async def __aenter__(self):
        return self
    async def __aexit__(self, *a):
        return None

@pytest.mark.asyncio
async def test_scrape_parallel_force_full_ignora_dados_antigos(monkeypatch, tmp_path):
    ficheiro = tmp_path / "data.json"
    ficheiro.write_text('{"Antigo": {}}', encoding="utf-8")

    monkeypatch.setattr(scraper, "OUTPUT_FILE", str(ficheiro))
    monkeypatch.setattr(scraper, "load_existing_data", lambda: {"Antigo": {}})
    monkeypatch.setattr(scraper, "_scrape_chunk", AsyncMock())
    monkeypatch.setattr(scraper, "save_data", lambda data: None)

    dados_guardados = {}
    def fake_save(data):
        dados_guardados.update(data)
    monkeypatch.setattr(scraper, "save_data", fake_save)

    class _FakeSession:
        async def __aenter__(self): return self
        async def __aexit__(self, *a): return None
    monkeypatch.setattr(scraper.aiohttp, "ClientSession", lambda *a, **k: _FakeSession())

    await scraper.scrape_newsletters_parallel(links=[], force_full=True)

    assert not ficheiro.exists()  # foi apagado por force_full antes de gravar de novo