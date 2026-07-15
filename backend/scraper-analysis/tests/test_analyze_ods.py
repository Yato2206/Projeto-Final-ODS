import analyze_ods as analyze_ods
from unittest.mock import patch, MagicMock, AsyncMock, mock_open
import asyncio
import pytest
from pathlib import Path
import json
from urllib.error import HTTPError
from datetime import datetime

def test_preprocessar_texto_vazio():
    assert analyze_ods.preprocessar_texto("") == ""

def test_preprocessar_texto_none():
    assert analyze_ods.preprocessar_texto(None) == ""

def test_preprocessar_texto_lowercase():
    resultado = analyze_ods.preprocessar_texto("TEXTO EM MAIÚSCULAS")
    assert resultado == resultado.lower()

def test_preprocessar_texto_remove_pontuacao():
    resultado = analyze_ods.preprocessar_texto("olá, mundo! como estás?")
    assert "," not in resultado
    assert "!" not in resultado
    assert "?" not in resultado

def test_preprocessar_texto_tokeniza_palavras():
    resultado = analyze_ods.preprocessar_texto("machine learning")
    assert "machine" in resultado
    assert "learning" in resultado

def test_preprocessar_texto_texto_normal():
    resultado = analyze_ods.preprocessar_texto("Investigação em Inteligência Artificial")
    assert "investigação" in resultado
    assert "inteligência" in resultado
    assert "artificial" in resultado

def test_preprocessar_texto_so_pontuacao():
    resultado = analyze_ods.preprocessar_texto("!!! ??? ,,, ...")
    assert resultado.strip() == ""

def test_preprocessar_texto_numeros_preservados():
    resultado = analyze_ods.preprocessar_texto("versão 2026")
    assert "2026" in resultado

def test_preprocessar_texto_devolve_string():
    resultado = analyze_ods.preprocessar_texto("qualquer texto")
    assert isinstance(resultado, str)

@pytest.mark.parametrize("texto, esperado_contem", [
    ("Machine Learning", ["machine", "learning"]),
    ("olá MUNDO!", ["olá", "mundo"]),
    ("texto, com. pontuação!", ["texto", "com", "pontuação"]),
])
def test_preprocessar_texto_parametrizado(texto, esperado_contem):
    resultado = analyze_ods.preprocessar_texto(texto)
    for palavra in esperado_contem:
        assert palavra in resultado

@pytest.mark.parametrize("texto_simulado, esperado_uoa, esperado_hk", [
    (#MATCH
        "sustentabilidade reciclagem oceano", 
        {"ODS12": 1, "ODS14": 1},  
        {"ODS13": 1}             
    ),
    (#NO MATCH
        "computador teclado rato", 
        {}, 
        {}
    )
])
def test_classificar_ods(monkeypatch, tmp_path, texto_simulado, esperado_uoa, esperado_hk):
    monkeypatch.setattr(analyze_ods, "BASE_DIR", str(tmp_path))
    taxo_dir = tmp_path / "taxonomies"
    taxo_dir.mkdir(parents=True, exist_ok=True)

    taxo_uoa_data = {
        "ODS12": ["sustentabilidade", "consumo"],
        "ODS14": ["oceano", "mar"]
    }
    taxo_hk_data = {
        "ODS13": ["reciclagem", "clima"]
    }
    
    (taxo_dir / "taxo_UoA.json").write_text(json.dumps(taxo_uoa_data), encoding="utf-8")
    (taxo_dir / "taxo_HK.json").write_text(json.dumps(taxo_hk_data), encoding="utf-8")

    with patch("analyze_ods.preprocessar_texto", side_effect=lambda x: x.lower()):
        resultado = analyze_ods.classificar_ods(
            titulo="Título de Teste", 
            texto_conteudo=texto_simulado
        )

    assert resultado["UoA"] == esperado_uoa
    assert resultado["HK"] == esperado_hk

def test_classificar_ods_match_palavra_exata(monkeypatch, tmp_path):
    monkeypatch.setattr(analyze_ods, "BASE_DIR", str(tmp_path))
    taxo_dir = tmp_path / "taxonomies"
    taxo_dir.mkdir(parents=True, exist_ok=True)

    (taxo_dir / "taxo_UoA.json").write_text(json.dumps({"ODS13": ["clima"]}), encoding="utf-8")
    (taxo_dir / "taxo_HK.json").write_text(json.dumps({}), encoding="utf-8")

    texto_com_substring = "o evento climatérico foi intenso"

    with patch("analyze_ods.preprocessar_texto", side_effect=lambda x: x.lower()):
        resultado = analyze_ods.classificar_ods(titulo="", texto_conteudo=texto_com_substring)

    assert resultado["UoA"] == {}