import { useState } from "react";
import '../styles/FilterPanel.css';

interface FilterPanelProps {
    onMinDateChange: (date: string) => void;
    onMaxDateChange: (date: string) => void;
    onTypesChange: (types: string[]) => void;
    onOdsChange: (ods: string[]) => void;
    onApplyFilters: () => void;
    minDate: string;
    maxDate: string;
    types: string[];
    ods: string[];
    availableTypes: string[];
    availableOds: string[];
    buttonLabel?: string;
    yearRange?: { minYear: number; maxYear: number };
}

const FilterPanel: React.FC<FilterPanelProps> = ({
    onMinDateChange,
    onMaxDateChange,
    onTypesChange,
    onOdsChange,
    onApplyFilters,
    minDate,
    maxDate,
    types,
    ods,
    availableTypes,
    availableOds,
    buttonLabel = "Aplicar Filtros",
    yearRange
}) => {

    const getMaxMonthString = (): string => {
        const maxYear = yearRange?.maxYear || new Date().getFullYear();
        const currentMonth = new Date().getMonth() + 1;
        const currentYear = new Date().getFullYear();

        if (maxYear === currentYear) {
            return `${maxYear}-${String(currentMonth).padStart(2, '0')}`;
        }
        return `${maxYear}-12`;
    };

    const handleMinDateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        onMinDateChange(e.target.value);
    };

    const handleMaxDateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        onMaxDateChange(e.target.value);
    };

    const handleTypeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const typeValue = e.target.value;
        let updatedTypes: string[];

        if (e.target.checked) {
            updatedTypes = [...types, typeValue];
        } else {
            updatedTypes = types.filter(t => t !== typeValue);
        }

        onTypesChange(updatedTypes);
    };

    const handleOdsChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const odsValue = e.target.value;
        let updatedOds: string[];

        if (e.target.checked) {
            updatedOds = [...ods, odsValue];
        } else {
            updatedOds = ods.filter(o => o !== odsValue);
        }

        onOdsChange(updatedOds);
    };

    const handleSelectAllOds = () => {
        if (ods.length === availableOds.length) {
            // Deselect all
            onOdsChange([]);
        } else {
            // Select all
            onOdsChange([...availableOds]);
        }
    };

    return (
        <div className="filter-panel">
            <h2>Filtros</h2>

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

            <div className="filter-group">
                <label>Tipo:</label>
                <div className="type-checkboxes">
                    {availableTypes.map(typeOption => (
                        <div key={typeOption} className="checkbox-item">
                            <input
                                id={`type-${typeOption}`}
                                type="checkbox"
                                value={typeOption}
                                checked={types.includes(typeOption)}
                                onChange={handleTypeChange}
                            />
                            <label htmlFor={`type-${typeOption}`}>{typeOption}</label>
                        </div>
                    ))}
                </div>
            </div>

            <div className="filter-group">
                <div className="filter-label-with-button">
                    <label>ODS:</label>
                    <button 
                        onClick={handleSelectAllOds}
                        className="select-all-button"
                        title={ods.length === availableOds.length ? "Desselecionar todos" : "Selecionar todos"}
                    >
                        {ods.length === availableOds.length ? "Desselecionar tudo" : "Selecionar tudo"}
                    </button>
                </div>
                <div className="ods-checkboxes">
                    {availableOds.map(odsOption => (
                        <div key={odsOption} className="checkbox-item">
                            <input
                                id={`ods-${odsOption}`}
                                type="checkbox"
                                value={odsOption}
                                checked={ods.includes(odsOption)}
                                onChange={handleOdsChange}
                            />
                            <label htmlFor={`ods-${odsOption}`}>{odsOption}</label>
                        </div>
                    ))}
                </div>
            </div>

            <button onClick={onApplyFilters} className="apply-button">
                {buttonLabel}
            </button>
        </div>
    );
};

export default FilterPanel;



