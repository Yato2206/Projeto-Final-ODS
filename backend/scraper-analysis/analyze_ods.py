import json
import re
import math
import glob
from pathlib import Path
import os
import nltk
from nltk.corpus import stopwords
from utilis import load_existing_data_from_files_with_same_prefix, eliminate_old
import ahocorasick
import time

nltk.download('punkt')
nltk.download('punkt_tab')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def preprocessar_texto(texto):
    if not texto:
        return ""
    texto = texto.lower()
    texto = re.sub(r'[^\w\s]', ' ', texto)
    palavras = nltk.word_tokenize(texto)

    return " ".join(palavras)

_automato = None
_keyword_para_ods = None
_estruturas_taxonomicas = None

_PADRAO_LIMITE = re.compile(r'\w')  # caracteres considerados "parte de palavra"


def _construir_automato():
    global _automato, _keyword_para_ods, _estruturas_taxonomicas
    if _automato is not None:
        return

    taxonomias = {}
    for nome_taxonomia, caminho_arquivo in get_taxonomias().items():
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            taxonomias[nome_taxonomia] = json.load(f)

    automato = ahocorasick.Automaton()
    keyword_para_ods = {}
    estrutura = {}

    for nome_taxonomia, keywords_por_ods in taxonomias.items():
        estrutura[nome_taxonomia] = list(keywords_por_ods.keys())
        for ods, keywords in keywords_por_ods.items():
            for kw in keywords:
                kw_lower = kw.lower().strip()
                if not kw_lower:
                    continue
                keyword_para_ods.setdefault(kw_lower, []).append((nome_taxonomia, ods))
                # add_word aceita chave duplicada (sobrescreve o value), por isso
                # o mapeamento real está em keyword_para_ods, não no automaton
                automato.add_word(kw_lower, kw_lower)

    automato.make_automaton()
    _automato = automato
    _keyword_para_ods = keyword_para_ods
    _estruturas_taxonomicas = estrutura


def _e_limite_de_palavra(texto, pos):
    """True se a posição pos (fora dos limites incluído) NÃO é parte de uma palavra."""
    if pos < 0 or pos >= len(texto):
        return True
    return not _PADRAO_LIMITE.match(texto[pos])

def get_taxonomias():
    taxonomies_dir = os.path.join(BASE_DIR, 'taxonomies')
    os.makedirs(taxonomies_dir, exist_ok=True)
    filepaths = sorted(glob.glob(os.path.join(taxonomies_dir, 'taxo_*.json')))

    taxonomia_files = {}

    for path in filepaths:

        filename = os.path.basename(path)

        key = filename.replace('taxo_', '').replace('.json', '')

        taxonomia_files[key] = path

    return taxonomia_files

def classificar_ods(titulo, texto_conteudo):
    _construir_automato()

    texto_completo = f"{titulo} {texto_conteudo}"
    texto_tratado = preprocessar_texto(texto_completo).lower()

    contagens = {}  # (nome_taxonomia, ods) -> contagem

    for end_idx, kw_encontrada in _automato.iter(texto_tratado):
        start_idx = end_idx - len(kw_encontrada) + 1

        # verifica word boundary manualmente (equivalente ao \b...\b do regex original)
        antes_ok = _e_limite_de_palavra(texto_tratado, start_idx - 1)
        depois_ok = _e_limite_de_palavra(texto_tratado, end_idx + 1)

        if not (antes_ok and depois_ok):
            continue

        for nome_taxonomia, ods in _keyword_para_ods[kw_encontrada]:
            chave = (nome_taxonomia, ods)
            contagens[chave] = contagens.get(chave, 0) + 1

    resultados = {}
    for nome_taxonomia, lista_ods in _estruturas_taxonomicas.items():
        ods_identificados = {}
        for ods in lista_ods:
            contagem = contagens.get((nome_taxonomia, ods), 0)
            if contagem > 0:
                ods_identificados[ods] = contagem
        resultados[nome_taxonomia] = ods_identificados

    return resultados

def extrair_indice(caminho):
    m = re.search(r'_(\d+)\.json$', os.path.basename(caminho))
    return int(m.group(1)) if m else -1

