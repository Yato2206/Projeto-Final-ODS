from unittest.mock import patch, MagicMock, AsyncMock
import asyncio
import pytest
from pathlib import Path
import json
import scraper_docentes as scraper
from urllib.error import HTTPError
from datetime import datetime
from bs4 import BeautifulSoup

#selector tem de abranger os elementos pretentidos, e nao apenas o elemento pai, para que o parse_element funcione corretamente.abs
#EXEMPLO: se eu quero um a que esta dentro de um span, o selector tem de ser span, de modo a que a funcao receba o elemento do a
@pytest.mark.parametrize("escola, html, selector, nome_esperado, link_esperado, expected_count", [
    #CASOS DE SUCESSO
    (
        "ESCS",
        """
        <div class="item">
            <div>
                <div class="views-field views-field-view-node">
                    <a>
                    <div class="views-field views-field-title">
                        <span> <a href="/TEST/ESCS">TEST ESCS</span>
                    </div>
                    </a>
                </div>
            </div>
        </div>
        """,
        "div",
        "TEST ESCS",
        "https://www.escs.ipl.pt/TEST/ESCS",
        1
    ),
    (
        "ESD",
        '<div class="content-main"><span><a href="/TEST/ESD">TEST ESD</a></span></div>',
        "span",
        "TEST ESD",
        "https://www.esd.ipl.pt/TEST/ESD",
        1
    ),
    (
        "ESELX",
        '<div class="container-bg"><div><a href="/TEST/ESELX">TEST ESELX</a></div></div>',
        "div",
        "TEST ESELX",
        "https://www.eselx.ipl.pt/TEST/ESELX",
        1
    ),
    (
        "ESML",
        '<div class="t3-content"><h2><a href="/TEST/ESML">TEST ESML</a></h2></div>',
        "h2",
        "TEST ESML",
        "https://www.esml.ipl.pt/TEST/ESML",
        1
    ),
    (
        "ESTC",
        '<div class="content-main"><tr><a href="/TEST/ESTC">TEST ESTC</a></tr></div>',
        "tr",
        "TEST ESTC",
        "https://www.estc.ipl.pt/TEST/ESTC",
        1    
    ),
    (
        "ESSL",
        '<div class = table><tr><td><a href="/TEST/ESSL">TEST ESSL</a></td></tr></div>',
        "tr",
        "TEST ESSL",
        "https://www.essl.ipl.pt/TEST/ESSL",
        1
    ),
    (
        "ISCAL",
        '<div class="mt-5"><tr><a href="/TEST/ISCAL">TEST ISCAL</a></tr></div>',
        "tr",
        "TEST ISCAL",
        "https://www.iscal.ipl.pt/TEST/ISCAL",
        1
    ),
    (
        "ISEL",
        '<div class="gva-view-grid"><span><a href="/TEST/ISEL">TEST ISEL</a></span></div>',
        "span",
        "TEST ISEL",
        "https://www.isel.pt/TEST/ISEL",
        1
    ),
    (#caso especial dos href ESSL
        "ESSL",
        '<div class = table><tr><td><a href="mailto:test@essl.ipl.pt">TEST ESSL</a></td></tr></div>',
        "tr",
        "TEST ESSL",
        "LINK NAO DISPONIVEL",
        1
    ),
    #CASOS DE ERRO
    (
        "ISEL",
        '<div class="gva-view-grid"><span><span href="/TEST/ISEL">TEST ISEL</span></span></div>',
        "span",
        "TEST ISEL",
        "https://www.isel.pt/TEST/ISEL",
        0
    ),
    (#sem nome
        "ISEL",
        '<div class="gva-view-grid"><span><a>TEST ISEL</a></span></div>',
        "span",
        "TEST ISEL",
        "https://www.isel.pt/TEST/ISEL",
        0
    ),
    (#caso especial do ESELX com departamento"
        "ESELX",
        '<div class="container-bg"><div><a href="/TEST/ESELX">Departamento TEST ESELX</a></div></div>',
        "div",
        "Departamento TEST ESELX",
        "https://www.eselx.ipl.pt/TEST/ESELX",
        0
    ),
    (
        "ISEL",
        '<div class="gva-view-grid"><span><a>TEST ISEL</a></span></div>',
        "span",
        "TEST ISEL",
        "https://www.isel.pt/TEST/ISEL",
        0
    ),
    (#href com mailto
        "ISEL",
        '<div class="gva-view-grid"><span><a href="mailto:test@isel.pt">TEST ISEL</a></span></div>',
        "span",
        "TEST ISEL",
        "https://www.isel.pt/TEST/ISEL",
        0
    ),
    (#href comecado com ?
        "ISEL",
        '<div class="gva-view-grid"><span><a href="?test=isel">TEST ISEL</a></span></div>',
        "span",
        "TEST ISEL",
        "https://www.isel.pt/TEST/ISEL",
        0
    )
])
def test_parse_element(escola, html, selector, nome_esperado, link_esperado, expected_count):
    soup = BeautifulSoup(html, "html.parser")
    print(f"HTML: {soup}")
    items = soup.select(selector)
    print(f"Items found: {items}")

    docentes = {}
    for element in items:
        result = scraper.parse_element(element, escola)
        if result:
            nome, record = result
            docentes[nome] = record

    assert len(docentes) == expected_count
    if expected_count > 0:
        assert nome_esperado in docentes
        assert docentes[nome_esperado]["escola"] == escola
        assert docentes[nome_esperado]["link"] == link_esperado
        assert "dateChecked" in docentes[nome_esperado]

