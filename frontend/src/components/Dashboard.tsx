import React from "react"
import FilterPanel from "./FilterPanel";
import {useEffect, useReducer, useState} from "react";
import {Result} from "../interfaces";
import { Tipo , Ods } from "../types";
import '../styles/Dashboard.css';

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

type State = {
    minDate: string;
    maxDate: string;
    types: string[];
    ods: string[];
};

type PendingFilters = {
    minDate: string;
    maxDate: string;
    types: string[];
    ods: string[];
};

type Action =
    | { type: "apply-filters"; minDate: string; maxDate: string; types: string[]; ods: string[] };

function reducer(state: State, action: Action): State {
    switch (action.type) {
        case "apply-filters":
            return {
                minDate: action.minDate,
                maxDate: action.maxDate,
                types: action.types,
                ods: action.ods,
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
};

export function DashboardFilters() {
    const [state, dispatch] = useReducer(reducer, initialState);
    const [pendingFilters, setPendingFilters] = useState<PendingFilters>({
        minDate: "",
        maxDate: "",
        types: [],
        ods: [],
    });
    const [data, setData] = useState<Result[]>([]);
    const [dashboardData, setDashboardData] = useState<any>(null);

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

            // Load all resultados_ods_*.json files
            for (let i = 1; i <= 7; i++) {
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
        } catch (error) {
            console.error("Error fetching documents data:", error);
        }
    }

    useEffect(() => {
        fetchDocumentsData();
    }, []);

    const getMonthDateRange = (monthStr: string): { startDate: Date; endDate: Date } | null => {
        if (!monthStr) return null;
        const [year, month] = monthStr.split('-');
        const startDate = new Date(parseInt(year), parseInt(month) - 1, 1);
        const endDate = new Date(parseInt(year), parseInt(month), 0);
        return { startDate, endDate };
    };

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

    const generateDashboard = () => {
        // Apply the pending filters
        dispatch({
            type: "apply-filters",
            minDate: pendingFilters.minDate,
            maxDate: pendingFilters.maxDate,
            types: pendingFilters.types,
            ods: pendingFilters.ods
        });

        let filtered = [...data];

        // Date range filter
        if (pendingFilters.minDate || pendingFilters.maxDate) {
            filtered = filtered.filter(item => {
                const itemDate = new Date(item.date);

                if (pendingFilters.minDate) {
                    const minRange = getMonthDateRange(pendingFilters.minDate);
                    if (minRange && itemDate < minRange.startDate) {
                        return false;
                    }
                }

                if (pendingFilters.maxDate) {
                    const maxRange = getMonthDateRange(pendingFilters.maxDate);
                    if (maxRange && itemDate > maxRange.endDate) {
                        return false;
                    }
                }

                return true;
            });
        }

        // Type filter
        if (pendingFilters.types && pendingFilters.types.length > 0) {
            filtered = filtered.filter(item =>
                item.type && pendingFilters.types.includes(item.type)
            );
        }

        // ODS filter
        if (pendingFilters.ods && pendingFilters.ods.length > 0) {
            filtered = filtered.filter(item =>
                item.ods && item.ods.some((odsItem: string) => pendingFilters.ods.includes(odsItem))
            );
        }

        // Count items per ODS
        const odsCount: { [key: string]: number } = {};
        pendingFilters.ods.forEach(ods => {
            odsCount[ods] = 0;
        });

        filtered.forEach(item => {
            if (item.ods) {
                item.ods.forEach(ods => {
                    if (odsCount.hasOwnProperty(ods)) {
                        odsCount[ods]++;
                    }
                });
            }
        });

        // Convert to chart format and sort by ODS number
        const chartData = Object.entries(odsCount)
            .map(([ods, count]) => ({
                name: ods,
                count: count
            }))
            .sort((a, b) => {
                const numA = parseInt(a.name.match(/\d+/)?.[0] || '0');
                const numB = parseInt(b.name.match(/\d+/)?.[0] || '0');
                return numA - numB;
            });

        setDashboardData({
            filters: {
                minDate: pendingFilters.minDate,
                maxDate: pendingFilters.maxDate,
                types: pendingFilters.types,
                ods: pendingFilters.ods,
            },
            totalItems: filtered.length,
            chartData: chartData
        });
    };

    return (
        <div className="dashboard-container">
            <h1>Dashboard de Análise</h1>
            
            <FilterPanel
                onMinDateChange={handleMinDateChange}
                onMaxDateChange={handleMaxDateChange}
                onTypesChange={handleTypesChange}
                onOdsChange={handleOdsChange}
                onApplyFilters={generateDashboard}
                minDate={pendingFilters.minDate}
                maxDate={pendingFilters.maxDate}
                types={pendingFilters.types}
                ods={pendingFilters.ods}
                availableTypes={availableTypes}
                availableOds={availableOds}
                buttonLabel="Gerar Dashboard"
                yearRange={getYearRange()}
            />

            {dashboardData && (
                <div className="dashboard-content">
                    <div className="dashboard-info">
                        <h2>Resultados</h2>
                        <div className="info-grid">
                            <div className="info-card">
                                <span className="info-label">Total de Documentos:</span>
                                <span className="info-value">{dashboardData.totalItems}</span>
                            </div>
                            {dashboardData.filters.minDate && (
                                <div className="info-card">
                                    <span className="info-label">Data Inicial:</span>
                                    <span className="info-value">{dashboardData.filters.minDate}</span>
                                </div>
                            )}
                            {dashboardData.filters.maxDate && (
                                <div className="info-card">
                                    <span className="info-label">Data Final:</span>
                                    <span className="info-value">{dashboardData.filters.maxDate}</span>
                                </div>
                            )}
                        </div>
                    </div>

                    {dashboardData.chartData && dashboardData.chartData.length > 0 && (
                        <div className="dashboard-chart">
                            <h2>Documentos por ODS</h2>
                            <div className="chart-container">
                                {dashboardData.chartData.map((item: any) => (
                                    <div key={item.name} className="chart-bar-item">
                                        <div className="chart-bar-label">{item.name}</div>
                                        <div className="chart-bar-wrapper">
                                            {item.count > 0 && (
                                                <div 
                                                    className="chart-bar" 
                                                    style={{
                                                        width: `${(item.count / Math.max(...dashboardData.chartData.filter((d: any) => d.count > 0).map((d: any) => d.count), 1)) * 100}%`
                                                    }}
                                                >
                                                    <span className="chart-bar-value">{item.count}</span>
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {(!dashboardData.chartData || dashboardData.chartData.length === 0) && (
                        <div className="dashboard-empty">
                            <p>Nenhum dado disponível para os filtros selecionados.</p>
                        </div>
                    )}
                </div>
            )}

            {!dashboardData && (
                <div className="dashboard-placeholder">
                    <p>Selecione os filtros e clique em "Gerar Dashboard" para gerar o dashboard.</p>
                </div>
            )}
        </div>
    );
}
