import os
import traceback
from pybliometrics.scopus import ScopusSearch, AbstractRetrieval
import json
from pathlib import Path
from tqdm import tqdm
import time
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
BASE_DIR = Path(__file__).parent
DOCUMENTS_DIR = Path(BASE_DIR, "../documents/scopus")

def get_prev_data_count():
    return len(list(DOCUMENTS_DIR.glob("scopus_*.json")))

def processar_ano(year, period_to_search, folder_path):
    """Faz a query ao Scopus para um ano e grava as publicações num ficheiro. Devolve nº de publicações guardadas."""
    start_time = time.time()
    x = ScopusSearch(
        f'PUBYEAR = {year} AND ( LIMIT-TO ( LANGUAGE , "English" ) OR LIMIT-TO ( LANGUAGE , "Portuguese" ) ) AND ( AF-ID ( "60018688" ) OR AF-ID ( "60019813" ) OR AF-ID ( "60079659" ) OR AF-ID ( "60285972" ) )',
        refresh=period_to_search,
        view="COMPLETE",
    )
    elapsed_time = time.time() - start_time
    print(f"Year: {year}, Results count: {len(x.results)}")
    print(f"Cache file modified: {x.get_cache_file_mdate()}")
    print(f"Cache file age: {x.get_cache_file_age()}")

    results = x.results
    publications = {}

    for doc in tqdm(results, desc=f"Processing year {year}"):
        try:
            doc_dict = doc._asdict()
            eid = doc_dict.get("eid")
            if not eid:
                logger.warning(f"Document missing EID: {doc_dict}")
                continue
            link = f"https://www.scopus.com/pages/publications/{eid}"
            texto = doc_dict.get("description")
            # Se o texto for None, não adiciona a publicação ao ficheiro, já que não existirá conteúdo para análise.
            if texto is None:
                logger.info(f"Document with EID {eid} has no description, skipping.")
                continue

            publications[link] = {
                "titulo": doc_dict.get("title"),
                "autores": doc_dict.get("author_names"),
                "texto": texto,
                "dataPublicacao": doc_dict.get("coverDate"),
                "tipo": doc_dict.get("subtypeDescription"),
                "dateChecked": datetime.now().isoformat(),
                "origem": "Scopus"
            }

        except Exception as e:
            logger.error(f"Error processing document: {e}", exc_info=True)
            pass

    file_name = f"scopus_{year}.json"
    file_path = os.path.join(folder_path, file_name)

    with open(file_path, "w", encoding="utf-8") as json_file:
        json.dump(publications, json_file, indent=2, ensure_ascii=False)
    print(f"Saved {file_name} with {len(publications)} publications")

    return len(publications)


def main():
      # initialize pybliometrics
    import pybliometrics
    pybliometrics.scopus.init()

    existing_files = get_prev_data_count()
    print(f"Number of existing files: {existing_files}")

    current_year = datetime.now().year
    
    # pegar apenas as publicações do ano atual, de modo a poupar tokens
    # pegar os ultimos 5 anos de publicações, já que não foram feitas pesquisas antes
    first_year = current_year if existing_files > 0 else current_year - 5  

    # valor em dias para definir quando faz uma pesquisa ao scopus, em vez de pegar os dados da cache
    # por defeito, serão 7 dias (uma semana) para atualizar, gastando tokens apenas 1 vez por semana
    period_to_search = 7

    folder_path = os.path.join(os.getcwd(), DOCUMENTS_DIR)

    for year in range(first_year, current_year + 1):
        processar_ano(year, period_to_search, folder_path)

if __name__ == "__main__":
    DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)
    main()