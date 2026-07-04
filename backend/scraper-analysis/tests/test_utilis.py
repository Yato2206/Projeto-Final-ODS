from unittest.mock import patch, MagicMock, AsyncMock
import asyncio
import aiohttp
import pytest
from pathlib import Path
import json
import utilis as utilis
from urllib.error import HTTPError
from datetime import datetime
from bs4 import BeautifulSoup

def test_load_existing_data_ficheiro(tmp_path):
    ficheiro = tmp_path / "data.json"
    dados = {"TESTE": {"testing": "data"}}
    ficheiro.write_text(json.dumps(dados), encoding="utf-8")

    resultado = utilis.load_existing_data(str(ficheiro))
    assert len(resultado) == 1
    assert "TESTE" in resultado
    assert resultado["TESTE"]["testing"] == "data"

def test_load_existing_data_ficheiro_nao_existe(tmp_path):
    ficheiro = tmp_path / "data.json" 
    resultado = utilis.load_existing_data(str(ficheiro))
    assert resultado == {}

def test_load_existing_data_ficheiro_vazio(tmp_path):
    ficheiro = tmp_path / "data.json"
    ficheiro.write_text("{}", encoding="utf-8")

    resultado = utilis.load_existing_data(str(ficheiro))
    assert resultado == {}

def test_load_existing_data_preserva_estrutura_completa(tmp_path):
    ficheiro = tmp_path / "data.json"
    dados = {"chave": {"campo1": "valor1", "campo2": 42, "lista": [1, 2, 3]}}
    ficheiro.write_text(json.dumps(dados, ensure_ascii=False), encoding="utf-8")

    resultado = utilis.load_existing_data(str(ficheiro))
    assert resultado["chave"]["campo1"] == "valor1"
    assert resultado["chave"]["campo2"] == 42
    assert resultado["chave"]["lista"] == [1, 2, 3]

def test_load_existing_data_com_caracteres_especiais(tmp_path):
    ficheiro = tmp_path / "data.json"
    dados = {"João Çavá": {"escola": "1", "título": "Investigação"}}
    ficheiro.write_text(json.dumps(dados, ensure_ascii=False), encoding="utf-8")

    resultado = utilis.load_existing_data(str(ficheiro))
    assert "João Çavá" in resultado
    assert resultado["João Çavá"]["título"] == "Investigação"

def test_save_data(tmp_path):
    ficheiro = tmp_path / "data.json"
    dados = {"Teste": {"testing": "data"}}

    utilis.save_data(dados, "testing", str(ficheiro))
    assert ficheiro.exists()
    conteudo = json.loads(ficheiro.read_text(encoding="utf-8"))
    assert "Teste" in conteudo
    assert conteudo["Teste"]["testing"] == "data"

def test_save_data_ordena_por_sort_key_decrescente(tmp_path):
    ficheiro = tmp_path / "data.json"
    dados = {
        "Test1": {"dataPublicacao": "2024-01-01"},
        "Test2": {"dataPublicacao": "2026-01-01"},
        "Test3": {"dataPublicacao": "2025-01-01"},
    }

    utilis.save_data(dados, "dataPublicacao", str(ficheiro))
    conteudo = json.loads(ficheiro.read_text(encoding="utf-8"))
    chaves = list(conteudo.keys())
    assert chaves == ["Test2", "Test3", "Test1"]

def test_save_data_sort_key_ausente_fica_no_final(tmp_path):
    ficheiro = tmp_path / "data.json"
    dados = {
        "Test1": {"dataPublicacao": "2026-01-01"},
        "Test2": {},   # sem dataPublicacao
    }

    utilis.save_data(dados, "dataPublicacao", str(ficheiro))

    conteudo = json.loads(ficheiro.read_text(encoding="utf-8"))
    chaves = list(conteudo.keys())
    assert chaves[0] == "Test1"
    assert chaves[-1] == "Test2" #nao existe dataPublicacao, deve ficar no final

def test_save_data_sobrescreve_ficheiro_existente(tmp_path):
    ficheiro = tmp_path / "data.json"
    ficheiro.write_text(json.dumps({"Antigo": {}}), encoding="utf-8")

    dados_novos = {"Novo": {"dataPublicacao": "2026-01-01"}}
    utilis.save_data(dados_novos, "dataPublicacao", str(ficheiro))

    conteudo = json.loads(ficheiro.read_text(encoding="utf-8"))
    assert "Antigo" not in conteudo
    assert "Novo" in conteudo

