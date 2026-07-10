import format_documents as formatDocuments
from unittest.mock import patch, MagicMock, AsyncMock, mock_open
import asyncio
import pytest
from pathlib import Path
import json
from urllib.error import HTTPError
from datetime import datetime
from bs4 import BeautifulSoup

def test_format_newsletter_documents_without_noticias():
    conteudo_mock = {
        "Newsletter: Test": 
            {
                "titulo": "Newsletter: Test",
                "link": "https://www.ipl.pt/newsletter/test",
                "politecnicoTitulo": "Notícias TESTE",
                "politecnicoTexto": "Este é um texto de teste para a newsletter.",
                "noticias": [],
                "dataPublicacao": "2026-06-06",
                "tipo": "Newsletter",
                "dateChecked": "2026-06-28T20:26:53.108757"
            }
    }
    with patch("pathlib.Path.exists", return_value=True), \
         patch("builtins.open", mock_open(read_data="{}")), \
         patch("format_documents.json.load", return_value=conteudo_mock):
            resultado = formatDocuments.format_newsletter_documents()
    assert len(resultado) == 1
    assert "https://www.ipl.pt/newsletter/test" in resultado
    assert resultado["https://www.ipl.pt/newsletter/test"]["titulo"] == "Notícias TESTE"
    assert resultado["https://www.ipl.pt/newsletter/test"]["autores"] == "Autor Desconhecido"
    assert resultado["https://www.ipl.pt/newsletter/test"]["texto"] == "Este é um texto de teste para a newsletter."
    assert resultado["https://www.ipl.pt/newsletter/test"]["dataPublicacao"] == "2026-06-06"
    assert resultado["https://www.ipl.pt/newsletter/test"]["tipo"] == "Newsletter"
    assert resultado["https://www.ipl.pt/newsletter/test"]["dateChecked"] == "2026-06-28T20:26:53.108757"
    assert resultado["https://www.ipl.pt/newsletter/test"]["origem"] == "Newsletter"

def test_format_newsletter_documents_with_one_noticias():
    conteudo_mock = {
        "Newsletter: Test": 
            {
                "titulo": "Newsletter: Test",
                "link": "https://www.ipl.pt/newsletter/test",
                "politecnicoTitulo": "Notícias TESTE",
                "politecnicoTexto": "Este é um texto de teste para a newsletter.",
                "noticias": [
                    {
                        "titulo": "Notícia 1",
                        "texto": "Texto da notícia 1"
                    }
                ],
                "dataPublicacao": "2026-06-06",
                "tipo": "Newsletter",
                "dateChecked": "2026-06-28T20:26:53.108757"
            }
    }
    with patch("pathlib.Path.exists", return_value=True), \
         patch("builtins.open", mock_open(read_data="{}")), \
         patch("format_documents.json.load", return_value=conteudo_mock):
            resultado = formatDocuments.format_newsletter_documents()
    assert len(resultado) == 2
    assert "https://www.ipl.pt/newsletter/test" in resultado
    assert resultado["https://www.ipl.pt/newsletter/test"]["titulo"] == "Notícias TESTE"
    assert resultado["https://www.ipl.pt/newsletter/test"]["autores"] == "Autor Desconhecido"
    assert resultado["https://www.ipl.pt/newsletter/test"]["texto"] == "Este é um texto de teste para a newsletter."
    assert resultado["https://www.ipl.pt/newsletter/test"]["dataPublicacao"] == "2026-06-06"
    assert resultado["https://www.ipl.pt/newsletter/test"]["tipo"] == "Newsletter"
    assert resultado["https://www.ipl.pt/newsletter/test"]["dateChecked"] == "2026-06-28T20:26:53.108757"
    assert resultado["https://www.ipl.pt/newsletter/test"]["origem"] == "Newsletter"
    assert "https://www.ipl.pt/newsletter/test#noticia-0" in resultado
    assert resultado["https://www.ipl.pt/newsletter/test#noticia-0"]["titulo"] == "Notícia 1"
    assert resultado["https://www.ipl.pt/newsletter/test#noticia-0"]["autores"] == "Autor Desconhecido"
    assert resultado["https://www.ipl.pt/newsletter/test#noticia-0"]["texto"] == "Texto da notícia 1"
    assert resultado["https://www.ipl.pt/newsletter/test#noticia-0"]["dataPublicacao"] == "2026-06-06"
    assert resultado["https://www.ipl.pt/newsletter/test#noticia-0"]["tipo"] == "Noticia da Newsletter"
    assert resultado["https://www.ipl.pt/newsletter/test#noticia-0"]["dateChecked"] == "2026-06-28T20:26:53.108757"
    assert resultado["https://www.ipl.pt/newsletter/test#noticia-0"]["origem"] == "Newsletter"


