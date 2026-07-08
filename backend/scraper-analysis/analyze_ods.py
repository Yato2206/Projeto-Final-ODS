import json
import re
import math
import glob
import os
import nltk
from nltk.corpus import stopwords
from utilis import load_existing_data_from_files_with_same_prefix

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

def get_taxonomias():
    taxonomies_dir = os.path.join(BASE_DIR, 'documents', 'taxonomies')
    filepaths = sorted(glob.glob(os.path.join(taxonomies_dir, 'taxo_*.json')))

    taxonomia_files = {}

    for path in filepaths:

        filename = os.path.basename(path)

        key = filename.replace('taxo_', '').replace('.json', '')

        taxonomia_files[key] = path

    return taxonomia_files

def classificar_ods(titulo, texto_conteudo):
    taxonomias = {}
    taxonomia_files = get_taxonomias()

    for nome_taxonomia, caminho_arquivo in taxonomia_files.items():
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            taxonomias[nome_taxonomia] = json.load(f)

    texto_completo = f"{titulo} {texto_conteudo}"
    texto_tratado = preprocessar_texto(texto_completo)

    resultados = {}

    for nome_taxonomia, keywords in taxonomias.items():

        ods_identificados = {}

        for ods, keywords in keywords.items():
            contagem_ods = 0
            for kw in keywords:
                padrao = rf"\b{re.escape(kw.lower())}\b"
                correspondencias = len(re.findall(padrao, texto_tratado))
                contagem_ods += correspondencias

            if contagem_ods > 0:
                ods_identificados[ods] = contagem_ods

        resultados[nome_taxonomia] = ods_identificados

    return resultados

def process_files_and_save(files_pattern, chunk_size=1000):
    output_dir = os.path.join(BASE_DIR, '..', '..', 'frontend', 'public')
    os.makedirs(output_dir, exist_ok=True)

    existing_results, _, _ = load_existing_data_from_files_with_same_prefix(output_dir, "resultados_ods")
    print(f"Loaded {len(existing_results)} results from output.")

    dados_consolidados = dict(existing_results)

    ficheiros_entrada = sorted(glob.glob(files_pattern))

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

    existing_files = sorted(glob.glob(os.path.join(output_dir, 'resultados_ods_*.json')))
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

process_files_and_save('documents/filtered_docs/filtered_documents_*.json', chunk_size=1000)
