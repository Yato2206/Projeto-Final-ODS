import { Result } from "../interfaces";
import { Tipo , Ods , Origens , Taxonomias , PendingFilters } from "../types";

export const availableTypes: Tipo[] = [
    "Ação na sociedade",
    "Artístico",
    "Artigo Científico",
    "Ensino",
    "Newsletter",
    "Noticia da Newsletter",
    "Licenciatura",
    "Mestrado",
    "Pos-Graduação",
    "Outro"
];

export const availableOds: Ods[] = [
    "ODS 1 - Erradicar a Pobreza",
    "ODS 2 - Erradicar a Fome",
    "ODS 3 - Saúde de Qualidade",
    "ODS 4 - Educação de Qualidade",
    "ODS 5 - Igualdade de Género",
    "ODS 6 - Água Potável e Saneamento",
    "ODS 7 - Energias Renováveis e Acessíveis",
    "ODS 8 - Trabalho Digno e Crescimento Económico",
    "ODS 9 - Indústria, Inovação e Infraestruturas",
    "ODS 10 - Reduzir as Desigualdades",
    "ODS 11 - Cidades e Comunidades Sustentáveis",
    "ODS 12 - Produção e Consumo Sustentáveis",
    "ODS 13 - Ação Climática",
    "ODS 14 - Proteger a Vida Marinha",
    "ODS 15 - Proteger a Vida Terrestre",
    "ODS 16 - Paz, Justiça e Instituições Eficazes",
    "ODS 17 - Parcerias para a Implementação dos Objetivos"
];

export const availableOrigens: Origens[] = ["Repositório Científico", "Newsletter", "Scopus", "Orcid"];

export const availableTaxonomias: Taxonomias[] = [
    "Universidade de Auckland",
    "Universidade de Educação de Hong Kong",
    "Universidade de Monash"
];

export const taxonomia_names: Record<Taxonomias, string> = {
    "Universidade de Auckland": "UoA",
    "Universidade de Educação de Hong Kong": "HK",
    "Universidade de Monash": "Msh",
};


export const COLORS = [
    '#E5243B', '#DDA63A', '#4C9F38', '#C7212F', '#FF3A21',
    '#26BDE2', '#FCC30B', '#A21942', '#FD6925', '#DD1367',
    '#FD9D24', '#C9992D', '#3F7E44', '#0A97D9', '#56C02B',
    '#00689D', '#19486A'
];

// Calculate the year range (current year - 5 years to current year)
export function getYearRange(): { minYear: number; maxYear: number } {
    const currentYear = new Date().getFullYear();
    return { minYear: currentYear - 5, maxYear: currentYear };
}

// Map document tipo to predefined type, defaulting to "Outro"
export function mapTipoToType(tipo: string): Tipo {
    if (availableTypes.includes(tipo as Tipo)) {
        return tipo as Tipo;
    }
    return "Outro";
}

//
export function getMonthDateRange(monthStr: string): { startDate: Date; endDate: Date } | null {
    if (!monthStr) return null;
    const [year, month] = monthStr.split('-');
    const startDate = new Date(parseInt(year), parseInt(month) - 1, 1);
    const endDate = new Date(parseInt(year), parseInt(month), 0);
    return { startDate, endDate };
}

// Get the name of a taxonomy from the code
export function getTaxonomiaName(code: string | null): string {
    if (!code) return "";
    const entry = Object.entries(taxonomia_names).find(([, c]) => c === code);
    return entry ? entry[0] : code;
}

// Get the minDate and maxDate values, when no filter is selected
export function getDefaultDateRange(): { minDate: string; maxDate: string } {
    const { minYear, maxYear } = getYearRange();
    const currentMonth = new Date().getMonth() + 1;
    const currentYear = new Date().getFullYear();

    const maxDate = maxYear === currentYear
        ? `${String(currentMonth).padStart(2, '0')}-${maxYear}`
        : `12$-${maxYear}`;

    return { minDate: `01-${minYear}`, maxDate };
}

export function sortOdsNumerically(odsArray: string[]): string[] {
    return [...odsArray].sort((a, b) => {
        const numA = parseInt(a.match(/\d+/)?.[0] || '0');
        const numB = parseInt(b.match(/\d+/)?.[0] || '0');
        return numA - numB;
    });
};

//2026-06-30T17:31:22.502087+00:00 => 30/06/2026 17:31
export function formatDateChecked(date: string): string {
    if(!date) return "";
    const newDate = new Date(date);

    const day = String(newDate.getDate()).padStart(2, '0');
    const month = String(newDate.getMonth() + 1).padStart(2, '0');
    const year = newDate.getFullYear();
    const hour = String(newDate.getHours()).padStart(2, '0');
    const minutes = String(newDate.getMinutes()).padStart(2, '0');

    return `${day}/${month}/${year} ${hour}:${minutes}`;
};