def test_save_data_vazio(tmp_path):
    ficheiro = tmp_path / "data.json"

    utilis.save_data({}, "dataPublicacao", str(ficheiro))
    conteudo = json.loads(ficheiro.read_text(encoding="utf-8"))
    assert conteudo == {}

def test_save_data_caracteres_especiais(tmp_path):
    ficheiro = tmp_path / "data.json"
    dados = {"João Çavá": {"título": "Investigação", "dataPublicacao": "2026-01-01"}}

    utilis.save_data(dados, "dataPublicacao", str(ficheiro))

    conteudo = json.loads(ficheiro.read_text(encoding="utf-8"))
    assert "João Çavá" in conteudo
    assert conteudo["João Çavá"]["título"] == "Investigação"

def test_load_links_ficheiro_nao_existe(tmp_path):
    ficheiro = tmp_path / "nao_existe.json"

    resultado = utilis.load_links(str(ficheiro))
    assert resultado == []

def test_load_links_versao_newsletter(tmp_path):
    ficheiro = tmp_path / "data.json"
    dados = {
        "Título A": {"link": "http://x.com/a", "dataPublicacao": "2026-01-01"},
        "Título B": {"link": "http://x.com/b", "dataPublicacao": "2025-06-15"},
    }
    ficheiro.write_text(json.dumps(dados), encoding="utf-8")

    resultado = utilis.load_links(str(ficheiro), True)

    assert len(resultado) == 2
    assert resultado[0]["titulo"] == "Título A"
    assert resultado[0]["link"] == "http://x.com/a"
    assert resultado[0]["dataPublicacao"] == "2026-01-01"

def test_load_existing_data_ficheiro_nao_existe(tmp_path):
    ficheiro = tmp_path / "data.json"   

    resultado = utilis.load_existing_data(str(ficheiro))
    assert resultado == {}

def test_load_existing_data_ficheiro_vazio(tmp_path):
    ficheiro = tmp_path / "data.json"
    ficheiro.write_text("{}", encoding="utf-8")

    resultado = utilis.load_existing_data(str(ficheiro))
    assert resultado == {}

def test_load_existing_data_com_conteudo(tmp_path):
    ficheiro = tmp_path / "data.json"
    dados = {
        "Docente A": {"escola": "1", "link": "http://x.com/a"},
        "Docente B": {"escola": "2", "link": "http://x.com/b"},
    }
    ficheiro.write_text(json.dumps(dados), encoding="utf-8")

    resultado = utilis.load_existing_data(str(ficheiro))
    assert len(resultado) == 2
    assert "Docente A" in resultado
    assert resultado["Docente A"]["escola"] == "1"

def test_load_existing_data_preserva_estrutura_completa(tmp_path):
    ficheiro = tmp_path / "data.json"
    dados = {"chave": {"campo1": "valor1", "campo2": 42, "lista": [1, 2, 3]}}
    ficheiro.write_text(json.dumps(dados, ensure_ascii=False), encoding="utf-8")

    resultado = utilis.load_existing_data(str(ficheiro))
    assert resultado["chave"]["campo1"] == "valor1"
    assert resultado["chave"]["campo2"] == 42
    assert resultado["chave"]["lista"] == [1, 2, 3]

def test_load_existing_data_com_caracteres_especiais(tmp_path):
    ficheiro = tmp_path / "data.json"
    dados = {"João Ção": {"escola": "1", "título": "Investigação"}}
    ficheiro.write_text(json.dumps(dados, ensure_ascii=False), encoding="utf-8")

    resultado = utilis.load_existing_data(str(ficheiro))
    assert "João Ção" in resultado
    assert resultado["João Ção"]["título"] == "Investigação"

def test_save_data_cria_ficheiro(tmp_path):
    ficheiro = tmp_path / "data.json"
    dados = {"Docente A": {"dataPublicacao": "2026-01-01"}}
    utilis.save_data(dados, "dataPublicacao", str(ficheiro))
    assert ficheiro.exists()

