from unittest.mock import patch, MagicMock, AsyncMock
import asyncio
import pytest
from pathlib import Path
import pytest_asyncio
import json
import scraper_repo_cientifico as scraper
from playwright.async_api import async_playwright
from urllib.error import HTTPError
from datetime import datetime

def test_extract_year_from_date():
    date_str = "2026-06-20"
    year = scraper.extract_year_from_date(date_str)
    assert year == 2026

def test_extract_year_from_date_invalid():
    date_str = "invalid-date"
    year = scraper.extract_year_from_date(date_str)
    assert year is None

def test_extract_year_from_date_none():
    date_str = None
    year = scraper.extract_year_from_date(date_str)
    assert year is None

def test_extract_year_from_date_empty():
    date_str = ""
    year = scraper.extract_year_from_date(date_str)
    assert year is None

@pytest.mark.asyncio
async def test_extract_item_data():
    mock_element = AsyncMock()
    mock_element.evaluate.return_value = {
        "titulo": "TESTE",
        "autores": "Autor 1, Autor 2",
        "texto": "Texto de teste.",
        "dataPublicacao": "2026-06-06",
        "tipo": "TIPO TESTE",
        "acesso": "Open Access",
        "link": "https://example.com/link_teste",
    }

    link, data = await scraper.extract_item_data(mock_element)
    assert link == "https://example.com/link_teste"
    assert data["titulo"] == "TESTE"
    assert "link" not in data           # confirma que foi removido
    assert "dateChecked" in data

@pytest.mark.asyncio
async def test_extract_item_data_sem_link_devolve_none():
    mock_element = AsyncMock()
    mock_element.evaluate.return_value = {
        "titulo": "Sem link",
        "link": None,
    }

    link, data = await scraper.extract_item_data(mock_element)
    assert link is None
    assert data is None

@pytest.mark.asyncio
async def test_extract_item_data_sem_data():
    mock_element = AsyncMock()
    mock_element.evaluate.return_value = None  # Simula que não há dados extraídos

    link, data = await scraper.extract_item_data(mock_element)
    assert link is None
    assert data is None

@pytest.mark.asyncio
async def test_extract_item_data_excecao_e_apanhada():
    mock_element = AsyncMock()
    mock_element.evaluate.side_effect = Exception("error")

    link, data = await scraper.extract_item_data(mock_element)
    assert link is None
    assert data is None

@pytest.mark.asyncio
async def test_extract_item_data_campos_em_falta_ficam_vazios():
    mock_element = AsyncMock()
    mock_element.evaluate.return_value = {
        "titulo": "TESTE",
        "autores": "",
        "texto": "",
        "dataPublicacao": "",
        "tipo": "",
        "acesso": "",
        "link": "https://example.com/link_teste",
    }

    link, data = await scraper.extract_item_data(mock_element)
    assert link == "https://example.com/link_teste"
    assert data["autores"] == ""
    assert data["texto"] == ""
    assert data["dataPublicacao"] == ""
    assert data["tipo"] == ""
    assert data["acesso"] == ""

@pytest.mark.asyncio
async def test_extract_item_data_com_playwright_real():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        await page.set_content("""
        <div id="item">
            <a href="/teste">TESTE</a>
            <div class="tag_elements">
                <a>2026-06-06</a>
                <a>Tipo Teste</a>
            </div>
            <div class="clamp-default-2"><span class="item-list-authors">Autor Teste</span></div>
            <div class="clamp-default-3"><div class="content"><span>Texto de exemplo.</span></div></div>
            <div class="access-status-list-element-badge"><a>Open Access</a></div>
        </div>
        """)

        element = await page.query_selector("#item")
        link, data = await scraper.extract_item_data(element)

        assert link == "https://repositorio.ipl.pt/teste"
        assert data["titulo"] == "TESTE"
        assert data["autores"] == "Autor Teste"
        assert data["dataPublicacao"] == "2026-06-06"

        await browser.close()

