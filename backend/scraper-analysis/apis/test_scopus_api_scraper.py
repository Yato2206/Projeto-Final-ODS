from unittest.mock import patch, MagicMock
import pytest
from pathlib import Path
import json
import scopus_api_scraper as scraper
import time

#===================================================================================
# TESTES FUNCIONAIS
#===================================================================================

def test_scopus_processar_ano(tmp_path):
    with patch('scopus_api_scraper.ScopusSearch') as mock_search:
        mock_doc = MagicMock()
        mock_doc._asdict.return_value = {
            "eid": "2-s2.0-12345",
            "title": "Test Article A",
            "author_names": "Author A, Author B",
            "description": "This is a test description.",
            "coverDate": "2026-06-06",
            "subtypeDescription": "Test subtype description",
        }
        mock_instance = MagicMock()
        mock_instance.results = [mock_doc]
        mock_search.return_value = mock_instance

        result = scraper.processar_ano(2026, 7, str(tmp_path))

        assert result == 1

def test_processar_ano_conteudo_ficheiro(tmp_path):
    with patch('scopus_api_scraper.ScopusSearch') as mock_search:
        mock_doc = MagicMock()
        mock_doc._asdict.return_value = {
            "eid": "2-s2.0-12345",
            "description": "Texto real",
        }
        mock_search.return_value.results = [mock_doc]

        scraper.processar_ano(2026, 7, str(tmp_path))

        ficheiro = Path(tmp_path) / "scopus_2026_001.json"
        data = json.loads(ficheiro.read_text(encoding="utf-8"))
        assert len(data) == 1
        assert "https://www.scopus.com/pages/publications/2-s2.0-12345" in data

def test_processar_ano_skip_no_eid(tmp_path):
    with patch('scopus_api_scraper.ScopusSearch') as mock_search:
        mock_doc = MagicMock()
        mock_doc._asdict.return_value = {
            "eid": "2-s2.0-12345",
            "description": "Texto real",
        }
        mock_doc2 = MagicMock()
        mock_doc2._asdict.return_value = {
            "eid": None,
            "description": "Texto real",
        }
        mock_search.return_value.results = [mock_doc, mock_doc2]

        scraper.processar_ano(2026, 7, str(tmp_path))

        ficheiro = Path(tmp_path) / "scopus_2026_001.json"
        data = json.loads(ficheiro.read_text(encoding="utf-8"))
        assert len(data) == 1

def test_processar_ano_skip_no_description(tmp_path):
    with patch('scopus_api_scraper.ScopusSearch') as mock_search:
        mock_doc = MagicMock()
        mock_doc._asdict.return_value = {
            "eid": "2-s2.0-12345",
            "description": "Texto real",
        }
        mock_doc2 = MagicMock()
        mock_doc2._asdict.return_value = {
            "eid": "2-s2.0-67890",
        }
        mock_search.return_value.results = [mock_doc, mock_doc2]

        scraper.processar_ano(2026, 7, str(tmp_path))

        ficheiro = Path(tmp_path) / "scopus_2026_001.json"
        data = json.loads(ficheiro.read_text(encoding="utf-8"))
        assert len(data) == 1
#===================================================================================
# TESTES DE BATCHING
#===================================================================================

def test_processar_ano_max_batch_size(tmp_path):
    with patch('scopus_api_scraper.ScopusSearch') as mock_search:
        mock_docs = []
        for i in range(1000): # Create 1000 mock documents
            mock_doc = MagicMock()
            mock_doc._asdict.return_value = {
                "eid": f"2-s2.0-{i}",
                "description": f"Description {i}",
            }
            mock_docs.append(mock_doc)
        mock_search.return_value.results = mock_docs
        scraper.processar_ano(2026, 7, str(tmp_path))
        ficheiro1 = Path(tmp_path) / "scopus_2026_001.json"
        assert ficheiro1.exists()
        data1 = json.loads(ficheiro1.read_text(encoding="utf-8"))
        assert len(data1) == 1000

def test_processar_ano_above_max_batch_size(tmp_path):
    with patch('scopus_api_scraper.ScopusSearch') as mock_search:
        mock_docs = []
        for i in range(1001): # Create 1001 mock documents
            mock_doc = MagicMock()
            mock_doc._asdict.return_value = {
                "eid": f"2-s2.0-{i}",
                "description": f"Description {i}",
            }
            mock_docs.append(mock_doc)
        mock_search.return_value.results = mock_docs
        scraper.processar_ano(2026, 7, str(tmp_path))
        ficheiro1 = Path(tmp_path) / "scopus_2026_001.json"
        fichero2 = Path(tmp_path) / "scopus_2026_002.json"
        assert ficheiro1.exists()
        assert fichero2.exists()
        data1 = json.loads(ficheiro1.read_text(encoding="utf-8"))
        data2 = json.loads(fichero2.read_text(encoding="utf-8"))
        assert len(data1) == 1000
        assert len(data2) == 1

def test_processar_ano_two_max_batch_size_files(tmp_path):
    with patch('scopus_api_scraper.ScopusSearch') as mock_search:
        mock_docs = []
        for i in range(2000): # Create 2000 mock documents
            mock_doc = MagicMock()
            mock_doc._asdict.return_value = {
                "eid": f"2-s2.0-{i}",
                "description": f"Description {i}",
            }
            mock_docs.append(mock_doc)
        mock_search.return_value.results = mock_docs
        scraper.processar_ano(2026, 7, str(tmp_path))
        ficheiro1 = Path(tmp_path) / "scopus_2026_001.json"
        fichero2 = Path(tmp_path) / "scopus_2026_002.json"
        ficheiro3 = Path(tmp_path) / "scopus_2026_003.json"
        assert ficheiro1.exists()
        assert fichero2.exists()
        assert not ficheiro3.exists()
        data1 = json.loads(ficheiro1.read_text(encoding="utf-8"))
        data2 = json.loads(fichero2.read_text(encoding="utf-8"))
        assert len(data1) == 1000
        assert len(data2) == 1000

#===================================================================================
# TESTES DA CACHE
#===================================================================================

def test_query_contain_correct_year(tmp_path):
    with patch('scopus_api_scraper.ScopusSearch') as mock_search:
        mock_search.return_value.results = []
        scraper.processar_ano(2026, 7, str(tmp_path))

        args, kwargs = mock_search.call_args
        assert "2026" in args[0] or "2026" in str(kwargs)

#===================================================================================
# STRESS TESTS
#===================================================================================

def test_stress_test(tmp_path):
    docs = []
    for i in range(100_000):
        m = MagicMock()
        m._asdict.return_value = {"eid": f"2-s2.0-{i}", "description": f"Texto {i}"}
        docs.append(m)

    with patch('scopus_api_scraper.ScopusSearch') as mock_search:
        mock_search.return_value.results = docs

        start = time.time()
        result = scraper.processar_ano(2026, 7, str(tmp_path))
        elapsed = time.time() - start

        assert result == 100_000