def test_save_data_conteudo_correto(tmp_path):
    ficheiro = tmp_path / "data.json"
    dados = {"Docente A": {"dataPublicacao": "2026-01-01"}}
    utilis.save_data(dados, "dataPublicacao", str(ficheiro))
    conteudo = json.loads(ficheiro.read_text(encoding="utf-8"))
    assert "Docente A" in conteudo
    assert conteudo["Docente A"]["dataPublicacao"] == "2026-01-01"

def test_save_data_ordena_por_sort_key_decrescente(tmp_path):
    ficheiro = tmp_path / "data.json"
    dados = {
        "Docente A": {"dataPublicacao": "2024-01-01"},
        "Docente B": {"dataPublicacao": "2026-01-01"},
        "Docente C": {"dataPublicacao": "2025-01-01"},
    }
    utilis.save_data(dados, "dataPublicacao", str(ficheiro))
    conteudo = json.loads(ficheiro.read_text(encoding="utf-8"))
    chaves = list(conteudo.keys())
    assert chaves == ["Docente B", "Docente C", "Docente A"]  

def test_save_data_sort_key_ausente_fica_no_final(tmp_path):
    """Items sem o sort_key devem ficar no fim (get devolve "")."""
    ficheiro = tmp_path / "data.json"
    dados = {
        "Docente A": {"dataPublicacao": "2026-01-01"},
        "Docente B": {}, 
    }
    utilis.save_data(dados, "dataPublicacao", str(ficheiro))
    conteudo = json.loads(ficheiro.read_text(encoding="utf-8"))
    chaves = list(conteudo.keys())
    assert chaves[0] == "Docente A"
    assert chaves[-1] == "Docente B"

def test_save_data_sobrescreve_ficheiro_existente(tmp_path):
    ficheiro = tmp_path / "data.json"
    ficheiro.write_text(json.dumps({"Antigo": {}}), encoding="utf-8")

    dados_novos = {"Novo": {"dataPublicacao": "2026-01-01"}}
    utilis.save_data(dados_novos, "dataPublicacao", str(ficheiro))
    conteudo = json.loads(ficheiro.read_text(encoding="utf-8"))
    assert "Antigo" not in conteudo
    assert "Novo" in conteudo

def test_save_data_vazio(tmp_path):
    ficheiro = tmp_path / "data.json"
    utilis.save_data({}, "dataPublicacao", str(ficheiro))
    conteudo = json.loads(ficheiro.read_text(encoding="utf-8"))
    assert conteudo == {}

def test_save_data_caracteres_especiais(tmp_path):
    ficheiro = tmp_path / "data.json"
    dados = {"João Ção": {"título": "Investigação", "dataPublicacao": "2026-01-01"}}
    utilis.save_data(dados, "dataPublicacao", str(ficheiro))
    conteudo = json.loads(ficheiro.read_text(encoding="utf-8"))
    assert "João Ção" in conteudo
    assert conteudo["João Ção"]["título"] == "Investigação"

def test_load_links_ficheiro_nao_existe(tmp_path):
    ficheiro = tmp_path / "nao_existe.json"
    resultado = utilis.load_links(str(ficheiro))
    assert resultado == []

def test_load_links_versao_newsletter(tmp_path):
    ficheiro = tmp_path / "data.json"
    dados = {
        "Título A": {"link": "http://x.com/a", "dataPublicacao": "2026-01-01"},
        "Título B": {"link": "http://x.com/b", "dataPublicacao": "2025-06-15"},
    }
    ficheiro.write_text(json.dumps(dados), encoding="utf-8")

    resultado = utilis.load_links(str(ficheiro), True)
    assert len(resultado) == 2
    assert resultado[0]["titulo"] == "Título A"
    assert resultado[0]["link"] == "http://x.com/a"
    assert resultado[0]["dataPublicacao"] == "2026-01-01"

def test_load_links_versao_newsletter_default(tmp_path):
    ficheiro = tmp_path / "data.json"
    dados = {"Título A": {"link": "http://x.com/a", "dataPublicacao": "2026-01-01"}}
    ficheiro.write_text(json.dumps(dados), encoding="utf-8")

    resultado = utilis.load_links(str(ficheiro))
    assert "titulo" in resultado[0]
    assert "link" in resultado[0]
    assert "dataPublicacao" in resultado[0]