@pytest.mark.asyncio
async def test_access_base_url():
    mock_page = AsyncMock()
    base_url = "https://example.com/"
    result = await scraper.access_base_url(mock_page, base_url)
    assert result is True
    mock_page.goto.assert_called_once_with(base_url, wait_until="networkidle", timeout=15000)

@pytest.mark.asyncio
async def test_access_base_url_excecao_e_apanhada():
    mock_page = AsyncMock()
    mock_page.goto.side_effect = Exception("error")
    result = await scraper.access_base_url(mock_page, "https://example.com/")
    assert result is False

@pytest_asyncio.fixture
async def page():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        pg = await browser.new_page()
        yield pg
        await browser.close()

@pytest.mark.asyncio
async def test_click_load_more_button_pt(page):
    await page.set_content("<button>Carregar mais</button>")
    resultado = await scraper.click_and_load_more_button(page)
    assert resultado is True

@pytest.mark.asyncio
async def test_click_load_more_button_en(page):
    await page.set_content('<input aria-label="Load more" type="button" />')
    resultado = await scraper.click_and_load_more_button(page)
    assert resultado is True

@pytest.mark.asyncio
async def test_click_load_more_button_none(page):
    await page.set_content("<div>No button here</div>")
    resultado = await scraper.click_and_load_more_button(page)
    assert resultado is False

@pytest.mark.asyncio
async def test_find_and_expand_date_filter_encontra_e_clica(page):
    await page.set_content("""
        <div class="facet-filter">
            <span>Outro filtro qualquer</span>
        </div>
        <div class="facet-filter">
            <span>Data de Publicação</span>
            <button class="filter-name">Expandir</button>
        </div>
    """)

    resultado = await scraper.find_and_expand_date_filter(page)

    assert resultado is not None
    # confirma que o filtro devolvido é mesmo o segundo (o que tem "Data")
    texto = await resultado.text_content()
    assert "Data" in texto


@pytest.mark.asyncio
async def test_find_and_expand_date_filter_label_em_ingles(page):
    await page.set_content("""
        <div class="facet-filter">
            <span>Date Range</span>
            <button class="filter-name">Expand</button>
        </div>
    """)

    resultado = await scraper.find_and_expand_date_filter(page)
    assert resultado is not None


@pytest.mark.asyncio
async def test_find_and_expand_date_filter_nao_encontrado(page):
    """Nenhum .facet-filter contém 'Data' ou 'Date'."""
    await page.set_content("""
        <div class="facet-filter"><span>Categoria</span></div>
        <div class="facet-filter"><span>Autor</span></div>
    """)

    resultado = await scraper.find_and_expand_date_filter(page)
    assert resultado is None


@pytest.mark.asyncio
async def test_find_and_expand_date_filter_sem_botao_toggle(page):
    """O filtro de data existe, mas falta o button.filter-name."""
    await page.set_content("""
        <div class="facet-filter">
            <span>Data</span>
        </div>
    """)

    resultado = await scraper.find_and_expand_date_filter(page)
    assert resultado is None


@pytest.mark.asyncio
async def test_find_and_expand_date_filter_nenhum_facet_filter_existe(page):
    await page.set_content("<div>nada relevante aqui</div>")

    resultado = await scraper.find_and_expand_date_filter(page)
    assert resultado is None

@pytest.mark.asyncio
async def test_find_and_expand_date_filter_real_behavior(page):
    await page.set_content("""
        <div class="facet-filter">
            <span>Data</span>
            <button class="filter-name" onclick="this.setAttribute('aria-expanded', 'true')">
                Expandir
            </button>
        </div>
    """)

    resultado = await scraper.find_and_expand_date_filter(page)

    assert resultado is not None
    botao = await page.query_selector("button.filter-name")
    expandido = await botao.get_attribute("aria-expanded")
    assert expandido == "true"   # confirma que o click() real disparou o onclick

