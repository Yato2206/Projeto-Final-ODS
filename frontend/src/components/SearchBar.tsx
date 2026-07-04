import React from "react"
import { useEffect , useState } from "react";
import ResultList from "./ResultList";
import FilterPanel from "./FilterPanel";
import { PendingFilters} from "../types";

import {
    taxonomia_names,
    getOdsForTaxonomia,
    fetchDocumentsData,
    filterDocuments
} from "./Utilis";

import { Result } from "../interfaces";
import { Taxonomias } from "../types";
import '../styles/SearchBar.css';
import {usePendingFilters} from "../hooks/usePendingFilters";

const ITEMS_PER_PAGE = 10;

export function SearchBar() {
    const [data, setData] = useState<Result[]>([]);
    const [filteredData, setFilteredData] = useState<Result[]>([]);
    const [currentPage, setCurrentPage] = useState(1);
    const [inputPage, setInputPage] = useState("");
    const {
        pendingFilters,
        handleMinDateChange,
        handleMaxDateChange,
        handleTypesChange,
        handleOdsChange,
        handleOrigensChange,
        handleTaxonomiasChange,
    } = usePendingFilters();

    const applyFilters = () => {
        const { filtered , selectedTax } = filterDocuments(data, pendingFilters);
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
        fetchDocumentsData().then(setData);
        setCurrentPage(1);
    }, []);

    // When data loads initially, show all data
    useEffect(() => {
        if (data.length > 0) {
            setFilteredData(data);
        }
    }, [data]);

    return (
        <div className="search-bar-container">
            <h1>Pesquisar Documentos</h1>
            
            <FilterPanel
                onMinDateChange={handleMinDateChange}
                onMaxDateChange={handleMaxDateChange}
                onTypesChange={handleTypesChange}
                onOdsChange={handleOdsChange}
                onOrigensChange={handleOrigensChange}
                onTaxonomiasChange={handleTaxonomiasChange}
                onApplyFilters={applyFilters}
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
                buttonLabel="Aplicar Filtros"
            />

            <div className="results-container">
                <h2>Resultados ({filteredData.length})</h2>
                <ResultList data={getPageData()} selectedTax={pendingFilters.taxonomias.length > 0 ? taxonomia_names[pendingFilters.taxonomias[0] as Taxonomias] : null} />
                
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