def test_format_newsletter_documents_with_more_than_one_noticias():
    conteudo_mock = {
        "Newsletter: Test": 
            {
                "titulo": "Newsletter: Test",
                "link": "https://www.ipl.pt/newsletter/test",
                "politecnicoTitulo": "Notícias TESTE",
                "politecnicoTexto": "Este é um texto de teste para a newsletter.",
                "noticias": [
                    {
                        "titulo": "Notícia 1",
                        "texto": "Texto da notícia 1"
                    },
                    {
                        "titulo": "Notícia 2",
                        "texto": "Texto da notícia 2"
                    }
                ],
                "dataPublicacao": "2026-06-06",
                "tipo": "Newsletter",
                "dateChecked": "2026-06-28T20:26:53.108757"
            }
    }
    with patch("pathlib.Path.exists", return_value=True), \
         patch("builtins.open", mock_open(read_data="{}")), \
         patch("format_documents.json.load", return_value=conteudo_mock):
            resultado = formatDocuments.format_newsletter_documents()
    assert len(resultado) == 3
    assert "https://www.ipl.pt/newsletter/test" in resultado
    assert resultado["https://www.ipl.pt/newsletter/test"]["titulo"] == "Notícias TESTE"
    assert resultado["https://www.ipl.pt/newsletter/test"]["autores"] == "Autor Desconhecido"
    assert resultado["https://www.ipl.pt/newsletter/test"]["texto"] == "Este é um texto de teste para a newsletter."
    assert resultado["https://www.ipl.pt/newsletter/test"]["dataPublicacao"] == "2026-06-06"
    assert resultado["https://www.ipl.pt/newsletter/test"]["tipo"] == "Newsletter"
    assert resultado["https://www.ipl.pt/newsletter/test"]["dateChecked"] == "2026-06-28T20:26:53.108757"
    assert resultado["https://www.ipl.pt/newsletter/test"]["origem"] == "Newsletter"
    assert "https://www.ipl.pt/newsletter/test#noticia-0" in resultado
    assert resultado["https://www.ipl.pt/newsletter/test#noticia-0"]["titulo"] == "Notícia 1"
    assert resultado["https://www.ipl.pt/newsletter/test#noticia-0"]["autores"] == "Autor Desconhecido"
    assert resultado["https://www.ipl.pt/newsletter/test#noticia-0"]["texto"] == "Texto da notícia 1"
    assert resultado["https://www.ipl.pt/newsletter/test#noticia-0"]["dataPublicacao"] == "2026-06-06"
    assert resultado["https://www.ipl.pt/newsletter/test#noticia-0"]["tipo"] == "Noticia da Newsletter"
    assert resultado["https://www.ipl.pt/newsletter/test#noticia-0"]["dateChecked"] == "2026-06-28T20:26:53.108757"
    assert resultado["https://www.ipl.pt/newsletter/test#noticia-0"]["origem"] == "Newsletter"
    assert "https://www.ipl.pt/newsletter/test#noticia-1" in resultado
    assert resultado["https://www.ipl.pt/newsletter/test#noticia-1"]["titulo"] == "Notícia 2"
    assert resultado["https://www.ipl.pt/newsletter/test#noticia-1"]["autores"] == "Autor Desconhecido"
    assert resultado["https://www.ipl.pt/newsletter/test#noticia-1"]["texto"] == "Texto da notícia 2"
    assert resultado["https://www.ipl.pt/newsletter/test#noticia-1"]["dataPublicacao"] == "2026-06-06"
    assert resultado["https://www.ipl.pt/newsletter/test#noticia-1"]["tipo"] == "Noticia da Newsletter"
    assert resultado["https://www.ipl.pt/newsletter/test#noticia-1"]["dateChecked"] == "2026-06-28T20:26:53.108757"
    assert resultado["https://www.ipl.pt/newsletter/test#noticia-1"]["origem"] == "Newsletter"