@pytest.mark.asyncio
async def test_fill_date_field_label_portugues(page):
    await page.set_content('<input aria-label="Data mínima" type="text" />')

    resultado = await scraper.fill_date_field(
        page, "2026", ["Data mínima", "Minimum Date"], "[7/14]"
    )

    assert resultado is True
    valor = await page.locator('input[aria-label="Data mínima"]').input_value()
    assert valor == "2026"

@pytest.mark.asyncio
async def test_fill_date_field_fallback_ingles(page):
    await page.set_content('<input aria-label="Minimum Date" type="text" />')

    resultado = await scraper.fill_date_field(
        page, "2026", ["Data mínima", "Minimum Date"], "[7/14]"
    )

    assert resultado is True
    valor = await page.locator('input[aria-label="Minimum Date"]').input_value()
    assert valor == "2026"

@pytest.mark.asyncio
async def test_fill_date_field_nenhum_label_encontrado(page):
    await page.set_content('<input aria-label="Outro Campo" type="text" />')

    resultado = await scraper.fill_date_field(
        page, "2026", ["Data mínima", "Minimum Date"], "[7/14]"
    )

    assert resultado is False

@pytest.mark.asyncio
async def test_fill_date_field_substitui_valor_existente(page):
    """Confirma que .clear() de facto limpa antes de preencher, sem concatenar."""
    await page.set_content('<input aria-label="Data mínima" type="text" value="2020" />')

    resultado = await scraper.fill_date_field(
        page, "2026", ["Data mínima", "Minimum Date"], "[7/14]"
    )

    assert resultado is True
    valor = await page.locator('input[aria-label="Data mínima"]').input_value()
    assert valor == "2026"

@pytest.mark.asyncio
async def test_fill_date_field_enter_dispara_evento(page):
    await page.set_content("""
        <input aria-label="Data mínima" type="text" />
        <script>
            document.querySelector('input').addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    document.body.setAttribute('data-enter-pressed', 'true');
                }
            });
        </script>
    """)

    resultado = await scraper.fill_date_field(
        page, "2026", ["Data mínima", "Minimum Date"], "[7/14]"
    )

    assert resultado is True
    enter_pressionado = await page.locator("body").get_attribute("data-enter-pressed")
    assert enter_pressionado == "true"

@pytest.mark.asyncio
async def test_fill_min_date_delega_com_labels_corretos(monkeypatch):
    mock_fill = AsyncMock(return_value=True)
    monkeypatch.setattr(scraper, "fill_date_field", mock_fill)

    resultado = await scraper.fill_min_date(page=None, year_str="2026")

    assert resultado is True
    mock_fill.assert_called_once_with(
        None, "2026",
        aria_labels=["Data mínima", "Minimum Date"],
        step_label="[7/14]",
    )


@pytest.mark.asyncio
async def test_fill_max_date_delega_com_labels_corretos(monkeypatch):
    mock_fill = AsyncMock(return_value=True)
    monkeypatch.setattr(scraper, "fill_date_field", mock_fill)

    resultado = await scraper.fill_max_date(page=None, year_str="2026")

    assert resultado is True
    mock_fill.assert_called_once_with(
        None, "2026",
        aria_labels=["Data máxima", "Maximum Date"],
        step_label="[9/14]",
    )

@pytest.mark.asyncio
async def test_scrape_items_adiciona_itens_novos(page, monkeypatch):
    await page.set_content("""
        <div class="mt-4 mb-4 d-flex"></div>
        <div class="mt-4 mb-4 d-flex"></div>
    """)

    extracted = [
        ("https://x/1", {"titulo": "Item 1", "dataPublicacao": "2026-01-01"}),
        ("https://x/2", {"titulo": "Item 2", "dataPublicacao": "2026-02-01"}),
    ]
    mock_extract = AsyncMock(side_effect=extracted)
    monkeypatch.setattr(scraper, "extract_item_data", mock_extract)
    monkeypatch.setattr(scraper, "extract_year_from_date", lambda d: 2026)

    batch = {}
    found, skipped, dup = await scraper.scrape_items_from_page(
        page, year=2026, done_links=set(), batch=batch,
        items_skipped=0, page_count=1, force_full=False,
    )

    assert found == 2
    assert skipped == 0
    assert dup is False
    assert len(batch) == 2