def test_load_links_versao_cursos(tmp_path):
    ficheiro = tmp_path / "data.json"
    dados = {
        "http://x.com/a": {"curso": "Título A", "tipoCurso": "Licenciatura", "escola": "ISEL"},
        "http://x.com/b": {"curso": "Título B", "tipoCurso": "Mestrado", "escola": "IPL"},
    }
    ficheiro.write_text(json.dumps(dados), encoding="utf-8")

    resultado = utilis.load_links(str(ficheiro), False)
    assert len(resultado) == 2
    assert resultado[0]["link"] == "http://x.com/a"
    assert resultado[0]["curso"] == "Título A"
    assert resultado[0]["tipoCurso"] == "Licenciatura"
    assert resultado[0]["escola"] == "ISEL"
    assert resultado[1]["link"] == "http://x.com/b"
    assert resultado[1]["curso"] == "Título B"
    assert resultado[1]["tipoCurso"] == "Mestrado"
    assert resultado[1]["escola"] == "IPL" 

def test_load_links_newsletter_campos_ausentes_ficam_none(tmp_path):
    ficheiro = tmp_path / "data.json"
    dados = {"Título A": {}} 
    ficheiro.write_text(json.dumps(dados), encoding="utf-8")

    resultado = utilis.load_links(str(ficheiro))
    assert resultado[0]["link"] is None
    assert resultado[0]["dataPublicacao"] is None

def test_load_links_ficheiro_vazio(tmp_path):
    ficheiro = tmp_path / "data.json"
    ficheiro.write_text("{}", encoding="utf-8")
    resultado = utilis.load_links(str(ficheiro))
    assert resultado == []

def test_load_links_curso_campos_ausentes_ficam_none(tmp_path):
    ficheiro = tmp_path / "data.json"
    dados = {"http://x.com/a": {}} 
    ficheiro.write_text(json.dumps(dados), encoding="utf-8")

    resultado = utilis.load_links(str(ficheiro), False)
    assert resultado[0]["curso"] is None
    assert resultado[0]["tipoCurso"] is None
    assert resultado[0]["escola"] is None

@pytest.mark.parametrize("newsletter", [True, False])
def test_load_links_estrutura_chaves_por_modo(tmp_path, newsletter):
    """Confirma que as chaves do dict devolvido são as correctas para cada modo."""
    ficheiro = tmp_path / "data.json"
    if newsletter:
        dados = {"Título": {"link": "http://x.com", "dataPublicacao": "2026"}}
        chaves_esperadas = {"titulo", "link", "dataPublicacao"}
    else:
        dados = {"http://x.com": {"curso": "Curso", "tipoCurso": "Licenciatura", "escola": "ISEL"}}
        chaves_esperadas = {"curso", "link", "tipoCurso", "escola"}

    ficheiro.write_text(json.dumps(dados), encoding="utf-8")

    resultado = utilis.load_links(str(ficheiro), newsletter)
    assert set(resultado[0].keys()) == chaves_esperadas

def test_fetch():
    with patch("utilis.urlopen") as mock_urlopen:
        mock_response = MagicMock()
        mock_response.read.return_value = b"<html>conteudo</html>"
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response
        resultado = utilis.fetch("http://exemplo.com")
        assert resultado == "<html>conteudo</html>"

def test_fetch_falha_todas_as_tentativas(monkeypatch):
    monkeypatch.setattr("utilis.sleep", lambda x: None)  # Evita delays durante o teste
    with patch("utilis.urlopen", side_effect=HTTPError("http://exemplo.com", 500, "Internal Server Error", {}, None)):
        resultado = utilis.fetch("http://exemplo.com")
        assert resultado is None

@pytest.mark.asyncio
async def test_fetch_async():
    semaphore = asyncio.Semaphore(1)
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.text.return_value = "<html>conteudo</html>"
    mock_session = MagicMock()
    mock_session.get.return_value.__aenter__.return_value = mock_response
    resultado = await utilis.fetch_async(mock_session, semaphore, "http://exemplo.com")
    assert resultado == "<html>conteudo</html>"

