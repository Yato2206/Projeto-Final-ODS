from unittest.mock import patch, MagicMock, AsyncMock
import asyncio
import aiohttp
import pytest
from pathlib import Path
import json
import utilis as utilis
from urllib.error import HTTPError
from datetime import datetime

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