@pytest.mark.parametrize("escola, html, expected_count", [
    (
        "ESCS",
        """
        <div class="item">
            <div>
                <div class="views-field views-field-view-node">
                    <a>
                    <div class="views-field views-field-title">
                        <span> <a href="/TEST/ESCS">TEST ESCS</span>
                    </div>
                    </a>
                </div>
            </div>
        </div>
        """,
        1
    ),
    (
        "ESD",
        '<div class="content-main"><span><a href="/TEST/ESD">TEST ESD</a></span></div>',
        1
    ),
    (
        "ESELX",
        '<div class="container-bg"><div><a href="/TEST/ESELX">TEST ESELX</a></div></div>',
        1
    ),
    (
        "ESML",
        '<div class="t3-content"><h2><a href="/TEST/ESML">TEST ESML</a></h2></div>',
        1
    ),
    (
        "ESTC",
        '<div class="content-main"><tr><a href="/TEST/ESTC">TEST ESTC</a></tr></div>',
        1    
    ),
    (
        "ESSL",
        '<div class = table><tr><td><a href="/TEST/ESSL">TEST ESSL</a></td></tr></div>',
        1
    ),
    (
        "ISCAL",
        '<div class="mt-5"><tr><a href="/TEST/ISCAL">TEST ISCAL</a></tr></div>',
        1
    ),
    (
        "ISEL",
        '<div class="gva-view-grid"><span><a href="/TEST/ISEL">TEST ISEL</a></span></div>',
        1
    )
])

def test_parse_docentes(html, escola, expected_count):
    resultado = scraper.parse_docentes(html, escola)
    assert len(resultado) == expected_count
    if expected_count > 0:
        assert "dateChecked" in resultado[f"TEST {escola}"]
        assert resultado[f"TEST {escola}"]["escola"] == escola
        if escola == "ISEL":
            assert resultado[f"TEST {escola}"]["link"] == f"https://www.isel.pt/TEST/{escola}"
        else:
            assert resultado[f"TEST {escola}"]["link"] == f"https://www.{escola.lower()}.ipl.pt/TEST/{escola}"

@pytest.mark.parametrize("escola, direct, expected_count", [
    ("ESCS", False, 0),
    ("ESD", True, 1),
    ("ESELX", False, 0),
    ("ESML", False, 0),
    ("ESTC", True, 1),
    ("ESSL", True, 1),
    ("ISCAL", False, 0),
    ("ISEL", False, 0)
])

def test_build_link_sources(escola, direct, expected_count, monkeypatch):
    monkeypatch.setattr(scraper, "load_departamentos_links", lambda escola: [])

    resultado = scraper.build_link_sources(escola)
    assert len(resultado) == expected_count
    if expected_count > 0:
        assert resultado[0]["escola"] == escola
        assert "link" in resultado[0]
        assert "source" in resultado[0]
    if direct:
        assert resultado[0]["source"] == "direct"
        assert resultado[0]["link"] == scraper.DIRECT_URLS[escola]