@pytest.mark.asyncio
async def test_fetch_async_status_diferente_de_200_tenta_novamente_e_falha(monkeypatch):
    monkeypatch.setattr(utilis.asyncio, "sleep", AsyncMock()) 

    semaphore = asyncio.Semaphore(1)
    mock_response = AsyncMock()
    mock_response.status = 404

    mock_session = MagicMock()
    mock_session.get.return_value.__aenter__.return_value = mock_response
    retries = 3

    resultado = await utilis.fetch_async(mock_session, semaphore, "http://exemplo.com", retries=retries)

    assert resultado is None
    assert mock_session.get.call_count == retries  # tentou RETRIES vezes


@pytest.mark.asyncio
async def test_fetch_async_excecao_de_rede_com_retry_ate_sucesso(monkeypatch):
    monkeypatch.setattr(utilis.asyncio, "sleep", AsyncMock())

    semaphore = asyncio.Semaphore(1)
    mock_response_ok = AsyncMock()
    mock_response_ok.status = 200
    mock_response_ok.text.return_value = "ok"

    mock_session = MagicMock()
    # primeira chamada lança excepção, segunda funciona
    mock_session.get.side_effect = [
       aiohttp.ClientError("falha de rede"),
        MagicMock(__aenter__=AsyncMock(return_value=mock_response_ok), __aexit__=AsyncMock(return_value=None)),
    ]

    resultado = await utilis.fetch_async(mock_session, semaphore, "http://exemplo.com")

    assert resultado == "ok"
    assert mock_session.get.call_count == 2


@pytest.mark.asyncio
async def test_fetch_async_falha_todas_as_tentativas(monkeypatch):
    monkeypatch.setattr(utilis.asyncio, "sleep", AsyncMock())

    semaphore = asyncio.Semaphore(1)
    mock_session = MagicMock()
    mock_session.get.side_effect = asyncio.TimeoutError("timeout")
    retries = 3

    resultado = await utilis.fetch_async(mock_session, semaphore, "http://exemplo.com", retries=retries)

    assert resultado is None
    assert mock_session.get.call_count == retries


def test_scrape_sequential_sem_curso(monkeypatch):
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

    def fake_parse_page(html, curso=None):
        soup = BeautifulSoup(html, 'html.parser')
        items = soup.find_all('div', class_='item')
        links = {}
        for item in items:
            title_tag = item.find('a')
            if title_tag:
                title = title_tag.get('href')
                links[title] = None
        return links

    all_news = {}
    base_url = "http://exemplo.com"
    min_page_items = 10
    monkeypatch.setattr(utilis, 'fetch', mock_fetch)
    monkeypatch.setattr(utilis, 'sleep', lambda x: None)  # Evita delays durante o teste
    utilis._scrape_sequential(base_url, fake_parse_page, 0, {}, all_news, min_page_items, curso=None)
    assert len(all_news) == 11
    assert chamadas["n"] == 2

def test_scrape_sequential_sem_curso_default(monkeypatch):
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

    def fake_parse_page(html, curso=None):
        soup = BeautifulSoup(html, 'html.parser')
        items = soup.find_all('div', class_='item')
        links = {}
        for item in items:
            title_tag = item.find('a')
            if title_tag:
                title = title_tag.get('href')
                links[title] = None
        return links

    all_news = {}
    base_url = "http://exemplo.com"
    min_page_items = 10
    monkeypatch.setattr(utilis, 'fetch', mock_fetch)
    monkeypatch.setattr(utilis, 'sleep', lambda x: None)  # Evita delays durante o teste
    utilis._scrape_sequential(base_url, fake_parse_page, 0, {}, all_news, min_page_items)
    assert len(all_news) == 11
    assert chamadas["n"] == 2

def test_scrape_sequential_com_curso(monkeypatch):
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

    def fake_parse_page(html, curso=None):
        soup = BeautifulSoup(html, 'html.parser')
        items = soup.find_all('div', class_='item')
        links = {}
        for item in items:
            title_tag = item.find('a')
            if title_tag:
                title = title_tag.get('href')
                links[title] = None
        return links

    all_news = {}
    base_url = "http://exemplo.com"
    min_page_items = 10
    monkeypatch.setattr(utilis, 'fetch', mock_fetch)
    monkeypatch.setattr(utilis, 'sleep', lambda x: None)  # Evita delays durante o teste
    curso = "ISEL"
    utilis._scrape_sequential(base_url, fake_parse_page, 0, {}, all_news, min_page_items, curso=curso)
    assert len(all_news) == 11
    assert chamadas["n"] == 2

