from pyorcid import OrcidAuthentication, Orcid
from datetime import datetime
from pathlib import Path
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utilis import extract_year, load_existing_data
import json
from dotenv import load_dotenv
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

class RateLimiter:
    """Garante no máximo `max_calls` chamadas por `period` segundos, entre threads."""
    def __init__(self, max_calls, period=1.0):
        self.max_calls = max_calls
        self.period = period
        self.lock = threading.Lock()
        self.calls = []

    def acquire(self):
        with self.lock:
            now = time.monotonic()
            self.calls = [c for c in self.calls if now - c < self.period]
            if len(self.calls) >= self.max_calls:
                sleep_time = self.period - (now - self.calls[0])
                if sleep_time > 0:
                    time.sleep(sleep_time)
                now = time.monotonic()
                self.calls = [c for c in self.calls if now - c < self.period]
            self.calls.append(time.monotonic())


rate_limiter = RateLimiter(max_calls=10, period=1.0)

load_dotenv()

auth = OrcidAuthentication(client_id=os.getenv("client_id"), client_secret=os.getenv("client_secret"))
token = auth.get_public_access_token()

def carregar_investigadores_de_docentes(docentes_path):
    """Lê o ficheiro docentes-info.json e retorna uma lista de dicts
    com `nome` e `id` extraído do link ORCID.
    Apenas inclui entradas que tenham um link ORCID válido.
    """
    if not docentes_path.exists():
        return []

    dados = load_existing_data(docentes_path)

    resultados = []
    for nome, info in dados.items():
        orcid_info = info.get("ORCID") if isinstance(info, dict) else None
        if not orcid_info:
            continue
        link = orcid_info.get("link") if isinstance(orcid_info, dict) else None
        if not link:
            continue
        # Extrai o ID do final do link (ex: https://orcid.org/0000-0002-7858-5358)
        orcid_id = link.rstrip("/").split("/")[-1]
        if orcid_id:
            resultados.append({"nome": nome, "id": orcid_id})

    return resultados

BASE_DIR = Path(__file__).parent
ESCOLAS_PATH = BASE_DIR.parent / "escolas"
DOCENTES_PATH = ESCOLAS_PATH / "docentes-info.json"

PRESENT_YEAR = datetime.now().year
ESCOLAS = [
    "Escola Superior de Comunicação Social",
    "Escola Superior de Dança",
    "Escola Superior de Educação de Lisboa",
    "Escola Superior de Música de Lisboa",
    "Escola Superior de Teatro e Cinema",
    "Escola Superior de Saúde de Lisboa",
    "Instituto Superior de Contabilidade e Administração de Lisboa",
    "Instituto Superior de Engenharia de Lisboa",
    "Instituto Politécnico de Lisboa",
]

def extract_funding_info(summary, docente):
    def get_date(date_obj):
        if not date_obj:
            return "0000-00-00"
        year = date_obj.get("year", {}).get("value") if date_obj.get("year") else "0000"
        month = date_obj.get("month", {}).get("value") if date_obj.get("month") else None
        if not month:
            return f"{year}"
        day = date_obj.get("day", {}).get("value") if date_obj.get("day") else None
        if not day:
            return f"{year}-{month}"
        return f"{year}-{month}-{day}"

    link = f"https://orcid.org/{docente['id']}"
    return {
        "titulo": summary.get("title", {}).get("title", {}).get("value"),
        "link": link,
        "autores": docente["nome"],
        "texto": "", #não dá para pegar a descrição a partir da API
        "dataPublicacao": get_date(summary.get("end-date")),
        "tipo": summary.get("type"),
        "dateChecked": datetime.now().isoformat(),
        "organizacao": summary.get("organization", {}).get("name"),
        "origem": "Orcid"
    }

def processar_docente(docente, token):
    """Faz a chamada à API (respeitando o rate limit) e devolve os fundings já filtrados."""
    rate_limiter.acquire()

    try:
        orcid = Orcid(orcid_id=docente["id"], orcid_access_token=token, state="public")
    except Exception as e:
        print(f"Erro a criar objeto Orcid para {docente['nome']} ({docente['id']}): {e}")
        return []

    fundings_data = orcid.fundings()
    full_data = fundings_data[1]

    all_funding_summaries = []
    for group in full_data.get("group", []):
        summaries = group.get("funding-summary", [])
        if summaries:
            all_funding_summaries.append(summaries[0])

    fundings_clean = [extract_funding_info(s, docente) for s in all_funding_summaries]

    fundings = []
    for f in fundings_clean:
        if f.get("organizacao") not in ESCOLAS:
            continue
        if PRESENT_YEAR - extract_year(f.get("dataPublicacao")) <= 5:
            fundings.append(f)

    return fundings

def main():
    print(f"\n{'='*50}")
    print(f"ORCID Funding Scraper")
    print(f"{'='*50}\n")

    os.makedirs(DOCENTES_PATH.parent, exist_ok=True)

    docentes = carregar_investigadores_de_docentes(DOCENTES_PATH)

    resultados = {}
    max_workers  = 12 # Número máximo de threads para chamadas à API. Pode ir até 12 com Public API
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_docente = {
            executor.submit(processar_docente, docente, token): docente
            for docente in docentes
        }

        for future in as_completed(future_to_docente):
            docente = future_to_docente[future]
            print(f"Concluído: {docente['nome']} ({docente['id']})")
            try:
                fundings = future.result()
                for funding in fundings:
                    resultados[funding["titulo"]] = funding
            except Exception as e:
                print(f"Erro a processar {docente['nome']} ({docente['id']}): {e}")

    output_dir = ESCOLAS_PATH.parent / "documents" / "docentes"
    os.makedirs(output_dir, exist_ok=True)
    json_output_path = output_dir / "docentes-financiamentos.json"
    with open(json_output_path, 'w', encoding='utf-8') as f:
        json.dump(resultados, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    main()