@pytest.mark.asyncio
async def test_scrape_paginated_source(monkeypatch):
    paginas = [
        {"Docente A": {"link": "/a"}, "Docente B": {"link": "/b"}, "Docente C": {"link": "/c"}}, 
        {"Docente D": {"link": "/d"}, "Docente E": {"link": "/e"}, "Docente F": {"link": "/f"}}, 
        {"Docente G": {"link": "/g"}},                                                             
    ]
    chamadas = {"n": 0}

    async def fake_fetch(session, semaphore, url, escola):
        chamadas["n"] += 1
        return "<html></html>"

    def fake_parse(html, escola):
        return paginas[chamadas["n"] - 1]

    monkeypatch.setattr(scraper, "fetch", fake_fetch)
    monkeypatch.setattr(scraper, "parse_docentes", fake_parse)

    accumulated = {}
    resultado = await scraper.scrape_paginated_source(None, None,"ISEL","http://x.com?page=", 3, accumulated)

    assert resultado == 7 
    assert len([k for k in accumulated if k not in ("escola", "sourceUrl", "dateChecked")]) == 7
    assert accumulated["escola"] == "ISEL"
    assert accumulated["sourceUrl"] == "http://x.com?page=2" 

@pytest.mark.asyncio
async def test_scrape_paginated_source_fetch_falha(monkeypatch):
    monkeypatch.setattr(scraper, "fetch", AsyncMock(return_value=None))

    accumulated = {}
    resultado = await scraper.scrape_paginated_source(None, None, "ISEL", "http://x.com?page=", 10, accumulated)

    assert resultado == 0
    assert accumulated == {}


@pytest.mark.asyncio
async def test_scrape_paginated_source_parse_devolve_vazio(monkeypatch):
    monkeypatch.setattr(scraper, "fetch", AsyncMock(return_value="<html></html>"))
    monkeypatch.setattr(scraper, "parse_docentes", lambda html, escola: {})

    accumulated = {}
    resultado = await scraper.scrape_paginated_source(None, None, "ISEL", "http://x.com?page=", 10, accumulated)

    assert resultado == 0
    assert accumulated == {}


@pytest.mark.asyncio
async def test_scrape_paginated_source_uma_pagina_com_menos_que_max(monkeypatch):
    monkeypatch.setattr(scraper, "fetch", AsyncMock(return_value="<html></html>"))
    monkeypatch.setattr(scraper, "parse_docentes", lambda html, escola: {
        "Docente A": {"link": "/a"},
        "Docente B": {"link": "/b"},
    })

    accumulated = {}
    resultado = await scraper.scrape_paginated_source(None, None, "ISEL", "http://x.com?page=", 10, accumulated)

    assert resultado == 2
    assert "Docente A" in accumulated
    assert "Docente B" in accumulated
    assert accumulated["escola"] == "ISEL"
    assert "sourceUrl" in accumulated
    assert "dateChecked" in accumulated


@pytest.mark.asyncio
async def test_scrape_paginated_source_multiplas_paginas(monkeypatch):
    paginas = [
        {"Docente A": {"link": "/a"}, "Docente B": {"link": "/b"}},  
        {"Docente C": {"link": "/c"}},                                
    ]
    chamadas = {"n": 0}

    async def fake_fetch(session, semaphore, url, escola):
        chamadas["n"] += 1
        return "<html></html>"

    def fake_parse(html, escola):
        idx = chamadas["n"] - 1
        return paginas[idx] if idx < len(paginas) else {}

    monkeypatch.setattr(scraper, "fetch", fake_fetch)
    monkeypatch.setattr(scraper, "parse_docentes", fake_parse)

    accumulated = {}
    resultado = await scraper.scrape_paginated_source(None, None, "ISEL", "http://x.com?page=", 2, accumulated)

    assert resultado == 3 
    assert chamadas["n"] == 2
    assert "Docente A" in accumulated
    assert "Docente C" in accumulated


@pytest.mark.asyncio
async def test_scrape_paginated_source_url_construida_corretamente(monkeypatch):
    urls_chamadas = []

    async def fake_fetch(session, semaphore, url, escola):
        urls_chamadas.append(url)
        return "<html></html>"

    monkeypatch.setattr(scraper, "fetch", fake_fetch)
    monkeypatch.setattr(scraper, "parse_docentes", lambda html, escola: {})
    await scraper.scrape_paginated_source(None, None, "ISEL", "http://x.com?page=", 10, {}, start_page=3)

    assert urls_chamadas == ["http://x.com?page=3"]