def test_format_newsletter_documents_skip_no_text():
    conteudo_mock = {
        "Newsletter: Test": 
            {
                "titulo": "Newsletter: Test",
                "link": "https://www.ipl.pt/newsletter/test",
                "politecnicoTitulo": "Notícias TESTE",
                "noticias": [],
                "dataPublicacao": "2026-06-06",
                "tipo": "Newsletter",
                "dateChecked": "2026-06-28T20:26:53.108757"
            }
    }
    with patch("pathlib.Path.exists", return_value=True), \
         patch("builtins.open", mock_open(read_data="{}")), \
         patch("format_documents.json.load", return_value=conteudo_mock):
        resultado = formatDocuments.format_newsletter_documents()
    assert len(resultado) == 0

def test_format_scientific_repo_documents():
    conteudo_mock = {
        "https://repositorio.ipl.pt/test": {
            "titulo": "Repo Test",
            "autores": "Autor 1, Autor 2",
            "texto": "Texto que descreve o documento.",
            "dataPublicacao": "2026-06-06",
            "tipo": "tipo Teste",
            "acesso": "Acesso aberto",
            "dateChecked": "2026-06-28T20:26:53.108757"
        }
    }

    with patch("glob.glob", return_value=["repo_cientifico/repo_cientifico_1.json"]), \
         patch("builtins.open", mock_open(read_data="{}")), \
         patch("format_documents.json.load", return_value=conteudo_mock):
        resultado = formatDocuments.format_scientific_repo_documents()
    assert len(resultado) == 1
    assert "https://repositorio.ipl.pt/test" in resultado
    assert resultado["https://repositorio.ipl.pt/test"]["titulo"] == "Repo Test"
    assert resultado["https://repositorio.ipl.pt/test"]["autores"] == "Autor 1, Autor 2"
    assert resultado["https://repositorio.ipl.pt/test"]["texto"] == "Texto que descreve o documento."
    assert resultado["https://repositorio.ipl.pt/test"]["dataPublicacao"] == "2026-06-06"
    assert resultado["https://repositorio.ipl.pt/test"]["tipo"] == "tipo Teste"
    assert resultado["https://repositorio.ipl.pt/test"]["dateChecked"] == "2026-06-28T20:26:53.108757"
    assert resultado["https://repositorio.ipl.pt/test"]["origem"] == "Repositório Científico"

def test_format_scientific_repo_documents_skip_no_text():
    conteudo_mock = {
        "https://repositorio.ipl.pt/test": {
            "titulo": "Repo Test",
            "autores": "Autor 1, Autor 2",
            "dataPublicacao": "2026-06-06",
            "tipo": "tipo Teste",
            "acesso": "Acesso aberto",
            "dateChecked": "2026-06-28T20:26:53.108757"
        }
    }

    with patch("glob.glob", return_value=["repo_cientifico/repo_cientifico_1.json"]), \
         patch("builtins.open", mock_open(read_data="{}")), \
         patch("format_documents.json.load", return_value=conteudo_mock):
        resultado = formatDocuments.format_scientific_repo_documents()
    assert len(resultado) == 0

