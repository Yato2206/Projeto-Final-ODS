import React from "react"
import {useEffect, useReducer, useState} from "react";
import OutputList from "./OutputList";
import FilterPanel from "./FilterPanel";
import { getNumberDocs } from "./Utilis";
import {Result} from "../interfaces";
import { Tipo , Ods , Origens } from "../types";
import '../styles/SearchBar.css';

const ITEMS_PER_PAGE = 10;
const availableTypes: Tipo[] = ["Ação na sociedade", "Artístico", "Artigo científico", "Ensino", "Newsletter", "Outro"];
const availableOds: Ods[] = [
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
]
const availableOrigens: Origens[] = ["Repositório Científico", "Newsletter", "Scopus"];

type State = {
    minDate: string;
    maxDate: string;
    types: string[];
    ods: string[];
    origens: string[];
};

type PendingFilters = {
    minDate: string;
    maxDate: string;
    types: string[];
    ods: string[];
    origens: string[];
};

type Action =
    | { type: "apply-filters"; minDate: string; maxDate: string; types: string[]; ods: string[]; origens: string[] };

function reducer(state: State, action: Action): State {
    switch (action.type) {
        case "apply-filters":
            return {
                minDate: action.minDate,
                maxDate: action.maxDate,
                types: action.types,
                ods: action.ods,
                origens: action.origens,
            };
        default:
            return state;
    }
}

const initialState: State = {
    minDate: "",
    maxDate: "",
    types: [],
    ods: [],
    origens: [],
};