def process_files_and_save(files_pattern, chunk_size=1000):
    output_dir = Path(__file__).parent.parent.parent / 'frontend' / 'public'
    #output_dir = os.path.join(BASE_DIR, '..', '..', 'frontend', 'public')
    os.makedirs(output_dir, exist_ok=True)

    existing_results, _, _ = load_existing_data_from_files_with_same_prefix(output_dir, "resultados_ods")
    print(f"Loaded {len(existing_results)} results from output.")

    dados_consolidados = dict(existing_results)

    ficheiros_entrada = sorted(glob.glob(files_pattern))
    print(f"Found {len(ficheiros_entrada)} files matching pattern: {files_pattern}")

    if not ficheiros_entrada:
        print(f"No files found with pattern: {files_pattern}")
        return

    print(f"Files found: {ficheiros_entrada}")

    for caminho_ficheiro in ficheiros_entrada:
        print(f"A ler e a analisar: {os.path.basename(caminho_ficheiro)}...")

        with open(caminho_ficheiro, 'r', encoding='utf-8') as f:
            dados_ficheiro = json.load(f)

        for url, info in dados_ficheiro.items():

            if url in dados_consolidados:
                continue

            titulo = info.get("titulo", "")
            if not titulo:
                titulo = info.get("curso", "")
            texto_conteudo = info.get("texto", "")

            print(f"A analisar {url}")
            ods_mapeados = classificar_ods(titulo, texto_conteudo)

            item_resultado = info.copy()
            item_resultado["ods_mapeados"] = ods_mapeados
            dados_consolidados[url] = item_resultado

    new_items = [(u, v) for u, v in dados_consolidados.items() if u not in existing_results]
    total_new = len(new_items)
    print(f"New items to add: {total_new}")

    existing_files = sorted(glob.glob(os.path.join(output_dir, 'resultados_ods_*.json')), key = extrair_indice)
    last_index = 0
    last_path = None
    last_data = {}

    if existing_files:
        last_path = existing_files[-1]
        try:
            last_index = int(os.path.splitext(os.path.basename(last_path))[0].split('_')[-1])
        except Exception:
            last_index = len(existing_files)
        try:
            with open(last_path, 'r', encoding='utf-8') as f:
                last_data = json.load(f) or {}
        except Exception as e:
            print(f"Warning: could not load last results file {last_path}: {e}")
            last_data = {}

    if last_index == 0:
        next_index = 1
    else:
        next_index = last_index + 1

    written_count = 0
    if last_path and isinstance(last_data, dict):
        space = chunk_size - len(last_data)
        if space > 0 and total_new > 0:
            to_take = min(space, total_new)

            for i in range(to_take):
                url, item = new_items[i]
                last_data[url] = item
                written_count += 1

            tmp_last = last_path + '.tmp'
            with open(tmp_last, 'w', encoding='utf-8') as f_out:
                json.dump(last_data, f_out, indent=2, ensure_ascii=False)
            os.replace(tmp_last, last_path)
            print(f"-> Added {to_take} items to existing file: {last_path}")

    remaining = new_items[written_count:]
    if remaining:
        for i in range(0, len(remaining), chunk_size):
            chunk_slice = remaining[i:i + chunk_size]
            chunk_dict = {u: v for u, v in chunk_slice}
            out_path = os.path.join(output_dir, f"resultados_ods_{next_index}.json")
            tmp_path = out_path + '.tmp'
            with open(tmp_path, 'w', encoding='utf-8') as f_out:
                json.dump(chunk_dict, f_out, indent=2, ensure_ascii=False)
            os.replace(tmp_path, out_path)
            print(f"-> Saved new file: {out_path} ({len(chunk_dict)} items)")
            next_index += 1

print(Path(__file__).parent.parent.parent / 'frontend' / 'public')
existing_results, _, _ = load_existing_data_from_files_with_same_prefix(Path(__file__).parent.parent.parent / 'frontend' / 'public', "resultados_ods")  # Load existing results
print(f"Loaded {len(existing_results)} existing results for ODS analysis.")
resultado_final = eliminate_old(existing_results)  # Call eliminate_old with existing results to clean up old files
items_finais = list(resultado_final.items())
tamanho_bloco = 1000
output_path =  Path(__file__).parent.parent.parent / 'frontend' / 'public'
output_path.mkdir(parents=True, exist_ok=True)
prefixo_saida = "resultados_ods"

for i in range(0, len(items_finais), tamanho_bloco):
    bloco_atual = items_finais[i : i + tamanho_bloco]
    
    # Converte o bloco de volta para o formato de dicionário {url: conteudo}
    dicionario_bloco = dict(bloco_atual)
    
    # Define o nome do ficheiro (ex: resultado_sem_duplicados_1.json, resultado_sem_duplicados_2.json)
    numero_ficheiro = (i // tamanho_bloco) + 1
    nome_ficheiro = f"{prefixo_saida}_{numero_ficheiro}.json"
    
    with open(output_path / nome_ficheiro, 'w', encoding='utf-8') as f:
        json.dump(dicionario_bloco, f, indent=4, ensure_ascii=False)
        
    print(f"Ficheiro '{nome_ficheiro}' guardado com {len(dicionario_bloco)} itens.")
process_files_and_save('documents/filtered_docs/filtered_documents_*.json', chunk_size=1000)