def test_format_orcid():
    conteudo_mock = {
        "Titulo Teste": {
            "titulo": "Titulo Teste",
            "link": "https://orcid.org/test",
            "autores": "Autor 1, Autor 2",
            "texto": "Texto do documento.",
            "dataPublicacao": "2026-01-01",
            "tipo": "funding",
            "dateChecked": "2026-06-28T20:26:53.108757",
            "origem": "Orcid"
        }
    }

    mock_file = MagicMock(spec=Path)
    mock_file.name = "docente_1.json"

    mock_orcid_dir = MagicMock(spec=Path)
    mock_orcid_dir.exists.return_value = True
    mock_orcid_dir.glob.return_value = [mock_file]

    with patch("format_documents.DOCUMENTS_DIR") as mock_documents_dir, \
         patch("builtins.open", mock_open(read_data="{}")), \
         patch("format_documents.json.load", return_value=conteudo_mock):
        mock_documents_dir.__truediv__.return_value = mock_orcid_dir
        resultado = formatDocuments.format_orcid()

    assert len(resultado) == 1
    assert "Titulo Teste" in resultado
    assert resultado["Titulo Teste"]["titulo"] == "Titulo Teste"
    assert resultado["Titulo Teste"]["link"] == "https://orcid.org/test"
    assert resultado["Titulo Teste"]["autores"] == "Autor 1, Autor 2"
    assert resultado["Titulo Teste"]["texto"] == "Texto do documento."
    assert resultado["Titulo Teste"]["dataPublicacao"] == "2026-01-01"
    assert resultado["Titulo Teste"]["tipo"] == "funding"
    assert resultado["Titulo Teste"]["dateChecked"] == "2026-06-28T20:26:53.108757"
    assert resultado["Titulo Teste"]["origem"] == "Orcid"

def test_format_orcid_directory_not_found():
    mock_orcid_dir = MagicMock(spec=Path)
    mock_orcid_dir.exists.return_value = False

    with patch("format_documents.DOCUMENTS_DIR") as mock_documents_dir:
        mock_documents_dir.__truediv__.return_value = mock_orcid_dir
        resultado = formatDocuments.format_orcid()

    assert resultado == {}

def test_format_orcid_no_files_found():
    mock_orcid_dir = MagicMock(spec=Path)
    mock_orcid_dir.exists.return_value = True
    mock_orcid_dir.glob.return_value = []

    with patch("format_documents.DOCUMENTS_DIR") as mock_documents_dir:
        mock_documents_dir.__truediv__.return_value = mock_orcid_dir
        resultado = formatDocuments.format_orcid()

    assert resultado == {}

def test_format_orcid_skip_non_dict_entries():
    conteudo_mock = {
        "Titulo Valido": {
            "titulo": "Titulo Valido",
            "autores": "Autor 1"
        },
        "Entrada Invalida": "isto nao e um dict"
    }

    mock_file = MagicMock(spec=Path)
    mock_file.name = "docente_1.json"

    mock_orcid_dir = MagicMock(spec=Path)
    mock_orcid_dir.exists.return_value = True
    mock_orcid_dir.glob.return_value = [mock_file]

    with patch("format_documents.DOCUMENTS_DIR") as mock_documents_dir, \
         patch("builtins.open", mock_open(read_data="{}")), \
         patch("format_documents.json.load", return_value=conteudo_mock):
        mock_documents_dir.__truediv__.return_value = mock_orcid_dir
        resultado = formatDocuments.format_orcid()

    assert len(resultado) == 1
    assert "Titulo Valido" in resultado
    assert "Entrada Invalida" not in resultado

def test_format_orcid_skip_empty_titulo():
    conteudo_mock = {
        "Chave Qualquer": {
            "titulo": "",
            "autores": "Autor 1"
        }
    }

    mock_file = MagicMock(spec=Path)
    mock_file.name = "docente_1.json"

    mock_orcid_dir = MagicMock(spec=Path)
    mock_orcid_dir.exists.return_value = True
    mock_orcid_dir.glob.return_value = [mock_file]

    with patch("format_documents.DOCUMENTS_DIR") as mock_documents_dir, \
         patch("builtins.open", mock_open(read_data="{}")), \
         patch("format_documents.json.load", return_value=conteudo_mock):
        mock_documents_dir.__truediv__.return_value = mock_orcid_dir
        resultado = formatDocuments.format_orcid()

    assert len(resultado) == 0

