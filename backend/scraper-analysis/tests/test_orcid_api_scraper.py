import time
import threading
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, MagicMock
import orcid_api_scraper as scraper

def test_carregar_investigadores_path_nao_existe():
    mock_path = MagicMock(spec=Path)
    mock_path.exists.return_value = False

    resultado = scraper.carregar_investigadores_de_docentes(mock_path)

    assert resultado == []

def test_carregar_investigadores_com_orcid_valido():
    dados_mock = {
        "Test User": {
            "ORCID": {"link": "https://orcid.org/test-orcid-id"}
        }
    }

    mock_path = MagicMock(spec=Path)
    mock_path.exists.return_value = True

    with patch("orcid_api_scraper.load_existing_data", return_value=dados_mock):
        resultado = scraper.carregar_investigadores_de_docentes(mock_path)

    assert resultado == [{"nome": "Test User", "id": "test-orcid-id"}]

def test_carregar_investigadores_link_com_barra_final():
    dados_mock = {
        "Test User": {
            "ORCID": {"link": "https://orcid.org/test-orcid-id/"}
        }
    }

    mock_path = MagicMock(spec=Path)
    mock_path.exists.return_value = True

    with patch("orcid_api_scraper.load_existing_data", return_value=dados_mock):
        resultado = scraper.carregar_investigadores_de_docentes(mock_path)

    assert resultado == [{"nome": "Test User", "id": "test-orcid-id"}]

def test_carregar_investigadores_sem_chave_orcid():
    dados_mock = {
        "Test User": {"outra_info": "something"}
    }

    mock_path = MagicMock(spec=Path)
    mock_path.exists.return_value = True

    with patch("orcid_api_scraper.load_existing_data", return_value=dados_mock):
        resultado = scraper.carregar_investigadores_de_docentes(mock_path)

    assert resultado == []

def test_carregar_investigadores_orcid_nao_e_dict():
    dados_mock = {
        "Test User": {"ORCID": "nao e um dict"}
    }

    mock_path = MagicMock(spec=Path)
    mock_path.exists.return_value = True

    with patch("orcid_api_scraper.load_existing_data", return_value=dados_mock):
        resultado = scraper.carregar_investigadores_de_docentes(mock_path)

    assert resultado == []

def test_carregar_investigadores_sem_link():
    dados_mock = {
        "Test User": {"ORCID": {}}
    }

    mock_path = MagicMock(spec=Path)
    mock_path.exists.return_value = True

    with patch("orcid_api_scraper.load_existing_data", return_value=dados_mock):
        resultado = scraper.carregar_investigadores_de_docentes(mock_path)

    assert resultado == []

def test_carregar_investigadores_info_nao_e_dict():
    dados_mock = {
        "Test User": "nao e um dict"
    }

    mock_path = MagicMock(spec=Path)
    mock_path.exists.return_value = True

    with patch("orcid_api_scraper.load_existing_data", return_value=dados_mock):
        resultado = scraper.carregar_investigadores_de_docentes(mock_path)

    assert resultado == []

def test_carregar_investigadores_multiplos_docentes():
    dados_mock = {
        "Test User": {"ORCID": {"link": "https://orcid.org/test-orcid-id"}},
        "Another User": {"ORCID": {"link": "https://orcid.org/another-orcid-id"}},
        "User Without Orcid": {"outra_info": "bla"}
    }

    mock_path = MagicMock(spec=Path)
    mock_path.exists.return_value = True

    with patch("orcid_api_scraper.load_existing_data", return_value=dados_mock):
        resultado = scraper.carregar_investigadores_de_docentes(mock_path)

    assert len(resultado) == 2
    nomes = [d["nome"] for d in resultado]
    assert "Test User" in nomes
    assert "Another User" in nomes
    assert "User Without Orcid" not in nomes

def _base_summary(date_obj=None, titulo="Projeto X", tipo="contract", organizacao="ISEL"):
    return {
        "title": {"title": {"value": titulo}},
        "type": tipo,
        "organization": {"name": organizacao},
        "end-date": date_obj
    }

def test_extract_funding_info_data_completa():
    summary = _base_summary(date_obj={
        "year": {"value": "2023"},
        "month": {"value": "09"},
        "day": {"value": "15"}
    })
    docente = {"nome": "Test User", "id": "test-orcid-id"}

    resultado = scraper.extract_funding_info(summary, docente)

    assert resultado["titulo"] == "Projeto X"
    assert resultado["link"] == "https://orcid.org/test-orcid-id"
    assert resultado["autores"] == "Test User"
    assert resultado["texto"] == ""
    assert resultado["dataPublicacao"] == "2023-09-15"
    assert resultado["tipo"] == "contract"
    assert resultado["organizacao"] == "ISEL"
    assert resultado["origem"] == "Orcid"
    assert "dateChecked" in resultado

def test_extract_funding_info_so_ano_e_mes():
    summary = _base_summary(date_obj={
        "year": {"value": "2023"},
        "month": {"value": "09"},
        "day": None
    })
    docente = {"nome": "Test User", "id": "test-orcid-id"}

    resultado = scraper.extract_funding_info(summary, docente)
    assert resultado["dataPublicacao"] == "2023-09"

def test_extract_funding_info_so_ano():
    summary = _base_summary(date_obj={
        "year": {"value": "2023"},
        "month": None,
        "day": None
    })
    docente = {"nome": "Test User", "id": "test-orcid-id"}

    resultado = scraper.extract_funding_info(summary, docente)
    assert resultado["dataPublicacao"] == "2023"

def test_extract_funding_info_sem_data():
    summary = _base_summary(date_obj=None)
    docente = {"nome": "Test User", "id": "test-orcid-id"}

    resultado = scraper.extract_funding_info(summary, docente)
    assert resultado["dataPublicacao"] == "0000-00-00"

