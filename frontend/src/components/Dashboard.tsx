import React from "react"
import FilterPanel from "./FilterPanel";
import {useEffect, useReducer, useState, useRef} from "react";
import { toPng } from "html-to-image";
import {Result} from "../interfaces";
import { getNumberDocs } from "./Utilis";
import { Tipo , Ods , Origens } from "../types";
import * as XLSX from 'xlsx';
import '../styles/Dashboard.css';
import BarChartComponent from "./BarChart";
import AreaChartComponent from "./PieChart";
import OvertimeChart from "./OvertimeChart";

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

function GridItem({ title, children }) {
    return (
        <div className="gridItem">
            <h3>{title}</h3>
            {children}
        </div>
    );
}

export function DashboardScreen() {
    const [state, dispatch] = useReducer(reducer, initialState);
    const [pendingFilters, setPendingFilters] = useState<PendingFilters>({
        minDate: "",
        maxDate: "",
        types: [],
        ods: [],
        origens: [],
    });
    const [data, setData] = useState<Result[]>([]);
    const [dashboardData, setDashboardData] = useState<any>(null);
    const [filteredData, setFilteredData] = React.useState<Result[]>([]);
    const barchartRef = useRef();
    const timechartRef = useRef();
    const piechartRef = useRef();

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

    const handleOrigensChange = (origens: string[]) => {
        setPendingFilters({
            ...pendingFilters,
            origens
        });
    };

    const generateDashboards = () => {

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

        // Origin filter
        if (pendingFilters.origens && pendingFilters.origens.length > 0) {
            filtered = filtered.filter(item =>
                item.origin && pendingFilters.origens.includes(item.origin)
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

        // Data for the Total Contributions by ODS Chart and Pie Chart
        const chartData: Array<{ name: string; count: number }> = Object.entries(odsCount)
            .map(([ods, count]) => ({
                name: ods,
                count: count
            }))
            .sort((a, b) => {
                const numA = parseInt(a.name.match(/\d+/)?.[0] || '0');
                const numB = parseInt(b.name.match(/\d+/)?.[0] || '0');
                return numA - numB;
            });


        // Data for the Total Contributions by Month Chart
        const monthlyCount: { [key: string]: number } = {};
        const monthlyData: Array<{ month: string; totalCount: number; date: string ; eachCount: number }> = [];

        filtered.forEach(item => {
            try {
                const itemDate = new Date(item.date);
                const year = itemDate.getFullYear();
                const month = String(itemDate.getMonth() + 1).padStart(2, '0');
                const monthKey = `${year}-${month}`;

                monthlyCount[monthKey] = (monthlyCount[monthKey] || 0) + 1;
            } catch (error) {
                console.error('Error parsing date:', item.date);
            }
        });

        Object.entries(monthlyCount)
            .sort((a, b) => a[0].localeCompare(b[0]))
            .forEach(([monthKey, totalCount]) => {
                const [year, month] = monthKey.split('-');
                const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
                const monthName = monthNames[parseInt(month) - 1];
                monthlyData.push({
                    month: `${monthName} ${year}`,
                    totalCount: totalCount,
                    date: monthKey,
                    eachCount: chartData.count
                });
            });

        dispatch({
            type: "apply-filters",
            minDate: pendingFilters.minDate,
            maxDate: pendingFilters.maxDate,
            types: pendingFilters.types,
            ods: pendingFilters.ods,
            origens: pendingFilters.origens,
        });

        setFilteredData(filtered);

        setDashboardData({
            filters: {
                minDate: pendingFilters.minDate,
                maxDate: pendingFilters.maxDate,
                types: pendingFilters.types,
                ods: pendingFilters.ods,
                origens: pendingFilters.origens,
            },
            totalItems: filtered.length,
            chartData: chartData,
            monthlyData: monthlyData
        });
    };

    const handleExport = () => {
        const exportData = filteredData.map(item => ({
            "Título": item.name,
            "Tipo": item.type,
            "Origem": item.origin,
            "ODS": item.ods.join("; "),
        }));

        const wb = XLSX.utils.book_new();
        const ws = XLSX.utils.json_to_sheet(exportData);
        XLSX.utils.book_append_sheet(wb, ws, "Documentos");

        const width = [
            { wch: 100 },  // Título
            { wch: 15 },   // Tipo
            { wch: 20 },   // Origem
            { wch: 5 },    // ODS
        ];
        ws['!cols'] = width;

        XLSX.writeFile(wb, `Dashboard_ODS.xlsx`);
    }

    const handleDownload = (ref, filename) => {
        toPng(ref.current, { backgroundColor: '#ffffff' })
            .then((dataUrl) => {
                const link = document.createElement('a')
                link.download = filename;
                link.href = dataUrl;
                link.click();
            }).catch((error) => {
            console.error("Error exporting image:", error);
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
                onOrigensChange={handleOrigensChange}
                onApplyFilters={generateDashboards}
                minDate={pendingFilters.minDate}
                maxDate={pendingFilters.maxDate}
                types={pendingFilters.types}
                ods={pendingFilters.ods}
                origens={pendingFilters.origens}
                availableTypes={availableTypes}
                availableOds={availableOds}
                availableOrigens={availableOrigens}
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

                            <button onClick={handleExport}>
                                Exportar
                            </button>
                        </div>
                    </div>


                    <div className="dashboard-results">
                        <div>
                            <div ref={barchartRef}>
                                <GridItem title="Contribuições aos ODS">
                                    <BarChartComponent data={dashboardData.chartData}/>
                                </GridItem>

                                <div className="info-grid">
                                    <div className="info-card">
                                        <span className="info-label">Total de Documentos:</span>
                                        <span className="info-value">{dashboardData.totalItems}</span>
                                    </div>

                                    <div className="info-card">
                                        <span className="info-label">Tipos de Documentos:</span>
                                        <span className="info-value">{dashboardData.filters.types}</span>
                                    </div>

                                    <div className="info-card">
                                        <span className="info-label">Total de Documentos:</span>
                                        <span className="info-value">{dashboardData.totalItems}</span>
                                    </div>
                                </div>
                            </div>

                            <button onClick={() => handleDownload(barchartRef, "barChartODS.png") }>
                                Download PNG
                            </button>
                        </div>

                        <div>
                            <div ref={timechartRef}>
                                <GridItem title="Contribuições aos ODS por Mês">
                                    <OvertimeChart data={dashboardData.monthlyData} />
                                </GridItem>
                            </div>

                            <button onClick={() => handleDownload(timechartRef, "timeChartODS.png") }>
                                Download PNG
                            </button>
                        </div>

                        <div>
                            <div ref={piechartRef}>
                                <GridItem title="Percentagens de Contribuições">
                                    <AreaChartComponent data={dashboardData.chartData}/>
                                </GridItem>
                            </div>

                            <button onClick={() => handleDownload(piechartRef, "pieChartODS.png") }>
                                Download PNG
                            </button>
                        </div>
                    </div>
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