def test_format_orcid_fallback_titulo_to_key():
    conteudo_mock = {
        "Chave Como Titulo": {
            "autores": "Autor 1"
        }
    }

    mock_file = MagicMock(spec=Path)
    mock_file.name = "docente_1.json"

    mock_orcid_dir = MagicMock(spec=Path)
    mock_orcid_dir.exists.return_value = True
    mock_orcid_dir.glob.return_value = [mock_file]

    with patch("format_documents.DOCUMENTS_DIR") as mock_documents_dir, \
         patch("builtins.open", mock_open(read_data="{}")), \
         patch("format_documents.json.load", return_value=conteudo_mock):
        mock_documents_dir.__truediv__.return_value = mock_orcid_dir
        resultado = formatDocuments.format_orcid()

    assert len(resultado) == 1
    assert "Chave Como Titulo" in resultado
    assert resultado["Chave Como Titulo"]["titulo"] == "Chave Como Titulo"

def test_merge_and_save():
    newsletter_docs = {
        "https://www.ipl.pt/newsletter/test": {
            "titulo": "Newsletter: Test",
            "autores": "Autor Desconhecido",
            "texto": "Texto da newsletter de teste.",
            "dataPublicacao": "2026-06-06",
            "tipo": "Newsletter",
            "dateChecked": "2026-06-28T20:26:53.108757",
            "origem": "Newsletter"
        }
    }
    scientific_repo_docs = {
        "https://repositorio.ipl.pt/test": {
            "titulo": "Repo Test",
            "autores": "Autor 1, Autor 2",
            "texto": "Texto que descreve o documento.",
            "dataPublicacao": "2026-06-06",
            "tipo": "tipo Teste",
            "dateChecked": "2026-06-28T20:26:53.108757",
            "origem": "Repositório Científico"
        }
    }
    scopus_docs = {
        "https://www.scopus.com/test": {
            "titulo": "Scopus Test",
            "autores": "Autor A, Autor B",
            "texto": "Texto que descreve o documento Scopus.",
            "dataPublicacao": "2026-06-06",
            "tipo": "tipo Teste",
            "dateChecked": "2026-06-28T20:26:53.108757",
            "origem": "Scopus"
        }
    }
    orcid_docs = {
        "Something": {
            "titulo": "Orcid Test",
            "autores": "Autor X, Autor Y",
            "texto": "Texto que descreve o documento Orcid.",
            "dataPublicacao": "2026-06-06",
            "tipo": "tipo Teste",
            "dateChecked": "2026-06-28T20:26:53.108757",
            "origem": "Orcid"
        }
    }
    cursos_docs = {
        "https://www.ipl.pt/cursos/test": {
            "curso": "Cursos Test",
            "autores": "ISEL",
            "texto": "Texto que descreve o documento de cursos.",
            "tipo": "tipo Teste",
            "dateChecked": "2026-06-28T20:26:53.108757",
            "origem": "ISEL"
        }
    }
    conteudo_mock = {**newsletter_docs, **scientific_repo_docs, **scopus_docs, **orcid_docs, **cursos_docs}
    with patch("builtins.open", mock_open()) as mock_file, \
         patch("pathlib.Path.mkdir", return_value=None):
            resultado = formatDocuments.merge_and_save(newsletter_docs, scientific_repo_docs, scopus_docs, orcid_docs, cursos_docs)
    assert len(resultado) == 5

def test_parse_args_com_diretorias_extra():
    argumentos_falsos = [
        "script.py", 
        "--extra-dir", "pasta/extra1", 
        "--extra-dir", "pasta/extra2"
    ]

    with patch("sys.argv", argumentos_falsos):
        args = formatDocuments.parse_args()
    assert args.extra_dir == ["pasta/extra1", "pasta/extra2"]


def test_parse_args_default_vazio():
    argumentos_falsos = ["script.py"]

    with patch("sys.argv", argumentos_falsos):
        args = formatDocuments.parse_args()