@pytest.mark.asyncio
async def test_scrape_paginated_source_acumula_metadata_da_ultima_pagina(monkeypatch):
    paginas = [
        {"D1": {"link": "/1"}, "D2": {"link": "/2"}},   
        {"D3": {"link": "/3"}},                         
    ]
    chamadas = {"n": 0}

    async def fake_fetch(session, semaphore, url, escola):
        chamadas["n"] += 1
        return "<html></html>"

    def fake_parse(html, escola):
        return paginas[chamadas["n"] - 1]

    monkeypatch.setattr(scraper, "fetch", fake_fetch)
    monkeypatch.setattr(scraper, "parse_docentes", fake_parse)

    accumulated = {}
    await scraper.scrape_paginated_source(None, None, "ISEL", "http://x.com?page=", 2, accumulated)

    assert accumulated["sourceUrl"] == "http://x.com?page=1"


@pytest.mark.asyncio
async def test_scrape_paginated_source_fetch_falha_na_segunda_pagina(monkeypatch):
    chamadas = {"n": 0}

    async def fake_fetch(session, semaphore, url, escola):
        chamadas["n"] += 1
        return "<html></html>" if chamadas["n"] == 1 else None

    monkeypatch.setattr(scraper, "fetch", fake_fetch)
    monkeypatch.setattr(scraper, "parse_docentes", lambda html, escola: {
        "D1": {"link": "/1"}, "D2": {"link": "/2"}  
    })

    accumulated = {}
    resultado = await scraper.scrape_paginated_source(None, None, "ISEL", "http://x.com?page=", 2, accumulated)

    assert resultado == 2     
    assert chamadas["n"] == 2 

@pytest.mark.asyncio
async def test_scrape_one(monkeypatch):
    monkeypatch.setattr(scraper, "fetch", AsyncMock(return_value="<html></html>"))
    monkeypatch.setattr(scraper, "parse_docentes", lambda html, escola: {
        "Docente A": {"link": "/a"},
    })

    link_info = {"link": "http://x.com/1", "title": "Dep A"}
    resultado = await scraper.scrape_one(None, None, "ISEL", link_info, set())

    assert "ISEL::Dep A" in resultado
    assert resultado["ISEL::Dep A"]["sourceUrl"] == "http://x.com/1"
    assert "Docente A" in resultado["ISEL::Dep A"]

@pytest.mark.asyncio
async def test_scrape_one_ja_foi_scraped(monkeypatch):
    mock_fetch = AsyncMock()
    monkeypatch.setattr(scraper, "fetch", mock_fetch)

    link_info = {"link": "http://x.com/1", "title": "Dep A"}
    resultado = await scraper.scrape_one(None, None, "ISEL", link_info, {"ISEL::Dep A"})

    assert resultado == {}
    mock_fetch.assert_not_called()

@pytest.mark.asyncio
async def test_scrape_one_fetch_falha(monkeypatch):
    monkeypatch.setattr(scraper, "fetch", AsyncMock(return_value=None))

    link_info = {"link": "http://x.com/1", "title": "Dep A"}
    resultado = await scraper.scrape_one(None, None, "ISEL", link_info, set())

    assert resultado == {}

@pytest.mark.asyncio
async def test_scrape_one_parse_devolve_vazio(monkeypatch):
    monkeypatch.setattr(scraper, "fetch", AsyncMock(return_value="<html></html>"))
    monkeypatch.setattr(scraper, "parse_docentes", lambda html, escola: {})

    link_info = {"link": "http://x.com/1", "title": "Dep A"}
    resultado = await scraper.scrape_one(None, None, "ISEL", link_info, set())

    assert resultado == {}

@pytest.mark.asyncio
async def test_scrape_one_sucesso_sem_title_usa_url_como_chave(monkeypatch):
    monkeypatch.setattr(scraper, "fetch", AsyncMock(return_value="<html></html>"))
    monkeypatch.setattr(scraper, "parse_docentes", lambda html, escola: {
        "Docente B": {"link": "/b"},
    })

    link_info = {"link": "http://x.com/1"}  
    resultado = await scraper.scrape_one(None, None, "ISEL", link_info, set())

    assert "ISEL::http://x.com/1" in resultado
    assert resultado["ISEL::http://x.com/1"]["sourceUrl"] == "http://x.com/1"