def test_scrape_sequential_sem_items_novos(monkeypatch):
    html = """
        <div class="view-content-wrap">
            <div class="item"><div class="views-field-title"><a href="/ja/existe">Newsletter Já Existente</a></div></div>
        </div>
    """

    def fake_parse_page(html, curso=None):
        soup = BeautifulSoup(html, 'html.parser')
        items = soup.find_all('div', class_='item')
        links = {}
        for item in items:
            title_tag = item.find('a')
            if title_tag:
                title = title_tag.get('href')
                links[title] = None
        return links

    chamadas = {"n": 0}
    def mock_fetch(url):
        chamadas["n"] += 1
        return html

    monkeypatch.setattr(utilis, 'fetch', mock_fetch)
    monkeypatch.setattr(utilis, 'sleep', lambda x: None) 
    
    existing_data = {"/ja/existe": {"link": "https://www.ipl.pt/ja/existe"}}
    all_news = dict(existing_data)  
    base_url = "http://exemplo.com"
    min_page_items = 10 
    utilis._scrape_sequential(base_url, fake_parse_page, 0, existing_data, all_news, min_page_items)
    
    assert len(all_news) == 1 
    assert chamadas["n"] == 1  

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

    def fake_parse_page(html, curso=None):
        soup = BeautifulSoup(html, 'html.parser')
        items = soup.find_all('div', class_='item')
        links = {}
        for item in items:
            title_tag = item.find('a')
            if title_tag:
                title = title_tag.get('href')
                links[title] = None
        return links

    existing_data = {"Newsletter Já Existente": {"link": "https://www.ipl.pt/ja/existe"}}
    all_news = dict(existing_data)  # Copia para simular o estado inicial

    chamadas = {"n": 0}
    
    def mock_fetch(url):
        chamadas["n"] += 1
        return html_novo if chamadas["n"] == 1 else html_existente

    monkeypatch.setattr(utilis, 'fetch', mock_fetch)
    monkeypatch.setattr(utilis, 'sleep', lambda x: None)
    base_url = "http://exemplo.com"
    min_page_items = 10
    utilis._scrape_sequential(base_url, fake_parse_page, 0, existing_data, all_news, min_page_items)
    assert chamadas["n"] == 1
    assert len(all_news) == 2  # Um item existente e um novo
    
def test_scrape_sequential_pagina_com_items_novos_e_existentes(monkeypatch):
    items_html = "".join(
        f'<div class="item"><div class="views-field-title"><a href="/item{i}">Newsletter {i}</a></div></div>'
        for i in range(10)
    )
    html_pagina_0 = f'<div class="view-content-wrap">{items_html}</div>'
    html_pagina_1 = '<div class="view-content-wrap"></div>'

    def fake_parse_page(html, curso=None):
        soup = BeautifulSoup(html, 'html.parser')
        items = soup.find_all('div', class_='item')
        links = {}
        for item in items:
            title_tag = item.find('a')
            if title_tag:
                title = title_tag.get('href')
                links[title] = None
        return links

    existing_data = {
        "/item9": None,
        "/item8": None,
    }
    all_news = dict(existing_data)

    chamadas = {"n": 0}
    def mock_fetch(url):
        chamadas["n"] += 1
        return html_pagina_0 if chamadas["n"] == 1 else html_pagina_1

    base_url = "http://exemplo.com"
    min_page_items = 10
    monkeypatch.setattr(utilis, 'fetch', mock_fetch)
    monkeypatch.setattr(utilis, 'sleep', lambda x: None)
    utilis._scrape_sequential(base_url, fake_parse_page, 0, existing_data, all_news, min_page_items)

    print(all_news)

    assert len(all_news) == 10          # 2 existentes + 8 novos
    assert chamadas["n"] == 2           # avançou para a página 1 (10 itens == MIN_ITEMS_PER_PAGE)~