def test_extract_funding_info_dateChecked_usa_datetime_now():
    summary = _base_summary(date_obj=None)
    docente = {"nome": "Test User", "id": "test-orcid-id"}

    fake_now = datetime(2026, 7, 10, 18, 0, 0)
    with patch("orcid_api_scraper.datetime") as mock_datetime:
        mock_datetime.now.return_value = fake_now
        resultado = scraper.extract_funding_info(summary, docente)
    assert resultado["dateChecked"] == fake_now.isoformat()


def test_rate_limiter_permite_ate_ao_limite_sem_dormir():
    limiter = scraper.RateLimiter(max_calls=5, period=1.0)

    with patch("time.sleep") as mock_sleep:
        for _ in range(5):
            limiter.acquire()

    mock_sleep.assert_not_called()
    assert len(limiter.calls) == 5

def test_rate_limiter_dorme_quando_excede_limite():
    limiter = scraper.RateLimiter(max_calls=2, period=1.0)

    with patch("time.sleep") as mock_sleep:
        limiter.acquire()
        limiter.acquire()
        limiter.acquire()  # esta deve disparar sleep
    mock_sleep.assert_called_once()
    sleep_arg = mock_sleep.call_args[0][0]
    assert sleep_arg > 0

def test_rate_limiter_limpa_chamadas_antigas():
    limiter = scraper.RateLimiter(max_calls=2, period=0.1)

    limiter.acquire()
    limiter.acquire()
    time.sleep(0.15)  # deixa o período expirar

    with patch("time.sleep") as mock_sleep:
        limiter.acquire()
    mock_sleep.assert_not_called()
    assert len(limiter.calls) == 1

def test_rate_limiter_thread_safe():
    limiter = scraper.RateLimiter(max_calls=100, period=1.0)
    resultados = []

    def worker():
        limiter.acquire()
        resultados.append(1)
    threads = [threading.Thread(target=worker) for _ in range(20)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert len(resultados) == 20
    assert len(limiter.calls) == 20

def _fundings_data_mock(groups):
    full_data = {"group": groups}
    return (["placeholder"], full_data)

def test_processar_docente_sucesso_com_filtros():
    docente = {"nome": "Test User", "id": "test-orcid-id"}

    groups = [
        {"funding-summary": [_base_summary(
            date_obj={"year": {"value": "2024"}, "month": None, "day": None},
            titulo="Projeto Válido",
            organizacao="ISEL"
        )]},
        {"funding-summary": [_base_summary(
            date_obj={"year": {"value": "2024"}, "month": None, "day": None},
            titulo="Projeto Organizacao Errada",
            organizacao="OUTRA"
        )]},
        {"funding-summary": [_base_summary(
            date_obj={"year": {"value": "2010"}, "month": None, "day": None},
            titulo="Projeto Antigo",
            organizacao="ISEL"
        )]},
    ]

    mock_orcid_instance = MagicMock()
    mock_orcid_instance.fundings.return_value = _fundings_data_mock(groups)

    with patch("orcid_api_scraper.rate_limiter") as mock_limiter, \
         patch("orcid_api_scraper.Orcid", return_value=mock_orcid_instance), \
         patch("orcid_api_scraper.ESCOLAS", ["ISEL"]), \
         patch("orcid_api_scraper.PRESENT_YEAR", 2026):
        resultado = scraper.processar_docente(docente, "fake_token")

    mock_limiter.acquire.assert_called_once()
    assert len(resultado) == 1
    assert resultado[0]["titulo"] == "Projeto Válido"


def test_processar_docente_erro_ao_criar_orcid():
    docente = {"nome": "Test User", "id": "test-orcid-id"}

    with patch("orcid_api_scraper.rate_limiter") as mock_limiter, \
         patch("orcid_api_scraper.Orcid", side_effect=Exception("erro de auth")):
        resultado = scraper.processar_docente(docente, "fake_token")

    mock_limiter.acquire.assert_called_once()
    assert resultado == []


def test_processar_docente_sem_fundings():
    docente = {"nome": "Test User", "id": "test-orcid-id"}

    mock_orcid_instance = MagicMock()
    mock_orcid_instance.fundings.return_value = _fundings_data_mock([])

    with patch("orcid_api_scraper.rate_limiter"), \
         patch("orcid_api_scraper.Orcid", return_value=mock_orcid_instance), \
         patch("orcid_api_scraper.ESCOLAS", ["ISEL"]), \
         patch("orcid_api_scraper.PRESENT_YEAR", 2026):
        resultado = scraper.processar_docente(docente, "fake_token")

    assert resultado == []

def test_processar_docente_multiplos_summaries_por_grupo_pega_so_primeiro():
    docente = {"nome": "Test User", "id": "test-orcid-id"}

    groups = [
        {"funding-summary": [
            _base_summary(date_obj={"year": {"value": "2024"}, "month": None, "day": None},
                          titulo="Primeira Fonte", organizacao="ISEL"),
            _base_summary(date_obj={"year": {"value": "2024"}, "month": None, "day": None},
                          titulo="Segunda Fonte", organizacao="ISEL"),
        ]},
    ]

    mock_orcid_instance = MagicMock()
    mock_orcid_instance.fundings.return_value = _fundings_data_mock(groups)

    with patch("orcid_api_scraper.rate_limiter"), \
         patch("orcid_api_scraper.Orcid", return_value=mock_orcid_instance), \
         patch("orcid_api_scraper.ESCOLAS", ["ISEL"]), \
         patch("orcid_api_scraper.PRESENT_YEAR", 2026):
        resultado = scraper.processar_docente(docente, "fake_token")

    assert len(resultado) == 1
    assert resultado[0]["titulo"] == "Primeira Fonte"