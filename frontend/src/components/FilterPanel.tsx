import { useState } from "react";
import '../styles/FilterPanel.css';

interface FilterPanelProps {
    onTextChange: (text: string) => void;
    onMinDateChange: (date: string) => void;
    onMaxDateChange: (date: string) => void;
    minDate: string;
    maxDate: string;
    isLoading: boolean;
    yearRange?: { minYear: number; maxYear: number };
}

const FilterPanel: React.FC<FilterPanelProps> = ({
    onTextChange,
    onMinDateChange,
    onMaxDateChange,
    minDate,
    maxDate,
    isLoading,
    yearRange
}) => {
    const [searchText, setSearchText] = useState("");

    // Calculate max month string for HTML5 input constraint
    const getMaxMonthString = (): string => {
        const maxYear = yearRange?.maxYear || new Date().getFullYear();
        const currentMonth = new Date().getMonth() + 1;
        const currentYear = new Date().getFullYear();
        
        // If we're in the current year, limit to current month. Otherwise, use December of max year.
        if (maxYear === currentYear) {
            return `${maxYear}-${String(currentMonth).padStart(2, '0')}`;
        }
        return `${maxYear}-12`;
    };

    const handleTextChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const value = e.target.value;
        setSearchText(value);
        onTextChange(value);
    };

    const handleMinDateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        onMinDateChange(e.target.value);
    };

    const handleMaxDateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        onMaxDateChange(e.target.value);
    };

    return (
        <div className="filter-panel">
            <h2>Filtros</h2>
            
            <div className="filter-group">
                <label htmlFor="search-text">Pesquisar por nome:</label>
                <input
                    id="search-text"
                    type="text"
                    placeholder="Digite o nome da newsletter..."
                    value={searchText}
                    onChange={handleTextChange}
                    className="filter-input"
                />
            </div>

            <div className="filter-group">
                <label htmlFor="min-date">Data inicial (mês/ano):</label>
                <input
                    id="min-date"
                    type="month"
                    value={minDate}
                    onChange={handleMinDateChange}
                    className="filter-input"
                    min={`${yearRange?.minYear || new Date().getFullYear() - 5}-01`}
                    max={getMaxMonthString()}
                />
            </div>

            <div className="filter-group">
                <label htmlFor="max-date">Data final (mês/ano):</label>
                <input
                    id="max-date"
                    type="month"
                    value={maxDate}
                    onChange={handleMaxDateChange}
                    className="filter-input"
                    min={`${yearRange?.minYear || new Date().getFullYear() - 5}-01`}
                    max={getMaxMonthString()}
                />
            </div>

            {/* TODO: ODS Filter - Uncomment and implement when ODS data is available */}
            {/* <div className="filter-group">
                <label htmlFor="ods-select">ODS:</label>
                <Select
                    id="ods-select"
                    options={odsOptions}
                    isMulti
                    onChange={handleOdsChange}
                    className="filter-select"
                />
            </div> */}

            {/* TODO: Type Filter - Uncomment and implement when Type data is available */}
            {/* <div className="filter-group">
                <label htmlFor="type-select">Tipo:</label>
                <Select
                    id="type-select"
                    options={typeOptions}
                    isMulti
                    onChange={handleTypeChange}
                    className="filter-select"
                />
            </div> */}
        </div>
    );
};

export default FilterPanel;




