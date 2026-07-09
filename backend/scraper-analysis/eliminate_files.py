import json
from pathlib import Path
from datetime import datetime
from utilis import load_existing_data_from_files_with_same_prefix, eliminate_old

BASE_INPUT_PATH = Path("documents/formatted_docs/")

def remove_duplicates(existing_items):
    objetos_unicos = {}
    objetos_cursos = {}

    for url, conteudo in existing_items.items():
        #caso dos cursos, ignorar
        if 'dataPublicacao' not in conteudo:
            objetos_cursos[url] = conteudo
            continue
        
        data_pub_atual = conteudo['dataPublicacao']
        chave_comparacao = (conteudo['titulo'])
        
        data_iso = conteudo['dateChecked'].replace('Z', '+00:00')
        data_verificacao_atual = datetime.fromisoformat(data_iso).replace(tzinfo=None)
        
        #se é repetido
        if chave_comparacao in objetos_unicos:
            url_existente, conteudo_existente = objetos_unicos[chave_comparacao]
            data_pub_existente = conteudo_existente['dataPublicacao']
            #se a data de publicação atual é mais recente, substitui o existente
            if data_pub_atual > data_pub_existente:
                objetos_unicos[chave_comparacao] = (url, conteudo)      

            data_iso_existente = conteudo_existente['dateChecked'].replace('Z', '+00:00')
            data_verificacao_existente = datetime.fromisoformat(data_iso_existente).replace(tzinfo=None)
            
            #se a data de publicação é igual, verifica a data de verificação
            if data_verificacao_atual > data_verificacao_existente:
                objetos_unicos[chave_comparacao] = (url, conteudo)
        else:
            objetos_unicos[chave_comparacao] = (url, conteudo)

    resultado_final = {}
    for url, conteudo in objetos_unicos.values():
        resultado_final[url] = conteudo
    resultado_final.update(objetos_cursos)
    return resultado_final

def main():
    BASE_INPUT_PATH.mkdir(parents=True, exist_ok=True)
    existing_items, _, _ = load_existing_data_from_files_with_same_prefix(BASE_INPUT_PATH, "documents_formatted_")
    not_dup = remove_duplicates(existing_items)
    resultado_final = eliminate_old(not_dup)
    items_finais = list(resultado_final.items())
    tamanho_bloco = 1000
    output_path =  Path("documents/filtered_docs/")
    output_path.mkdir(parents=True, exist_ok=True)
    prefixo_saida = "filtered_documents"

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

    print(f"Sucesso! Todos os dados foram divididos e guardados.")

if __name__ == "__main__":
    main()