@pytest.mark.asyncio
async def test_scrape_items_ignora_link_ou_data_vazios(page, monkeypatch):
    await page.set_content('<div class="mt-4 mb-4 d-flex"></div>')

    monkeypatch.setattr(scraper, "extract_item_data", AsyncMock(return_value=(None, None)))

    batch = {}
    found, skipped, dup = await scraper.scrape_items_from_page(
        page, year=2026, done_links=set(), batch=batch,
        items_skipped=0, page_count=1, force_full=False,
    )

    assert found == 0
    assert batch == {}


@pytest.mark.asyncio
async def test_scrape_items_salta_ano_diferente(page, monkeypatch):
    await page.set_content('<div class="mt-4 mb-4 d-flex"></div>')

    monkeypatch.setattr(scraper, "extract_item_data", AsyncMock(
        return_value=("https://x/1", {"titulo": "Item Antigo", "dataPublicacao": "2020-01-01"})
    ))
    monkeypatch.setattr(scraper, "extract_year_from_date", lambda d: 2020)

    batch = {}
    found, skipped, dup = await scraper.scrape_items_from_page(
        page, year=2026, done_links=set(), batch=batch,
        items_skipped=0, page_count=1, force_full=False,
    )

    assert found == 0
    assert skipped == 1
    assert batch == {}


@pytest.mark.asyncio
async def test_scrape_items_para_ao_encontrar_duplicado(page, monkeypatch):
    await page.set_content("""
        <div class="mt-4 mb-4 d-flex"></div>
        <div class="mt-4 mb-4 d-flex"></div>
    """)

    extracted = [
        ("https://x/ja-existe", {"titulo": "Já Existe", "dataPublicacao": "2026-01-01"}),
        ("https://x/novo", {"titulo": "Nunca Devia Chegar Aqui", "dataPublicacao": "2026-01-01"}),
    ]
    monkeypatch.setattr(scraper, "extract_item_data", AsyncMock(side_effect=extracted))
    monkeypatch.setattr(scraper, "extract_year_from_date", lambda d: 2026)

    batch = {}
    done_links = {"https://x/ja-existe"}

    found, skipped, dup = await scraper.scrape_items_from_page(
        page, year=2026, done_links=done_links, batch=batch,
        items_skipped=0, page_count=1, force_full=False,
    )

    assert dup is True
    assert found == 0         
    assert "https://x/novo" not in batch


@pytest.mark.asyncio
async def test_scrape_items_force_full_ignora_duplicados(page, monkeypatch):
    await page.set_content('<div class="mt-4 mb-4 d-flex"></div>')

    monkeypatch.setattr(scraper, "extract_item_data", AsyncMock(
        return_value=("https://x/ja-existe", {"titulo": "Já Existe", "dataPublicacao": "2026-01-01"})
    ))
    monkeypatch.setattr(scraper, "extract_year_from_date", lambda d: 2026)

    batch = {}
    done_links = {"https://x/ja-existe"}

    found, skipped, dup = await scraper.scrape_items_from_page(
        page, year=2026, done_links=done_links, batch=batch,
        items_skipped=0, page_count=1, force_full=True,   # ignora done_links
    )

    assert dup is False
    assert found == 1
    assert "https://x/ja-existe" in batch


@pytest.mark.asyncio
async def test_scrape_items_nao_duplica_link_ja_no_batch(page, monkeypatch):
    """Confirma o `if link not in batch` — mesmo link duas vezes na mesma página."""
    await page.set_content("""
        <div class="mt-4 mb-4 d-flex"></div>
        <div class="mt-4 mb-4 d-flex"></div>
    """)

    extracted = [
        ("https://x/repetido", {"titulo": "Repetido", "dataPublicacao": "2026-01-01"}),
        ("https://x/repetido", {"titulo": "Repetido", "dataPublicacao": "2026-01-01"}),
    ]
    monkeypatch.setattr(scraper, "extract_item_data", AsyncMock(side_effect=extracted))
    monkeypatch.setattr(scraper, "extract_year_from_date", lambda d: 2026)

    batch = {}
    found, skipped, dup = await scraper.scrape_items_from_page(
        page, year=2026, done_links=set(), batch=batch,
        items_skipped=0, page_count=1, force_full=False,
    )

    assert found == 1    
    assert len(batch) == 1


