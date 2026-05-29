import os
import traceback
from pybliometrics.scopus import ScopusSearch, AbstractRetrieval
import json
from tqdm import tqdm
import time
import logging
from datetime import datetime

# Configure logging
#logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# NOTE: config file for pybliometrics is stored in $HOME/.config/pybliometrics.cfg

if __name__ == "__main__":
    # initialize pybliometrics
    import pybliometrics
    logger.info("Initializing pybliometrics...")
    pybliometrics.scopus.init()
    logger.info("Pybliometrics initialized successfully")

    CURRENT_YEAR = datetime.now().year
    FIRST_YEAR = CURRENT_YEAR - 5 # pegar os ultimos 5 anos de publicações

    # begin script
    for year in range(FIRST_YEAR, CURRENT_YEAR + 1):    #o segundo parametro da funcao range nao conta, 
                                                        #logo para pegar o do ano atual é necessário colocar o 
                                                        # ano atual + 1
        logger.info(f"Processing year {year}")
        # make the folder to store the data for the year
        current_path = os.getcwd()
        folder_path = os.path.join(current_path, "output", str(year))
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        # get the results
        logger.info(f"Starting ScopusSearch for year {year}...")
        start_time = time.time()
        x = ScopusSearch(
            f'PUBYEAR = {year} AND ( LIMIT-TO ( LANGUAGE , "English" ) OR LIMIT-TO ( LANGUAGE , "Portuguese" ) ) AND ( AF-ID ( "60018688" ) OR AF-ID ( "60019813" ) OR AF-ID ( "60079659" ) OR AF-ID ( "60285972" ) )',
            #f'ABS ( "data mining" ) OR ABS ( "machine learning" ) OR TITLE ( "data mining" ) OR TITLE ( "machine learning" ) AND TITLE ( "material" ) OR ABS ( "material" ) OR SRCTITLE ( "material" ) AND SUBJAREA ( mate ) AND DOCTYPE ( "AR" ) AND SRCTYPE( j ) AND PUBYEAR = {year} AND NOT SUBJAREA (medi ) AND NOT SUBJAREA ( immu ) AND NOT SUBJAREA ( BIOC ) AND NOT SUBJAREA ( busi )',
            view="COMPLETE")
        elapsed_time = time.time() - start_time
        logger.info(f"ScopusSearch completed in {elapsed_time:.2f}s. Year: {year}, Results count: {len(x.results)}")
        print(f"Year: {year} , Results count: {len(x.results)}")

        # Group results into batches of up to 1000 items
        batch_size = 1000
        results = x.results
        num_batches = (len(results) + batch_size - 1) // batch_size
        
        for batch_num in range(num_batches):
            try:
                start_idx = batch_num * batch_size
                end_idx = min(start_idx + batch_size, len(results))
                batch = results[start_idx:end_idx]
                
                # Create batch file
                batch_file_name = f"scopus_{year}_{batch_num + 1:03d}.json"
                batch_file_path = os.path.join(folder_path, batch_file_name)
                
                publications = []
                
                for doc in tqdm(batch, desc=f"Processing batch {batch_num + 1}/{num_batches}"):
                    try:
                        doc_dict = doc._asdict()
                        eid = doc_dict.get("eid")
                        link = f"https://www.scopus.com/pages/publications/{eid}"
                        
                        # Extract specific parameters from the document
                        publication = {
                            "titulo": doc_dict.get("title"),
                            "link": link,
                            "dataPublicacao": doc_dict.get("coverDate"),
                            "autores": doc_dict.get("author_names"),
                            "texto": doc_dict.get("description"),
                            "tipo": doc_dict.get("subtypeDescription"),
                            "dateChecked": datetime.now().isoformat()
                        }
                        
                        publications.append(publication)
                        
                    except Exception as e:
                        logger.error(f"Error processing document in batch: {e}", exc_info=True)
                        pass
                
                # Save batch to JSON file
                with open(batch_file_path, "w", encoding="utf-8") as json_file:
                    json.dump(publications, json_file, indent=2, ensure_ascii=False)
                logger.info(f"Saved {batch_file_name} with {len(publications)} publications")
                print(f"Saved {batch_file_name} with {len(publications)} publications")
                
            except Exception as e:
                logger.error(f"Error processing batch {batch_num}: {e}", exc_info=True)
                pass