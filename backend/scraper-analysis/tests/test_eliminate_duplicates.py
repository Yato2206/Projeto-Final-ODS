import pytest
from datetime import datetime
import eliminate_duplicates 

def test_remove_duplicates_cursos_ignorados_e_mantidos():
    dados_entrada = {
        "https/curso1": {
            "titulo": "Curso de Python",
            "texto": "Aprenda Python do zero."
        },
        "https/artigo1": {
            "titulo": "Artigo Científico A",
            "dataPublicacao": "2026-01-01",
            "dateChecked": "2026-07-04T12:00:00Z"
        }
    }
    
    resultado = eliminate_duplicates.remove_duplicates(dados_entrada)
    
    assert "https/curso1" in resultado
    assert "https/artigo1" in resultado
    assert resultado["https/curso1"]["titulo"] == "Curso de Python"

def test_remove_duplicates_substitui_por_data_publicacao_mais_recente():
    dados_entrada = {
        "https/artigo_velho": {
            "titulo": "Mesmo Titulo",
            "dataPublicacao": "2025-01-01",
            "dateChecked": "2026-07-04T12:00:00Z"
        },
        "https/artigo_novo": {
            "titulo": "Mesmo Titulo",
            "dataPublicacao": "2026-01-01",
            "dateChecked": "2026-07-04T12:00:00Z"
        }
    }
    
    resultado = eliminate_duplicates.remove_duplicates(dados_entrada)
    
    assert len(resultado) == 1
    assert "https/artigo_novo" in resultado
    assert "https/artigo_velho" not in resultado

def test_remove_duplicates_substitui_por_data_publicacao_mais_recente_versao_dataPublicacao_so_com_ano():
    dados_entrada = {
        "https/artigo_velho": {
            "titulo": "Mesmo Titulo",
            "dataPublicacao": "2026",
            "dateChecked": "2026-07-04T12:00:00Z"
        },
        "https/artigo_novo": {
            "titulo": "Mesmo Titulo",
            "dataPublicacao": "2026-01-01",
            "dateChecked": "2026-07-04T12:00:00Z"
        }
    }
    
    resultado = eliminate_duplicates.remove_duplicates(dados_entrada)
    
    assert len(resultado) == 1
    assert "https/artigo_novo" in resultado
    assert "https/artigo_velho" not in resultado


def test_remove_duplicates_mesma_publicacao_substitui_por_date_checked():
    dados_entrada = {
        "https/checado_primeiro": {
            "titulo": "Artigo Duplicado",
            "dataPublicacao": "2026-01-01",
            "dateChecked": "2026-07-04T10:00:00Z"
        },
        "https/checado_depois": {
            "titulo": "Artigo Duplicado",
            "dataPublicacao": "2026-01-01",
            "dateChecked": "2026-07-04T18:00:00Z"
        }
    }
    
    resultado = eliminate_duplicates.remove_duplicates(dados_entrada)
    
    assert len(resultado) == 1
    assert "https/checado_depois" in resultado
    assert resultado["https/checado_depois"]["dateChecked"] == "2026-07-04T18:00:00Z"

def test_remove_duplicates_mantem_primeiro_se_existente_for_mais_recente():
    dados_entrada = {
        "https/vencedor": {
            "titulo": "Titulo Unico",
            "dataPublicacao": "2026-01-01",
            "dateChecked": "2026-07-05T00:00:00Z"
        },
        "https/perdedor": {
            "titulo": "Titulo Unico",
            "dataPublicacao": "2026-01-01",
            "dateChecked": "2026-07-01T00:00:00Z"
        }
    }
    
    resultado = eliminate_duplicates.remove_duplicates(dados_entrada)
    assert len(resultado) == 1
    assert "https/vencedor" in resultado

def test_remove_duplicates_vazio():
    resultado = eliminate_duplicates.remove_duplicates({})
    assert resultado == {}