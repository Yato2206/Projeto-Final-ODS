#!/usr/bin/env python3
"""
Document Formatter Script

Formats all JSON files from different sources (Newsletter, Scientific Repository)
into a standardized structure:

{
    "[link]": {
        "titulo": "Title",
        "autores": "Authors (blank for Newsletter)",
        "texto": "Full text content",
        "dataPublicacao": "YYYY-MM-DD",
        "tipo": "Newsletter" or "Repositório Científico",
        "dateChecked": "ISO timestamp",
        "origem": "Newsletter" or "Repositório Científico"
    }
}
"""

import json
import glob
from pathlib import Path
from datetime import datetime

DOCUMENTS_DIR = Path("documents")

def format_newsletter_documents():
    """Format newsletter content to standardized structure"""
    print("\n" + "="*60)
    print("FORMATTING NEWSLETTER DOCUMENTS")
    print("="*60)

    newsletter_file = DOCUMENTS_DIR / "newsletter_content.json"
    formatted_docs = {}

    if not newsletter_file.exists():
        print(f"⚠ Newsletter file not found: {newsletter_file}")
        return formatted_docs

    with open(newsletter_file, "r", encoding="utf-8") as f:
        newsletters = json.load(f)

    total_items = 0

    for newsletter_name, newsletter in newsletters.items():
        # Extract publication date
        date_publicacao = newsletter.get("dataPublicacao", "")
        date_checked = newsletter.get("dateChecked", datetime.now().isoformat())

        # Process Politécnico text as main item
        politecnico_titulo = newsletter.get("politecnicoTitulo", newsletter_name)
        politecnico_texto = newsletter.get("politecnicoTexto", "")
        link = newsletter.get("link", "")

        if link and politecnico_texto:
            formatted_docs[link] = {
                "titulo": politecnico_titulo,
                "autores": "Autor Desconhecido",
                "texto": politecnico_texto,
                "dataPublicacao": date_publicacao,
                "tipo": "Newsletter",
                "dateChecked": date_checked,
                "origem": "Newsletter"
            }
            total_items += 1

        # Process each noticia as separate item
        noticias = newsletter.get("noticias", [])
        for idx, noticia in enumerate(noticias):
            noticia_titulo = noticia.get("titulo", "")
            noticia_texto = noticia.get("texto", "")

            noticia_link = f"{link}#noticia-{idx}" if link else f"{newsletter_name}#noticia-{idx}"

            if noticia_texto:
                formatted_docs[noticia_link] = {
                    "titulo": noticia_titulo,
                    "autores": "Autor Desconhecido",
                    "texto": noticia_texto,
                    "dataPublicacao": date_publicacao,
                    "tipo": "Newsletter",
                    "dateChecked": date_checked,
                    "origem": "Newsletter"
                }
                total_items += 1

    print(f"✓ Formatted {total_items} newsletter items")
    return formatted_docs


def format_scientific_repo_documents():
    """Format scientific repository documents to standardized structure"""
    print("\n" + "="*60)
    print("FORMATTING SCIENTIFIC REPOSITORY DOCUMENTS")
    print("="*60)

    formatted_docs = {}
    repo_files = sorted(glob.glob(str(DOCUMENTS_DIR / "repo_cientifico_*.json")))

    total_items = 0

    for repo_file in repo_files:
        try:
            with open(repo_file, "r", encoding="utf-8") as f:
                documents = json.load(f)

            file_items = 0
            for link, doc in documents.items():
                titulo = doc.get("titulo", "")
                autores = doc.get("autores", "")
                texto = doc.get("texto", "")
                data_publicacao = doc.get("dataPublicacao", "")
                tipo = doc.get("tipo", "")
                date_checked = doc.get("dateChecked", datetime.now().isoformat())

                if texto:  # Only include if there's text content
                    formatted_docs[link] = {
                        "titulo": titulo,
                        "autores": autores,
                        "texto": texto,
                        "dataPublicacao": data_publicacao,
                        "tipo": tipo,
                        "dateChecked": date_checked,
                        "origem": "Repositório Científico"
                    }
                    total_items += 1
                    file_items += 1

            print(f"  ✓ {Path(repo_file).name}: {file_items} items")

        except Exception as e:
            print(f"  ✗ Error processing {repo_file}: {e}")

    print(f"✓ Formatted {total_items} scientific repository items")
    return formatted_docs


def merge_and_save(newsletter_docs, repo_docs, chunk_size=1000):
    """Merge all documents and save into multiple chunked files"""

    print("\n" + "="*60)
    print("MERGING AND SAVING")
    print("="*60)

    all_docs = {**newsletter_docs, **repo_docs}

    items = list(all_docs.items())

    total_files = 0

    for i in range(0, len(items), chunk_size):
        chunk = dict(items[i:i + chunk_size])

        output_file = DOCUMENTS_DIR / f"documents_formatted_{total_files + 1}.json"

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(chunk, f, ensure_ascii=False, indent=2)

        print(f"✓ Saved {len(chunk)} documents to {output_file}")

        total_files += 1

    print(f"\n✓ Saved {len(all_docs)} total documents across {total_files} files")

    return all_docs

def main():
    """Main formatter pipeline"""
    print("\nStarting document formatter...")

    # Ensure documents directory exists
    DOCUMENTS_DIR.mkdir(exist_ok=True)

    # Format documents from each source
    newsletter_docs = format_newsletter_documents()
    repo_docs = format_scientific_repo_documents()

    # Merge and save
    all_docs = merge_and_save(newsletter_docs, repo_docs)

    print("\n" + "="*60)
    print(f"FORMATTING COMPLETE!")
    print(f"Total documents: {len(all_docs)}")
    print(f"  - Newsletter items: {len(newsletter_docs)}")
    print(f"  - Scientific Repository items: {len(repo_docs)}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