@pytest.mark.asyncio
async def test_scrape_items_acumula_items_skipped_existente(page, monkeypatch):
    """Confirma que items_skipped recebido como parâmetro é incrementado, não reiniciado."""
    await page.set_content('<div class="mt-4 mb-4 d-flex"></div>')

    monkeypatch.setattr(scraper, "extract_item_data", AsyncMock(
        return_value=("https://x/1", {"titulo": "Antigo", "dataPublicacao": "2020-01-01"})
    ))
    monkeypatch.setattr(scraper, "extract_year_from_date", lambda d: 2020)

    batch = {}
    found, skipped, dup = await scraper.scrape_items_from_page(
        page, year=2026, done_links=set(), batch=batch,
        items_skipped=5, page_count=1, force_full=False,   # já vinha com 5
    )

    assert skipped == 6   # incrementou a partir de 5, não reiniciou

@pytest.mark.asyncio
async def test_go_next_page_clica_quando_disponivel(page):
    await page.set_content('<a class="page-link">»</a>')

    resultado = await scraper.go_next_page(page)

    assert resultado is True


@pytest.mark.asyncio
async def test_go_next_page_botao_nao_encontrado(page):
    await page.set_content('<div>sem paginação aqui</div>')

    resultado = await scraper.go_next_page(page)

    assert resultado is False


@pytest.mark.asyncio
async def test_go_next_page_botao_desativado(page):
    await page.set_content('<a class="page-link" aria-disabled="true">»</a>')

    resultado = await scraper.go_next_page(page)

    assert resultado is False


@pytest.mark.asyncio
async def test_go_next_page_botao_ativado_explicitamente(page):
    """Confirma que aria-disabled="false" (ou ausente) não bloqueia o clique."""
    await page.set_content('<a class="page-link" aria-disabled="false">»</a>')

    resultado = await scraper.go_next_page(page)

    assert resultado is True


@pytest.mark.asyncio
async def test_go_next_page_clique_dispara_navegacao_real(page):
    """
    Confirma que o click() de facto teve efeito, não só que a função
    devolveu True — útil para apanhar regressões no selector/timing.
    """
    await page.set_content("""
        <a class="page-link" id="next">»</a>
        <script>
            document.getElementById('next').addEventListener('click', () => {
                document.body.setAttribute('data-clicked', 'true');
            });
        </script>
    """)

    resultado = await scraper.go_next_page(page)

    assert resultado is True
    clicado = await page.locator("body").get_attribute("data-clicked")
    assert clicado == "true"

def _mock_all_steps(monkeypatch, **overrides):
    """Mocka todos os passos do fluxo com defaults de sucesso, sobrepondo os que forem passados."""
    defaults = {
        "access_base_url": AsyncMock(return_value=True),
        "click_and_load_more_button": AsyncMock(return_value=True),
        "find_and_expand_date_filter": AsyncMock(return_value="filtro-fake"),
        "fill_min_date": AsyncMock(return_value=True),
        "fill_max_date": AsyncMock(return_value=True),
        "go_next_page": AsyncMock(return_value=False),  # por defeito, só uma página
        "save_to_rotating_file": AsyncMock(),
        "scrape_items_from_page": AsyncMock(return_value=(0, 0, False)),
    }
    defaults.update(overrides)
    for name, mock in defaults.items():
        monkeypatch.setattr(scraper, name, mock)
    return defaults

@pytest.fixture
def mock_page():
    """Page falsa, só precisa de responder a wait_for_timeout nestes testes de orquestração."""
    return AsyncMock()