@pytest.mark.asyncio
async def test_scrape_chunk_adiciona_todos_os_resultados():
    async def fake_scrape(session, link_info, existing_data, semaphore):
        return (link_info["link"], {"titulo": link_info["link"]})

    chunk = [{"link": "/a"}, {"link": "/b"}, {"link": "/c"}]
    all_data_shared = {}
    semaphore = asyncio.Semaphore(1)

    await utilis._scrape_chunk(None, chunk, {}, all_data_shared, semaphore, fake_scrape)

    assert len(all_data_shared) == 3
    assert "/a" in all_data_shared


@pytest.mark.asyncio
async def test_scrape_chunk_erro_num_item_nao_bloqueia_os_outros():
    async def fake_scrape(session, link_info, existing_data, semaphore):
        if link_info["link"] == "/falha":
            raise Exception("erro simulado")
        return (link_info["link"], {"titulo": link_info["link"]})

    chunk = [{"link": "/a"}, {"link": "/falha"}, {"link": "/c"}]
    all_data_shared = {}
    semaphore = asyncio.Semaphore(1)

    await utilis._scrape_chunk(None, chunk, {}, all_data_shared, semaphore, fake_scrape)

    assert len(all_data_shared) == 2          # "/falha" não entrou, os outros sim
    assert "/falha" not in all_data_shared
    assert "/a" in all_data_shared
    assert "/c" in all_data_shared


@pytest.mark.asyncio
async def test_scrape_chunk_resultado_none_nao_adiciona_nada():
    async def fake_scrape(session, link_info, existing_data, semaphore):
        return None  # já existia, ou falhou o parse

    chunk = [{"link": "/a"}, {"link": "/b"}]
    all_data_shared = {}
    semaphore = asyncio.Semaphore(1)

    await utilis._scrape_chunk(None, chunk, {}, all_data_shared, semaphore, fake_scrape)

    assert all_data_shared == {}


@pytest.mark.asyncio
async def test_scrape_parallel_divide_em_chunks_corretamente(monkeypatch, tmp_path):
    ficheiro = tmp_path / "data.json"
    ficheiro.write_text('{"Antigo": {}}', encoding="utf-8")
    chunks_recebidos = []

    async def fake_scrape_chunk(session, chunk, existing_data, all_data_shared, semaphore, scrape_func, prefix=""):
        chunks_recebidos.append(chunk)
        for item in chunk:
            all_data_shared[item["link"]] = {"titulo": item["link"]}

    monkeypatch.setattr(utilis, "_scrape_chunk", fake_scrape_chunk)
    monkeypatch.setattr(utilis, "load_existing_data", lambda output_file: {})
    monkeypatch.setattr(utilis, "save_data", lambda data, sort_key, output_file: None)
    monkeypatch.setattr(utilis, "aiohttp", type("FakeAiohttp", (), {
        "ClientSession": lambda *a, **k: _FakeSession()
    }))

    links = [{"link": f"/{i}"} for i in range(10)]
    semaphore = asyncio.Semaphore(1)
 
    def fake_scrape_something(links, semaphore, num_scrapers):
        pass

    sort_key = "titulo"
    await utilis.scrape_parallel(ficheiro, links, semaphore, sort_key, fake_scrape_something, 3, False)

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
    semaphore = asyncio.Semaphore(1)

    monkeypatch.setattr(utilis, "load_existing_data", lambda output_file: {"Antigo": {}})
    monkeypatch.setattr(utilis, "_scrape_chunk", AsyncMock())
    monkeypatch.setattr(utilis, "save_data", lambda data, sort_key, output_file: None)

    dados_guardados = {}
    def fake_save(data, sort_key, output_file):
        dados_guardados.update(data)
    monkeypatch.setattr(utilis, "save_data", fake_save)

    class _FakeSession:
        async def __aenter__(self): return self
        async def __aexit__(self, *a): return None
    monkeypatch.setattr(utilis.aiohttp, "ClientSession", lambda *a, **k: _FakeSession())

    sort_key = "titulo"
    def fake_scrape_something(links, semaphore, num_scrapers):
        return {link["link"]: {"titulo": link["link"]} for link in links}
    num_scrapers = 3

    await utilis.scrape_parallel(ficheiro, [], semaphore, sort_key, fake_scrape_something, num_scrapers, force_full=True)

    assert not ficheiro.exists()  # foi apagado por force_full antes de gravar de novo