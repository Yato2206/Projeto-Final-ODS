import React from "react"
import FilterPanel from "./FilterPanel";
import { useEffect , useState , useRef } from "react";
import { usePendingFilters } from "../hooks/usePendingFilters"
import { toPng , toSvg } from "html-to-image";
import { Result } from "../interfaces";
import * as XLSX from 'xlsx';
import '../styles/Dashboard.css';
import BarChartComponent from "./BarChart";
import AreaChartComponent from "./PieChart";
import MonthlyOvertimeChart from "./MonthlyOvertimeChart";
import YearlyOvertimeChart from "./YearlyOvertimeChart";
import {
    getTaxonomiaName,
    getDefaultDateRange,
    formatDateChecked,
    getOdsForTaxonomia,
    fetchDocumentsData,
    filterDocuments,
} from "./Utilis";
import {Taxonomias} from "../types";


function GridItem({ title, children }) {
    return (
        <div className="gridItem">
            <h3>{title}</h3>
            {children}
        </div>
    );
}

export function DashboardScreen() {
    const [data, setData] = useState<Result[]>([]);
    const [dashboardData, setDashboardData] = useState<any>(null);
    const [filteredData, setFilteredData] = React.useState<Result[]>([]);
    const barchartRef = useRef();
    const monthlytimechartRef = useRef();
    const yearlytimechartRef = useRef();
    const piechartRef = useRef();
    const { minDate: defaultMinDate, maxDate: defaultMaxDate } = getDefaultDateRange();
    const {
        pendingFilters,
        handleMinDateChange,
        handleMaxDateChange,
        handleTypesChange,
        handleOdsChange,
        handleOrigensChange,
        handleTaxonomiasChange,
    } = usePendingFilters();

    useEffect(() => {
        fetchDocumentsData().then(setData);
    }, []);

    const generateDashboards = () => {
        const { filtered, selectedTax } = filterDocuments(data, pendingFilters);

        // Count items per ODS
        const odsCount: { [key: string]: number } = {};
        const relevantOds = selectedTax ? getOdsForTaxonomia(data, pendingFilters.taxonomias[0]) : [];
        relevantOds.forEach(ods => {
            odsCount[ods] = 0;
        });

        filtered.forEach(item => {
            const itemOds = selectedTax && item.odsMapeados ? item.odsMapeados[selectedTax] : undefined;
            if (itemOds) {
                itemOds.forEach(ods => {
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


        // Data for the OverTimeMonthlyChart
        const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        const hasMonth = (dateStr: string): boolean => /^\d{4}-\d{2}/.test(dateStr);
        const itemsWithMonth = filtered.filter(item => hasMonth(item.date));

        const monthlyDataMap: { [monthKey: string]: any } = {};

        itemsWithMonth.forEach(item => {
            try {
                const itemDate = new Date(item.date);
                if (isNaN(itemDate.getTime())) {
                    return;
                }

                const year = itemDate.getFullYear();
                const month = String(itemDate.getMonth() + 1).padStart(2, '0');;
                const monthKey = `${year}-${month}`;

                if (!monthlyDataMap[monthKey]) {
                    monthlyDataMap[monthKey] = {
                        month: `${monthNames[itemDate.getMonth()]} ${year}`,
                        date: monthKey,
                        totalCount: 0
                    };
                    relevantOds.forEach(ods => {
                        monthlyDataMap[monthKey][ods] = 0
                    });
                }

                monthlyDataMap[monthKey].totalCount++;

                const itemOds = selectedTax && item.odsMapeados ? item.odsMapeados[selectedTax] : undefined;
                if (itemOds) {
                    itemOds.forEach(ods => {
                        if (monthlyDataMap[monthKey].hasOwnProperty(ods)) {
                            monthlyDataMap[monthKey][ods]++
                        }
                    });
                }
            } catch (error) {
                console.error("Error getting date:", item.date);
            }
        });

        const monthlyData = Object.entries(monthlyDataMap)
            .sort((a,b) => a[0].localeCompare(b[0]))
            .map(([, v]) => v);


        // Data for the OverTimeYearlyChart
        const yearlyDataMap: { [yearKey: string]: any } = {};

        filtered.forEach(item => {
            try {
                const itemDate = new Date(item.date);
                if (isNaN(itemDate.getTime())) {
                    return;
                }

                const yearKey = String(itemDate.getFullYear());

                if (!yearlyDataMap[yearKey]) {
                    yearlyDataMap[yearKey] = { year: yearKey, totalCount: 0 };
                    relevantOds.forEach(ods => { yearlyDataMap[yearKey][ods] = 0; });
                }

                yearlyDataMap[yearKey].totalCount++;

                const itemOds = selectedTax && item.odsMapeados ? item.odsMapeados[selectedTax] : undefined;
                if (itemOds) {
                    itemOds.forEach(ods => {
                        if (yearlyDataMap[yearKey].hasOwnProperty(ods)) {
                            yearlyDataMap[yearKey][ods]++;
                        }
                    });
                }
            } catch (error) {
                console.error('Error parsing date:', item.date);
            }
        });

        const yearlyData = Object.entries(yearlyDataMap)
            .sort((a, b) => a[0].localeCompare(b[0]))
            .map(([, v]) => v);


        setFilteredData(filtered);

        setDashboardData({
            filters: {
                minDate: pendingFilters.minDate,
                maxDate: pendingFilters.maxDate,
                types: pendingFilters.types,
                ods: pendingFilters.ods,
                origens: pendingFilters.origens,
                taxonomias: pendingFilters.taxonomias,
            },
            selectedTax: selectedTax,
            totalItems: filtered.length,
            chartData: chartData,
            monthlyData: monthlyData,
            yearlyData: yearlyData,
            relevantOds: relevantOds,
        });
    };

    const handleExport = () => {
        const taxonomia = dashboardData?.selectedTax;

        const exportData = filteredData.map(item => ({
            "Link": item.id,
            "Titulo": item.name,
            "Tipo": item.type,
            "Origem": item.origin,
            "Data": item.date,
            "Verificado": formatDateChecked(item.dateChecked),
            "ODS": taxonomia && item.odsMapeados?.[taxonomia]
                ? item.odsMapeados[taxonomia].join("; ")
                : "",
        }));

        const wb = XLSX.utils.book_new();
        const ws = XLSX.utils.json_to_sheet(exportData);
        XLSX.utils.book_append_sheet(wb, ws, "Documentos");

        const width = [
            { wch: 20 },   // Link
            { wch: 100 },  // Título
            { wch: 15 },   // Tipo
            { wch: 20 },   // Origem
            { wch: 12 },   // Data
            { wch: 17 },   // Verificado
            { wch: 5 },    // ODS
        ];
        ws['!cols'] = width;

        if(taxonomia) {
            const relevantOds = getOdsForTaxonomia(data, dashboardData.filters.taxonomias[0]);

            relevantOds.forEach((odsName) => {
                const filterForOds = filteredData.filter(item =>
                    item.odsMapeados?.[taxonomia]?.includes(odsName)
                );

                if (filterForOds.length === 0) return

                const exportOds = filterForOds.map(item => ({
                    "Link": item.id,
                    "Titulo": item.name,
                    "Tipo": item.type,
                    "Origem": item.origin,
                    "Data": item.date,
                    "Verificado": formatDateChecked(item.dateChecked)
                }));

                const odsWs = XLSX.utils.json_to_sheet(exportOds);
                odsWs['!cols'] = width;

                const sheetName = odsName
                    .replace(/[\\/?*[\]:]/g, "")
                    .substring(0, 31);

                XLSX.utils.book_append_sheet(wb, odsWs, sheetName);
            });
        }

        XLSX.writeFile(wb, `Dashboard_ODS.xlsx`);
    }

    const handleDownloadPng = (ref, filename) => {
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
    const handleDownloadSvg = (ref, filename) => {
        toSvg(ref.current, { backgroundColor: '#ffffff' })
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
                onTaxonomiasChange={handleTaxonomiasChange}
                onApplyFilters={generateDashboards}
                minDate={pendingFilters.minDate}
                maxDate={pendingFilters.maxDate}
                types={pendingFilters.types}
                ods={pendingFilters.ods}
                origens={pendingFilters.origens}
                taxonomias={pendingFilters.taxonomias}
                availableOds={
                    pendingFilters.taxonomias.length === 1
                        ? getOdsForTaxonomia(data, pendingFilters.taxonomias[0])
                        : []
                }
                buttonLabel="Gerar Dashboard"
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
                                        <span className="info-label">Data Inicial:</span>
                                        <span className="info-value">{dashboardData.filters.minDate || defaultMinDate}</span>
                                    </div>

                                    <div className="info-card">
                                        <span className="info-label">Data Final:</span>
                                        <span className="info-value">{dashboardData.filters.maxDate || defaultMaxDate}</span>
                                    </div>

                                    <div className="info-card">
                                        <span className="info-label">Taxonomia:</span>
                                        <span className="info-value">{getTaxonomiaName(dashboardData.selectedTax)}</span>
                                    </div>
                                </div>
                            </div>

                            <button onClick={() => handleDownloadPng(barchartRef, "barChartODS.png") }>
                                Download as PNG
                            </button>

                            <button onClick={() => handleDownloadSvg(barchartRef, "barChartODS.svg") }>
                                Download as SVG
                            </button>
                        </div>

                        { dashboardData.monthlyData.length > 1 && (
                            <div>
                                <div ref={monthlytimechartRef}>
                                    <GridItem title="Contribuições aos ODS por Mês">
                                        <MonthlyOvertimeChart data={dashboardData.monthlyData}  relevantOds={dashboardData.relevantOds} />
                                    </GridItem>

                                    <div className="info-grid">
                                        <div className="info-card">
                                            <span className="info-label">Taxonomia:</span>
                                            <span className="info-value">{getTaxonomiaName(dashboardData.selectedTax)}</span>
                                        </div>
                                    </div>
                                </div>

                                <button onClick={() => handleDownloadPng(monthlytimechartRef, "monthlyOvertimeChartODS.png") }>
                                    Download as PNG
                                </button>

                                <button onClick={() => handleDownloadSvg(monthlytimechartRef, "monthlyOvertimeChartODS.svg") }>
                                    Download as SVG
                                </button>
                            </div>
                        )}

                        { dashboardData.yearlyData.length > 1 && (
                            <div>
                                <div ref={yearlytimechartRef}>
                                    <GridItem title="Contribuições aos ODS por Ano">
                                        <YearlyOvertimeChart data={dashboardData.yearlyData}  relevantOds={dashboardData.relevantOds} />
                                    </GridItem>

                                    <div className="info-grid">
                                        <div className="info-card">
                                            <span className="info-label">Taxonomia:</span>
                                            <span className="info-value">{getTaxonomiaName(dashboardData.selectedTax)}</span>
                                        </div>
                                    </div>
                                </div>

                                <button onClick={() => handleDownloadPng(yearlytimechartRef, "yearlyOvertimeChartODS.png") }>
                                    Download as PNG
                                </button>

                                <button onClick={() => handleDownloadSvg(yearlytimechartRef, "yearlyOvertimeChartODS.svg") }>
                                    Download as SVG
                                </button>
                            </div>
                        )}

                        <div>
                            <div ref={piechartRef}>
                                <GridItem title="Percentagens de Contribuições">
                                    <AreaChartComponent data={dashboardData.chartData}/>
                                </GridItem>

                                <div className="info-grid">
                                    <div className="info-card">
                                        <span className="info-label">Data Inicial:</span>
                                        <span className="info-value">{dashboardData.filters.minDate || defaultMinDate}</span>
                                    </div>

                                    <div className="info-card">
                                        <span className="info-label">Data Final:</span>
                                        <span className="info-value">{dashboardData.filters.maxDate || defaultMaxDate}</span>
                                    </div>

                                    <div className="info-card">
                                        <span className="info-label">Taxonomia:</span>
                                        <span className="info-value">{getTaxonomiaName(dashboardData.selectedTax)}</span>
                                    </div>
                                </div>
                            </div>

                            <button onClick={() => handleDownloadPng(piechartRef, "pieChartODS.png") }>
                                Download as PNG
                            </button>

                            <button onClick={() => handleDownloadSvg(piechartRef, "pieChartODS.svg") }>
                                Download as SVG
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
