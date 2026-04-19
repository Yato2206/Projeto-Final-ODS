from sentence_transformers import SentenceTransformer, util
import json

model = SentenceTransformer('all-MiniLM-L6-v2')

ods_descriptions = {
    "ODS 1": "Erradicação da Pobreza",
    "ODS 2": "Fome Zero",
    "ODS 3": "Boa Saúde e Bem-Estar",
    "ODS 4": "Educação de Qualidade",
    "ODS 5": "Igualdade de Género",
    "ODS 6": "Água Limpa e Saneamento",
    "ODS 7": "Energia Acessível e Limpa",
    "ODS 8": "Emprego Digno e Crescimento Económico",
    "ODS 9": "Indústria, Inovação e Infraestrutura",
    "ODS 10": "Redução das Desigualdades",
    "ODS 11": "Cidades e Comunidades Sustentáveis",
    "ODS 12": "Consumo e Produção Responsáveis",
    "ODS 13": "Combate às Alterações Climáticas",
    "ODS 14": "Vida de Baixo D'Água",
    "ODS 15": "Vida Sobre a Terra",
    "ODS 16": "Paz, Justiça e Instituições Fortes",
    "ODS 17": "Parcerias Emprol das Metas"
}

ods_embeddings = {
    ods: model.encode(desc, convert_to_tensor=True)
    for ods, desc in ods_descriptions.items()
}

def classify_text(text):
    text_embedding = model.encode(text, convert_to_tensor=True)

    scores = {}

    for ods, emb in ods_embeddings.items():
        similarity = util.cos_sim(text_embedding, emb).item()
        scores[ods] = similarity

    return scores

with open("newsletter-content.json", "r", encoding="utf-8") as f:
    data = json.load(f)

results = {}
percentage_results = {}

for newsletter_name, newsletter in data.items():

    newsletter_results = []
    ods_totals = {ods: 0 for ods in ods_descriptions}

    # 1. process each news item
    for noticia in newsletter["noticias"]:
        text = noticia["titulo"] + " " + noticia["texto"]

        scores = classify_text(text)

        relevant = {k: v for k, v in scores.items() if v > 0.35}

        newsletter_results.append({
            "title": noticia["titulo"],
            "ods": relevant
        })

        # accumulate scores per newsletter
        for ods, score in scores.items():
            ods_totals[ods] += score

    results[newsletter_name] = newsletter_results


    # 2. normalize INSIDE THIS NEWSLETTER ONLY
    total = sum(ods_totals.values())

    if total > 0:
        ods_percentages = {}

        for ods, score in ods_totals.items():
            percentage = (score / total) * 100

            if percentage > 1:  # filter low importance
                ods_percentages[ods] = f"{percentage:.2f}%"

    else:
        ods_percentages = {}

    percentage_results[newsletter_name] = ods_percentages


# Save to file
with open("newsletter-analysis.json", "w", encoding="utf-8") as f:
    print("Newsletter analysis completed.")
    json.dump(results, f, ensure_ascii=False, indent=2)

with open("newsletter-percentages.json", "w", encoding="utf-8") as f:
    print("Newsletter percentages completed.")
    json.dump(percentage_results, f, ensure_ascii=False, indent=2)