@pytest.mark.asyncio
async def test_scrape_collection_by_year_para_se_access_base_url_falha(monkeypatch, mock_page):
    mocks = _mock_all_steps(monkeypatch, access_base_url=AsyncMock(return_value=False))

    resultado = await scraper.scrape_collection_by_year(page=mock_page, year=2026, done_links=set())

    assert resultado == 0
    mocks["click_and_load_more_button"].assert_not_called()


@pytest.mark.asyncio
async def test_scrape_collection_by_year_para_se_click_load_more_falha(monkeypatch, mock_page):
    mocks = _mock_all_steps(monkeypatch, click_and_load_more_button=AsyncMock(return_value=False))

    resultado = await scraper.scrape_collection_by_year(page=mock_page, year=2026, done_links=set())

    assert resultado == 0
    mocks["find_and_expand_date_filter"].assert_not_called()


@pytest.mark.asyncio
async def test_scrape_collection_by_year_para_se_filtro_de_data_nao_encontrado(monkeypatch, mock_page):
    mocks = _mock_all_steps(monkeypatch, find_and_expand_date_filter=AsyncMock(return_value=None))

    resultado = await scraper.scrape_collection_by_year(page=mock_page, year=2026, done_links=set())

    assert resultado == 0
    mocks["fill_min_date"].assert_not_called()


@pytest.mark.asyncio
async def test_scrape_collection_by_year_para_se_fill_min_date_falha(monkeypatch, mock_page):
    mocks = _mock_all_steps(monkeypatch, fill_min_date=AsyncMock(return_value=False))

    resultado = await scraper.scrape_collection_by_year(page=mock_page, year=2026, done_links=set())

    assert resultado == 0
    mocks["fill_max_date"].assert_not_called()


@pytest.mark.asyncio
async def test_scrape_collection_by_year_para_se_fill_max_date_falha(monkeypatch, mock_page):
    mocks = _mock_all_steps(monkeypatch, fill_max_date=AsyncMock(return_value=False))

    resultado = await scraper.scrape_collection_by_year(page=mock_page, year=2026, done_links=set())

    assert resultado == 0
    mocks["scrape_items_from_page"].assert_not_called()


@pytest.mark.asyncio
async def test_scrape_collection_by_year_para_quando_nao_ha_novos_itens(monkeypatch, mock_page):
    mocks = _mock_all_steps(
        monkeypatch,
        scrape_items_from_page=AsyncMock(return_value=(0, 0, False)),
    )

    resultado = await scraper.scrape_collection_by_year(page=mock_page, year=2026, done_links=set())

    assert resultado == 0
    mocks["go_next_page"].assert_not_called() 


@pytest.mark.asyncio
async def test_scrape_collection_by_year_continua_para_proxima_pagina_enquanto_houver_itens(monkeypatch, mock_page):
    """3 páginas com itens, a 4ª sem itens novos -> pára."""
    mocks = _mock_all_steps(
        monkeypatch,
        scrape_items_from_page=AsyncMock(side_effect=[
            (5, 0, False),
            (5, 0, False),
            (5, 0, False),
            (0, 0, False),
        ]),
        go_next_page=AsyncMock(side_effect=[True, True, True]),
    )

    resultado = await scraper.scrape_collection_by_year(page=mock_page, year=2026, done_links=set())

    assert resultado == 15  # 5+5+5+0
    assert mocks["scrape_items_from_page"].call_count == 4
    assert mocks["go_next_page"].call_count == 3


@pytest.mark.asyncio
async def test_scrape_collection_by_year_para_ao_encontrar_duplicado(monkeypatch, mock_page):
    mocks = _mock_all_steps(
        monkeypatch,
        scrape_items_from_page=AsyncMock(return_value=(3, 0, True)),  # reached_duplicate=True
    )

    resultado = await scraper.scrape_collection_by_year(page=mock_page, year=2026, done_links=set())

    assert resultado == 3
    mocks["go_next_page"].assert_not_called()  # parou por duplicado, nunca tentou próxima página