// Returns the ODS options that are actually present in `data` for a given taxonomia
export function getOdsForTaxonomia(data: Result[], taxonomiaName: string): string[] {
    if (!taxonomiaName) return [];
    const code = taxonomia_names[taxonomiaName as Taxonomias];
    const odsSet = new Set<string>();

    data.forEach(item => {
        if (item.odsMapeados && item.odsMapeados[code]) {
            item.odsMapeados[code].forEach(o => odsSet.add(o));
        }
    });

    return availableOds.filter(ods => odsSet.has(ods));
}

export async function getNumberDocs(): Promise<number> {
        const response = await fetch(`index.json`);
        const data = await response.json();
        return data.count || 0;
    }

// Returns the information from the documents with the analyzed data
export async function fetchDocumentsData(): Promise<Result[]> {
    const formattedDocs: Result[] = [];

    // Load all resultados_ods_*.json files
    for (let i = 1; i <= await getNumberDocs(); i++) {
        try {
            const response = await fetch(`/resultados_ods_${i}.json`);
            if (response.ok) {
                const data = await response.json();

                Object.entries(data).forEach(([key, value]: [string, any]) => {
                    const odsMapeados: Record<string, string[]> = {};
                    const odsPercentages: Record<string, Record<string, number>> = {};
                    const taxonomiasDoc: string[] = [];

                    const name = value.titulo ? value.titulo : value.curso;

                    if (value.ods_mapeados) {
                        Object.entries(value.ods_mapeados).forEach(([taxCode, odsObj]) => {
                            const odsCounts = odsObj as Record<string, number> | undefined;
                            const odsList = odsObj ? Object.keys(odsObj as object) : [];
                            odsMapeados[taxCode] = odsList;

                            const total = odsList.reduce((sum, ods) => sum + odsCounts![ods], 0);

                            const percentages: Record<string, number> = {};
                            odsList.forEach(ods => {
                                percentages[ods] = total > 0
                                    ? Math.round((odsCounts![ods] / total) * 1000) / 10   // 1 casa decimal
                                    : 0;
                            });
                            odsPercentages[taxCode] = percentages;

                            if (odsList.length > 0) {
                                taxonomiasDoc.push(taxCode);
                            }
                        });
                    }

                    const doc: Result = {
                        id: key,
                        name: name,
                        date: value.dataPublicacao,
                        type: mapTipoToType(value.tipo),
                        autores: value.autores,
                        origin: value.origem,
                        dateChecked: value.dateChecked,
                        odsMapeados: odsMapeados,
                        odsPercentages: odsPercentages,
                        taxonomias: taxonomiasDoc,
                        link: value.link || key,
                    };
                    formattedDocs.push(doc);
                });
            }
        } catch (error) {
            console.error(`Error loading resultados_ods_${i}.json:`, error);
        }
    }

    console.log("Loaded documents:", formattedDocs.length);
    // Sort by date descending
    formattedDocs.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
    return formattedDocs;
}

export function filterDocuments(data: Result[], filters: PendingFilters): { filtered: Result[], selectedTax: string | null } {
    let filtered = [...data];

    if (filters.minDate || filters.maxDate) {
        filtered = filtered.filter(item => {
            const itemDate = new Date(item.date);
            if (filters.minDate) {
                const minRange = getMonthDateRange(filters.minDate);
                if (minRange && itemDate < minRange.startDate) return false;
            }
            if (filters.maxDate) {
                const maxRange = getMonthDateRange(filters.maxDate);
                if (maxRange && itemDate > maxRange.endDate) return false;
            }
            return true;
        });
    }

    if (filters.types && filters.types.length > 0) {
        filtered = filtered.filter(item => item.type && filters.types.includes(item.type));
    }

    let selectedTax: string | null = null;
    if (filters.taxonomias && filters.taxonomias.length > 0) {
        selectedTax = taxonomia_names[filters.taxonomias[0] as Taxonomias];
        filtered = filtered.filter(item => item.taxonomias && item.taxonomias.includes(selectedTax!));
    }

    if (selectedTax && filters.ods && filters.ods.length > 0) {
        filtered = filtered.filter(item =>
            item.odsMapeados?.[selectedTax!]?.some((o: string) => filters.ods.includes(o))
        );
    }

    if (filters.origens && filters.origens.length > 0) {
        filtered = filtered.filter(item => item.origin && filters.origens.includes(item.origin));
    }

    return { filtered, selectedTax };
}