@pytest.mark.asyncio
async def test_scrape_one_source_url_adicionado_ao_record(monkeypatch):
    monkeypatch.setattr(scraper, "fetch", AsyncMock(return_value="<html></html>"))
    monkeypatch.setattr(scraper, "parse_docentes", lambda html, escola: {
        "Docente C": {"link": "/c"},
    })

    link_info = {"link": "http://x.com/dept", "title": "Dept"}
    resultado = await scraper.scrape_one(None, None, "ISEL", link_info, set())

    record = resultado["ISEL::Dept"]
    assert "sourceUrl" in record
    assert record["sourceUrl"] == "http://x.com/dept"

def _mock_escola_deps(monkeypatch, **overrides):
    """Mocka todas as dependências com defaults de sucesso."""
    defaults = {
        "load_existing_data": lambda escola: {},
        "load_departamentos_links": lambda escola: [{"link": "http://x.com/dept", "title": "Dep A"}],
        "build_link_sources": lambda escola: [{"link": "http://x.com/1", "title": "Dep A"}],
        "scrape_paginated_source": AsyncMock(return_value=5),
        "scrape_one": AsyncMock(return_value={"escola::Dep A": {"sourceUrl": "http://x.com/1"}}),
    }
    defaults.update(overrides)
    for name, mock in defaults.items():
        monkeypatch.setattr(scraper, name, mock)
    return defaults

@pytest.mark.asyncio
async def test_scrape_escola_ISEL_paginada(monkeypatch):
    mocks = _mock_escola_deps(monkeypatch)
    monkeypatch.setattr(scraper, "PAGINATED_SCHOOLS", {
        "ISEL": {"max_per_page": 10, "page_url": "http://x.com?page="}
    })
    resultado = await scraper.scrape_escola(None, None, "ISEL")

    assert "ISEL" in resultado
    mocks["scrape_paginated_source"].assert_called_once()


@pytest.mark.asyncio
async def test_scrape_escola_ISEL_sem_link_sources(monkeypatch):
    _mock_escola_deps(monkeypatch, load_departamentos_links=lambda escola: [])
    monkeypatch.setattr(scraper, "PAGINATED_SCHOOLS", {
        "ISEL": {"max_per_page": 10, "page_url": "http://x.com?page="}
    })
    resultado = await scraper.scrape_escola(None, None, "ISEL")

    assert resultado == {}


@pytest.mark.asyncio
async def test_scrape_escola_paginada(monkeypatch):
    mocks = _mock_escola_deps(monkeypatch)
    monkeypatch.setattr(scraper, "PAGINATED_SCHOOLS", {
        "ESD": {"max_per_page": 10, "page_url": "http://x.com?page="}
    })

    resultado = await scraper.scrape_escola(session=None, semaphore=None, escola="ESD")

    assert "ESD" in resultado
    mocks["scrape_paginated_source"].assert_called_once()

@pytest.mark.asyncio
async def test_scrape_escola_nao_paginada(monkeypatch):
    mocks = _mock_escola_deps(monkeypatch)
    monkeypatch.setattr(scraper, "PAGINATED_SCHOOLS", {})
    resultado = await scraper.scrape_escola(None, None, "ESD")

    assert "escola::Dep A" in resultado
    mocks["scrape_one"].assert_called_once()

@pytest.mark.asyncio
async def test_scrape_escola_directa_sem_link_sources(monkeypatch):
    _mock_escola_deps(monkeypatch, build_link_sources=lambda escola: [])
    monkeypatch.setattr(scraper, "PAGINATED_SCHOOLS", {})
    resultado = await scraper.scrape_escola(None, None, "ESELX")

    assert resultado == {}

@pytest.mark.asyncio
async def test_scrape_escola_directa_existing_data_preservado(monkeypatch):
    _mock_escola_deps(
        monkeypatch,
        load_existing_data=lambda escola: {"ESELX::Antigo": {"sourceUrl": "http://antigo.com"}},
        scrape_one=AsyncMock(return_value={}),   
    )
    monkeypatch.setattr(scraper, "PAGINATED_SCHOOLS", {})
    resultado = await scraper.scrape_escola(None, None, "ESELX")

    assert "ESELX::Antigo" in resultado   # existente foi preservado