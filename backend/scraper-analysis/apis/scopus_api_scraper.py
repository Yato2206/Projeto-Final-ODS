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
DOCUMENTS_DIR = Path("documents")

def get_prev_data_count():
    return len(list(DOCUMENTS_DIR.glob("scopus_*_*.json")))

def processar_ano(year, period_to_search, folder_path):
    """Faz a query ao Scopus para um ano e grava os batches em ficheiro. Devolve nº de publicações guardadas."""
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

    # Group results into batches of up to 1000 items
    batch_size = 1000
    results = x.results
    num_batches = (len(results) + batch_size - 1) // batch_size
    total_saved = 0

    for batch_num in range(num_batches):
        try:
            start_idx = batch_num * batch_size
            end_idx = min(start_idx + batch_size, len(results))
            batch = results[start_idx:end_idx]

            # Create batch file
            batch_file_name = f"scopus_{year}_{batch_num + 1:03d}.json"
            batch_file_path = os.path.join(folder_path, batch_file_name)

            publications = {}

            for doc in tqdm(batch, desc=f"Processing batch {batch_num + 1}/{num_batches}"):
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

                     # Extract specific parameters from the document
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
                    logger.error(f"Error processing document in batch: {e}", exc_info=True)
                    pass

            with open(batch_file_path, "w", encoding="utf-8") as json_file:
                json.dump(publications, json_file, indent=2, ensure_ascii=False)
            print(f"Saved {batch_file_name} with {len(publications)} publications")
            total_saved += len(publications)

        except Exception as e:
            logger.error(f"Error processing batch {batch_num}: {e}", exc_info=True)
            pass

    return total_saved


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

    folder_path = os.path.join(os.getcwd(), "documents")
    os.makedirs(folder_path, exist_ok=True)

    for year in range(first_year, current_year + 1):
        processar_ano(year, period_to_search, folder_path)

if __name__ == "__main__":
    main()