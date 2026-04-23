from sentence_transformers import SentenceTransformer, util
import json

model = SentenceTransformer('all-MiniLM-L6-v2')

ods_descriptions = {
    #=======================================================================
    #SEM TAXONOMIA
    #=======================================================================
    #"ODS 1": "Erradicação da Pobreza",
    #"ODS 2": "Fome Zero",
    #"ODS 3": "Boa Saúde e Bem-Estar",
    #"ODS 4": "Educação de Qualidade",
    #"ODS 5": "Igualdade de Género",
    #"ODS 6": "Água Limpa e Saneamento",
    #"ODS 7": "Energia Acessível e Limpa",
    #"ODS 8": "Emprego Digno e Crescimento Económico",
    #"ODS 9": "Indústria, Inovação e Infraestrutura",
    #"ODS 10": "Redução das Desigualdades",
    #"ODS 11": "Cidades e Comunidades Sustentáveis",
    #"ODS 12": "Consumo e Produção Responsáveis",
    #"ODS 13": "Combate às Alterações Climáticas",
    #"ODS 14": "Vida de Baixo D'Água",
    #"ODS 15": "Vida Sobre a Terra",
    #"ODS 16": "Paz, Justiça e Instituições Fortes",
    #"ODS 17": "Parcerias Emprol das Metas"
    #=======================================================================
    #ENGLISH (NO 17 )
    #=======================================================================
    #"ODS 1": "poverty, income distribution, wealth distribution, socio economic, socio-economic, socioeconomic, homeless, low-income, low income, affordab*, disparity, welfare, social safety, developing country, vulnerability, precarity, precarious, pro-poor",
    #"ODS 2": "agricultur*, nutrition, food security, food insecurity, food-secure, food system, child hunger, food justice, food scarcity, food sovereignty, food culture, culinary, agro*, permaculture, indigenous crops, regenerative agriculture, urban agriculture, organic food, biodynamic, food literacy, food education, benefit sharing, access and benefit sharing (ABS), malnutrition, end hunger, food price, zero hunger",
    #"ODS 3": "well being, wellbeing, well-being, mental health, public health, global health, health care, healthcare, health issues, mental wellness, disabilit*, sexual education, mindfulness, holism, illness, health education, communicable disease, health determinants, vaccine, substance abuse, maternal mortality, family planning, hazardous chemicals, pollution, health equity, neonatal mortality, infant mortality, child health, road traffic accidents, reproductive health, epidemics, universal health coverage",
    #"ODS 4": "equitable, pedagogy, knowledge, worldview, learning, knowledges, traditional knowledge, land-based knowledge, place-based knowledge, decolonial*, anticolonial, settler, equitable, equity, anti-racism, racism, anti-oppression, oppression, anti-discriminatory, early childhood development, peace, citizen, sustainability teaching, sustainability education, universal literacy, basic literacy, universal numeracy, environmental education, education for sustainable development, ecojustice education, place-based education, humane education, land-based learning, nature-based education, climate change education, vocational, technical learning, free education, accessible education, primary education, secondary education, tertiary education",
    #"ODS 5": "gender, women, girl, queer, female, feminis*, non-binary, non binary, sexes, LGBTQ*, patriarchy, transgender, two-spirit, gender equality, violence against women, trafficking, forced marriage",
    #"ODS 6": "water, sanita*, contamination, arid, drought, hygien*, sewage water scarcity, remediation, untreated wastewater, water harvesting, desalination, water efficiency, groundwater depletion, desertification, water filtration, latrines, open defecation, hydrological cycle, water and energy nexus, stormwater management, low impact development, green infrastructure, living infrastructure water education",
    #"ODS 7": "energy, renewabl*, wind, solar, geothermal, hydroelectric, fuel efficient, fuel-efficient, carbon capture, emission*, greenhouse, biofuel; energy sovereignty, energy security, energy education",
    #"ODS 8": "employment, economic growth, sustainable development, labour, labor, worker, wage, economic empowerment, entrepreneur*, small- and medium-sized enterprises, SMEs, sustainable tourism, youth employment, green job, economic recovery, green growth, sustainable growth",
    #"ODS 9": "infrastructure, buildings, capital, invest*, internet, globaliz*, globalis*, Industrialization, value chain, affordable credit, industrial diversification",
    #"ODS 10": "trade, inequality, financial market, taxation, equit*, equalit*, humanitarian, minorit*, refugee, BIPOC, of colour, of color, indigenous, reconciliation, truth and reconciliation, underserved, privileged, affordab*, equal access, marginalized, marginalised, impoverished, vulnerable population, social safety, social security, government program, disparity, income, Gini, anti-oppressive, anti-racist, anti-discriminatory, decolonization",
    #"ODS 11": "cities*, urban, resilien*, rural, sustainable development, public transport*, metro*, housing green infrastructure, low impact development, climate change adaptation, climate change mitigation, green buildings, affordable housing, walkab*, transit, civic spaces, open spaces, accessib*, indigenous placemaking, indigenous placekeeping",
    #"ODS 12": "consum*, production, waste, natural resource*, recycl*, industrial ecology, sustainable design, supply chain, outsourc*, offshor*, reuse, decarboniz*,decarbonis*, carbon tax, carbon pricing, food waste, public procurement, fossil fuel subsidies",
    #"ODS 13": "climate, greenhouse gas, global warming, weather, environmental, planet, vegan, vegetarian, anthropogenic, fossil fuel, emissions, carbon dioxide, CO2, carbon-neutral, carbon neutral, net zero, net-zero, methane, sea level, climate change mitigation, climate change adaptation, climate impacts, climate scenarios, climate solutions, climate justice, global climate models carbon capture, carbon sequestration, low carbon, resilience, anthropocene, climate positive, offsets, carbon trading, carbon markets, UNFCCC, climate finance, loss and damage, Paris",
    #"ODS 14": "ocean, marine, pollut*, conserv*, fish, natural habitat, species, animal, biodivers*, coral, maritime, ocean literacy ecosystem, overfish*, fish stocks, ocean, sustainable use, traditional use",
    #"ODS 15": "forest, biodivers*, ecolog*, pollut*, conserv*, land use, natural habitat, species, animal, regeneration, resilience, sustainable and traditional use, land ecological restoration, forest conservation, carbon sequestration, carbon capture, soil, erosion, habitat loss, endangered species ecosystem, deforestation, reforestation, wildlife, flora and fauna, benefit sharing",
    #"ODS 16": "institut*, governance, peace, social justice, injustice, criminal justice, human rights, democratic rights, voter rights, legal system, social change, corrupt*, nationalism, democra*, authoritarian, indigenous, judic*, ecojustice, indigenous rights, self-determination sovereignty violence, exploitation, trafficking, torture, rule of law, illicit, organized crime, bribe*, terroris*, prior and informed consent, access and benefit sharing, UNDRIP (United Nations Declaration on Rights of Indigenous Peoples), indigenous rights",
    #"ODS 17": ""
    #=======================================================================
    #PORTUGUESE (NO 17)
    #=======================================================================
    "ODS 1": "pobreza, distribuição de rendimento, distribuição de riqueza, socioeconómico, sem-abrigo, baixos rendimentos, acessível, disparidade, bem-estar social, proteção social, país em desenvolvimento, vulnerabilidade, precariedade, pró-pobre",
    "ODS 2": "agricultur*, nutrição, segurança alimentar, insegurança alimentar, sistema alimentar, fome infantil, justiça alimentar, escassez alimentar, soberania alimentar, cultura alimentar, culinária, agro*, permacultura, culturas indígenas, agricultura regenerativa, agricultura urbana, alimentação biológica, biodinâmica, literacia alimentar, educação alimentar, partilha de benefícios, acesso e partilha de benefícios, malnutrição, acabar com a fome, preço dos alimentos, fome zero",
    "ODS 3": "bem-estar, saúde mental, saúde pública, saúde global, cuidados de saúde, problemas de saúde, bem-estar mental, deficiênc*, educação sexual, mindfulness, holismo, doença, educação para a saúde, doenças transmissíveis, determinantes da saúde, vacina, abuso de substâncias, mortalidade materna, planeamento familiar, químicos perigosos, poluição, equidade na saúde, mortalidade neonatal, mortalidade infantil, saúde infantil, acidentes rodoviários, saúde reprodutiva, epidemias, cobertura universal de saúde",
    "ODS 4": "equidade, pedagogia, conhecimento, aprendizagem, saberes tradicionais, conhecimento baseado na terra, conhecimento local, descolonial*, anticolonial, equidade, antirracismo, racismo, anti-opressão, opressão, anti-discriminação, desenvolvimento infantil, paz, cidadania, ensino da sustentabilidade, educação para a sustentabilidade, literacia universal, numeracia, educação ambiental, educação para o desenvolvimento sustentável, educação ecológica, educação baseada no lugar, educação humanista, aprendizagem baseada na natureza, educação climática, ensino profissional, ensino técnico, educação gratuita, educação acessível, ensino primário, ensino secundário, ensino superior",
    "ODS 5": "género, mulheres, raparigas, queer, feminino, feminis*, não-binário, sexo, LGBTQ*, patriarcado, transgénero, igualdade de género, violência contra mulheres, tráfico humano, casamento forçado",
    "ODS 6": "água, saneamento, contaminação, árido, seca, higiene, águas residuais, escassez de água, remediação, águas não tratadas, captação de água, dessalinização, eficiência hídrica, esgotamento de águas subterrâneas, desertificação, filtragem de água, latrinas, defecação a céu aberto, ciclo hidrológico, gestão de águas pluviais, infraestrutura verde, educação sobre água",
    "ODS 7": "energia, renovável, vento, solar, geotérmica, hidroelétrica, eficiência energética, captura de carbono, emissões, gases com efeito de estufa, biocombustível, soberania energética, segurança energética, educação energética",
    "ODS 8": "emprego, crescimento económico, desenvolvimento sustentável, trabalho, trabalhador, salário, empoderamento económico, empreendedor*, PME, turismo sustentável, emprego jovem, emprego verde, recuperação económica, crescimento verde",
    "ODS 9": "infraestrutura, edifícios, capital, investimento, internet, globalização, industrialização, cadeia de valor, crédito acessível, diversificação industrial",
    "ODS 10": "comércio, desigualdade, mercado financeiro, tributação, equidade, igualdade, ajuda humanitária, minorias, refugiados, indígenas, reconciliação, populações vulneráveis, marginalizado, segurança social, programas governamentais, disparidade, rendimento, coeficiente de gini, antirracismo, descolonização",
    "ODS 11": "cidades, urbano, resiliência, rural, desenvolvimento sustentável, transporte público, habitação, infraestrutura verde, adaptação climática, mitigação climática, edifícios verdes, habitação acessível, mobilidade, espaços públicos, acessibilidade",
    "ODS 12": "consum*, produção, resíduos, recursos naturais, reciclagem, ecologia industrial, design sustentável, cadeia de abastecimento, externalização, reutilização, descarbonização, imposto sobre carbono, preço do carbono, desperdício alimentar, compras públicas, subsídios a combustíveis fósseis",
    "ODS 13": "clima, gases com efeito de estufa, aquecimento global, meteorologia, ambiente, planeta, vegano, vegetariano, antropogénico, combustíveis fósseis, emissões, dióxido de carbono, CO2, neutro em carbono, zero líquido, metano, nível do mar, mitigação climática, adaptação climática, impactos climáticos, justiça climática, modelos climáticos, captura de carbono, sequestro de carbono, baixo carbono, resiliência, antropoceno, mercados de carbono, financiamento climático, acordo de paris",
    "ODS 14": "oceano, marinho, poluição, conservação, pesca, habitat natural, espécies, biodiversidade, coral, marítimo, ecossistema, sobrepesca, stocks de peixe, uso sustentável",
    "ODS 15": "floresta, biodiversidade, ecologia, poluição, conservação, uso do solo, habitat natural, espécies, regeneração, resiliência, restauração ecológica, conservação florestal, sequestro de carbono, solo, erosão, perda de habitat, espécies ameaçadas, desflorestação, reflorestação, vida selvagem, flora e fauna",
    "ODS 16": "instituições, governação, paz, justiça social, injustiça, justiça criminal, direitos humanos, direitos democráticos, sistema legal, mudança social, corrupção, nacionalismo, democracia, autoritarismo, direitos indígenas, autodeterminação, soberania, violência, exploração, tráfico, tortura, estado de direito, crime organizado, terrorismo"
    #"ODS 17": ""
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

    for noticia in newsletter["noticias"]:
        text = noticia["titulo"] + " " + noticia["texto"]

        scores = classify_text(text)

        #relevant = {k: v for k, v in scores.items() if v > 0.35}

        sorted_scores = dict(
            sorted(
                scores.items(),
                key=lambda item: item[1],
                reverse=True
            )
        )

        newsletter_results.append({
            "title": noticia["titulo"],
            "ods": sorted_scores #relevant
        })

        for ods, score in scores.items():
            ods_totals[ods] += score

    results[newsletter_name] = newsletter_results

    total = sum(ods_totals.values())

    if total > 0:
        ods_percentages = {}

        for ods, score in ods_totals.items():
            percentage = (score / total) * 100

            if percentage > 1:
                ods_percentages[ods] = f"{percentage:.2f}%"

    else:
        ods_percentages = {}

    percentage_results[newsletter_name] = ods_percentages

with open("newsletter-analysis.json", "w", encoding="utf-8") as f:
    print("Newsletter analysis completed.")
    json.dump(results, f, ensure_ascii=False, indent=2)

with open("newsletter-percentages.json", "w", encoding="utf-8") as f:
    print("Newsletter percentages completed.")
    json.dump(percentage_results, f, ensure_ascii=False, indent=2)