@pytest.mark.asyncio
async def test_scrape_collection_by_year_para_quando_go_next_page_devolve_false(monkeypatch, mock_page):
    mocks = _mock_all_steps(
        monkeypatch,
        scrape_items_from_page=AsyncMock(return_value=(5, 0, False)),
        go_next_page=AsyncMock(return_value=False),
    )

    resultado = await scraper.scrape_collection_by_year(page=mock_page, year=2026, done_links=set())

    assert resultado == 5
    assert mocks["scrape_items_from_page"].call_count == 1  # só correu uma vez, depois parou


@pytest.mark.asyncio
async def test_scrape_collection_by_year_grava_batch_quando_atinge_batch_size(monkeypatch, mock_page):
    """Confirma save_to_rotating_file é chamado quando len(batch) >= BATCH_SIZE."""
    original_batch_size = scraper.BATCH_SIZE
    monkeypatch.setattr(scraper, "BATCH_SIZE", 2)

    def fake_scrape_items(page, year, done_links, batch, items_skipped, page_count, force_full):
        # simula adicionar itens directamente ao batch (mutado in place, como a função real faz)
        batch[f"https://x/{page_count}-a"] = {"titulo": "a"}
        batch[f"https://x/{page_count}-b"] = {"titulo": "b"}
        return 2, items_skipped, False

    async def async_fake_scrape_items(*args, **kwargs):
        return fake_scrape_items(*args, **kwargs)

    mocks = _mock_all_steps(
        monkeypatch,
        scrape_items_from_page=AsyncMock(side_effect=async_fake_scrape_items),
        go_next_page=AsyncMock(return_value=False),
    )

    resultado = await scraper.scrape_collection_by_year(page=mock_page, year=2026, done_links=set())

    assert resultado == 2
    mocks["save_to_rotating_file"].assert_called_once()


@pytest.mark.asyncio
async def test_scrape_collection_by_year_grava_batch_remanescente_no_final(monkeypatch, mock_page):
    """Confirma que itens que não chegaram a BATCH_SIZE são gravados no fim (fora do loop)."""
    monkeypatch.setattr(scraper, "BATCH_SIZE", 1000)  # nunca atinge dentro do loop

    def fake_scrape_items(page, year, done_links, batch, items_skipped, page_count, force_full):
        batch["https://x/1"] = {"titulo": "único item"}
        return 1, items_skipped, False

    async def async_fake_scrape_items(*args, **kwargs):
        return fake_scrape_items(*args, **kwargs)

    mocks = _mock_all_steps(
        monkeypatch,
        scrape_items_from_page=AsyncMock(side_effect=async_fake_scrape_items),
        go_next_page=AsyncMock(return_value=False),
    )

    resultado = await scraper.scrape_collection_by_year(page=mock_page, year=2026, done_links=set())

    assert resultado == 1
    mocks["save_to_rotating_file"].assert_called_once()
    chamada_args = mocks["save_to_rotating_file"].call_args[0][0]
    assert "https://x/1" in chamada_args


@pytest.mark.asyncio
async def test_scrape_collection_by_year_done_links_atualizado_apos_grava_batch(monkeypatch, mock_page):
    monkeypatch.setattr(scraper, "BATCH_SIZE", 1)

    def fake_scrape_items(page, year, done_links, batch, items_skipped, page_count, force_full):
        batch["https://x/1"] = {"titulo": "item"}
        return 1, items_skipped, False

    async def async_fake_scrape_items(*args, **kwargs):
        return fake_scrape_items(*args, **kwargs)

    mocks = _mock_all_steps(
        monkeypatch,
        scrape_items_from_page=AsyncMock(side_effect=async_fake_scrape_items),
        go_next_page=AsyncMock(return_value=False),
    )

    done_links = set()
    await scraper.scrape_collection_by_year(page=mock_page, year=2026, done_links=done_links)

    assert "https://x/1" in done_links