export function SearchBar() {
    const [state, dispatch] = useReducer(reducer, initialState);
    const [pendingFilters, setPendingFilters] = useState<PendingFilters>({
        minDate: "",
        maxDate: "",
        types: [],
        ods: [],
        origens: [],
    });
    const [data, setData] = useState<Result[]>([]);
    const [filteredData, setFilteredData] = useState<Result[]>([]);
    const [currentPage, setCurrentPage] = useState(1);
    const [inputPage, setInputPage] = useState("");

    // Calculate the year range (current year - 5 years to current year)
    const getYearRange = (): { minYear: number; maxYear: number } => {
        const currentYear = new Date().getFullYear();
        const minYear = currentYear - 5;
        return { minYear, maxYear: currentYear };
    };

    // Map document tipo to predefined type, defaulting to "Outro"
    const mapTipoToType = (tipo: string): Tipo => {
        if (availableTypes.includes(tipo as Tipo)) {
            return tipo as Tipo;
        }
        return "Outro";
    };

    // Fetch all formatted documents
    const fetchDocumentsData = async () => {
        try {
            const formattedDocs: Result[] = [];
            const odsSet = new Set<string>();

            // Load all resultados_ods_parte_*.json files
            for (let i = 1; i <= await getNumberDocs(); i++) {
                try {
                    const response = await fetch(`/resultados_ods_${i}.json`);
                    if (response.ok) {
                        const data = await response.json();
                        
                        Object.entries(data).forEach(([key, value]: [string, any]) => {
                            const ods = value.ods_mapeados ? Object.keys(value.ods_mapeados) : [];
                            
                            // Extract ODS numbers for the filter
                            ods.forEach((odsKey: string) => {
                                odsSet.add(odsKey);
                            });

                            const doc: Result = {
                                id: key,
                                name: value.titulo,
                                date: value.dataPublicacao,
                                type: mapTipoToType(value.tipo),
                                autores: value.autores,
                                origin: value.origem,
                                dateChecked: value.dateChecked,
                                ods: ods,
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
            setData(formattedDocs);
            // Set available ODS sorted
            setCurrentPage(1);
        } catch (error) {
            console.error("Error fetching documents data:", error);
        }
    }

    const getMonthDateRange = (monthStr: string): { startDate: Date; endDate: Date } | null => {
        if (!monthStr) return null;
        const [year, month] = monthStr.split('-');
        const startDate = new Date(parseInt(year), parseInt(month) - 1, 1);
        const endDate = new Date(parseInt(year), parseInt(month), 0);
        return { startDate, endDate };
    };

    const applyFilters = () => {
        let filtered = [...data];

        // Date range filter
        if (state.minDate || state.maxDate) {
            filtered = filtered.filter(item => {
                const itemDate = new Date(item.date);

                if (state.minDate) {
                    const minRange = getMonthDateRange(state.minDate);
                    if (minRange && itemDate < minRange.startDate) {
                        return false;
                    }
                }

                if (state.maxDate) {
                    const maxRange = getMonthDateRange(state.maxDate);
                    if (maxRange && itemDate > maxRange.endDate) {
                        return false;
                    }
                }

                return true;
            });
        }

        // Type filter
        if (state.types && state.types.length > 0) {
            filtered = filtered.filter(item =>
                item.type && state.types.includes(item.type)
            );
        }

        // ODS filter - check if any selected ODS is present in item.ods
        if (state.ods && state.ods.length > 0) {
            filtered = filtered.filter(item =>
                item.ods && item.ods.some((odsItem: string) => state.ods.includes(odsItem))
            );
        }

        // Origin filter
        if (state.origens && state.origens.length > 0) {
            filtered = filtered.filter(item =>
                item.origin && state.origens.includes(item.origin)
            );
        }

        setFilteredData(filtered);
        setCurrentPage(1);
    };

    const getPageData = () => {
        const startIndex = (currentPage - 1) * ITEMS_PER_PAGE;
        const endIndex = startIndex + ITEMS_PER_PAGE;
        return filteredData.slice(startIndex, endIndex);
    };

    const getTotalPages = () => {
        return Math.ceil(filteredData.length / ITEMS_PER_PAGE);
    };

    const handleFirstPage = () => {
        if (currentPage > 1) {
            setCurrentPage(1);
        }
    };

    const handlePreviousPage = () => {
        if (currentPage > 1) {
            setCurrentPage(currentPage - 1);
        }
    };

    const handlePageChange = (pageNumber: number) => {
        setCurrentPage(pageNumber);
    };

    const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
        if (e.key === "Enter") {
            const pageNum = parseInt(inputPage, 10);
            const totalPages = getTotalPages();

            if (!isNaN(pageNum) && pageNum >= 1 && pageNum <= totalPages) {
                handlePageChange(pageNum);
                setInputPage(""); // Optional: clear input after submitting
            } else {
                alert(`Please enter a valid page between 1 and ${totalPages}`);
            }
        }
    };

    const handleNextPage = () => {
        if (currentPage < getTotalPages()) {
            setCurrentPage(currentPage + 1);
        }
    };

    const handleLastPage = () => {
        if (currentPage < getTotalPages()) {
            setCurrentPage(getTotalPages());
        }
    };


    useEffect(() => {
        fetchDocumentsData();
    }, []);

    // When data loads initially, show all data
    useEffect(() => {
        if (data.length > 0) {
            setFilteredData(data);
        }
    }, [data]);

    // When state filters change (after Apply button is clicked), apply filters
    useEffect(() => {
        applyFilters();
    }, [state]);

    const handleMinDateChange = (minDate: string) => {
        setPendingFilters({
            ...pendingFilters,
            minDate
        });
    };

    const handleMaxDateChange = (maxDate: string) => {
        setPendingFilters({
            ...pendingFilters,
            maxDate
        });
    };

    const handleTypesChange = (types: string[]) => {
        setPendingFilters({
            ...pendingFilters,
            types
        });
    };

    const handleOdsChange = (ods: string[]) => {
        setPendingFilters({
            ...pendingFilters,
            ods
        });
    };

    const handleOrigensChange = (origens: string[]) => {
        setPendingFilters({
            ...pendingFilters,
            origens
        });
    };

    const handleApplyFilters = () => {
        dispatch({
            type: "apply-filters",
            minDate: pendingFilters.minDate,
            maxDate: pendingFilters.maxDate,
            types: pendingFilters.types,
            ods: pendingFilters.ods,
            origens: pendingFilters.origens,
        });
    };

    return (
        <div className="search-bar-container">
            <h1>Pesquisar Documentos</h1>
            
            <FilterPanel
                onMinDateChange={handleMinDateChange}
                onMaxDateChange={handleMaxDateChange}
                onTypesChange={handleTypesChange}
                onOdsChange={handleOdsChange}
                onOrigensChange={handleOrigensChange}
                onApplyFilters={handleApplyFilters}
                minDate={pendingFilters.minDate}
                maxDate={pendingFilters.maxDate}
                types={pendingFilters.types}
                ods={pendingFilters.ods}
                origens={pendingFilters.origens}
                availableTypes={availableTypes}
                availableOds={availableOds}
                availableOrigens={availableOrigens}
                buttonLabel="Aplicar Filtros"
                yearRange={getYearRange()}
            />

            <div className="results-container">
                <h2>Resultados ({filteredData.length})</h2>
                <OutputList data={getPageData()} />
                
                {getTotalPages() > 1 && (
                    <div className="pagination-controls">

                        <button
                            onClick={handleFirstPage}
                            disabled={currentPage === 1}
                            className="pagination-button"
                            title="Página anterior"
                        >
                            ˂˂
                        </button>

                        <button
                            onClick={handlePreviousPage}
                            disabled={currentPage === 1}
                            className="pagination-button"
                            title="Página anterior"
                        >
                            ˂ Anterior
                        </button>

                        <span className="pagination-info">
                            Página
                            <input
                                type="number"
                                className="page-input"
                                min="1"
                                max={getTotalPages()}
                                value={inputPage}
                                placeholder={currentPage.toString()}
                                onChange={(e) => setInputPage(Number(e.target.value))}
                                onKeyDown={handleKeyDown}
                            />
                            de {getTotalPages()}
                        </span>

                        <button
                            onClick={handleNextPage}
                            disabled={currentPage === getTotalPages()}
                            className="pagination-button"
                            title="Próxima página"
                        >
                            Próxima ˃
                        </button>

                        <button
                            onClick={handleLastPage}
                            disabled={currentPage === getTotalPages()}
                            className="pagination-button"
                            title="Próxima página"
                        >
                            ˃˃
                        </button>

                    </div>
                )}
            </div>
        </div>
    )
}