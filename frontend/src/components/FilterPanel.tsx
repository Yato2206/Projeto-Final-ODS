import React, { useState } from "react"
import '../styles/FilterPanel.css';

interface FilterPanelProps {
    onMinDateChange: (date: string) => void;
    onMaxDateChange: (date: string) => void;
    onTypesChange: (types: string[]) => void;
    onOdsChange: (ods: string[]) => void;
    onOrigensChange: (origens: string[]) => void;
    onApplyFilters: () => void;
    minDate: string;
    maxDate: string;
    types: string[];
    ods: string[];
    origens: string[];
    availableTypes: string[];
    availableOds: string[];
    availableOrigens: string[];
    buttonLabel?: string;
    yearRange?: { minYear: number; maxYear: number };
}

const FilterPanel: React.FC<FilterPanelProps> = ({
    onMinDateChange,
    onMaxDateChange,
    onTypesChange,
    onOdsChange,
    onOrigensChange,
    onApplyFilters,
    minDate,
    maxDate,
    types,
    ods,
    origens,
    availableTypes,
    availableOds,
    availableOrigens,
    buttonLabel = "Aplicar Filtros",
    yearRange
}) => {
    const [isTypesExpanded, setIsTypesExpanded] = useState(true);
    const [isOdsExpanded, setIsOdsExpanded] = useState(true);
    const [isOrigensExpanded, setIsOrigensExpanded] = useState(true);
    const [isFiltersExpanded, setIsFiltersExpanded] = useState(true);

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
        const newMinDate = e.target.value;
        // Only allow if maxDate is not set or if newMinDate is before or equal to maxDate
        if (!maxDate || newMinDate <= maxDate) {
            onMinDateChange(newMinDate);
        }
    };

    const handleMaxDateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const newMaxDate = e.target.value;
        // Only allow if minDate is not set or if newMaxDate is after or equal to minDate
        if (!minDate || newMaxDate >= minDate) {
            onMaxDateChange(newMaxDate);
        }
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

    const handleOrigemChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const origemValue = e.target.value;
        let updatedOrigem: string[];

        if (e.target.checked) {
            updatedOrigem = [...origens, origemValue];
        } else {
            updatedOrigem = origens.filter(o => o !== origemValue);
        }

        onOrigensChange(updatedOrigem);
    };

    const handleSelectAllTypes = () => {
        if (types.length === availableTypes.length) {
            onTypesChange([]);
        } else {
            onTypesChange([...availableTypes]);
        }
    };

    const handleSelectAllOds = () => {
        if (ods.length === availableOds.length) {
            onOdsChange([]);
        } else {
            onOdsChange([...availableOds]);
        }
    };

    return (
        <div className="filter-panel">
            <div className="filter-label-with-button">
                <h2>Filtros</h2>
                <label className="container">
                    <input
                        type="checkbox"
                        checked={isFiltersExpanded}
                        onChange={() => setIsFiltersExpanded(!isFiltersExpanded)}
                    />

                    <svg viewBox="0 0 512 512" height="1em" xmlns="http://www.w3.org/2000/svg"
                         className="chevron-down">
                        <path
                            d="M233.4 406.6c12.5 12.5 32.8 12.5 45.3 0l192-192c12.5-12.5 12.5-32.8 0-45.3s-32.8-12.5-45.3 0L256 338.7 86.6 169.4c-12.5-12.5-32.8-12.5-45.3 0s-12.5 32.8 0 45.3l192 192z"></path>
                    </svg>

                </label>
            </div>

            {isFiltersExpanded && (
                <div>
                    <div className="filter-group">
                        <label htmlFor="min-date">Data inicial (mês/ano):</label>
                        <input
                            id="min-date"
                            type="month"
                            value={minDate}
                            onChange={handleMinDateChange}
                            className="filter-input"
                            min={`${yearRange?.minYear || new Date().getFullYear() - 5}-01`}
                            max={maxDate || getMaxMonthString()}
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
                            min={minDate || `${yearRange?.minYear || new Date().getFullYear() - 5}-01`}
                            max={getMaxMonthString()}
                        />
                    </div>

                        <div className="filter-group">
                            <div className="filter-label-with-button">
                                <label>Tipo:</label>
                                <div className="type-button-group">
                                    {isTypesExpanded && (
                                        <button
                                            className="select-all-button"
                                            onClick={handleSelectAllTypes}
                                        >
                                            {types.length === availableTypes.length ? "Limpar" : "Selecionar tudo"}
                                        </button>
                                    )}
                                    <label className="container">
                                        <input
                                            type="checkbox"
                                            checked={isTypesExpanded}
                                            onChange={() => setIsTypesExpanded(!isTypesExpanded)}
                                        />
                                        <svg viewBox="0 0 512 512" height="1em" xmlns="http://www.w3.org/2000/svg" className="chevron-down">
                                            <path d="M233.4 406.6c12.5 12.5 32.8 12.5 45.3 0l192-192c12.5-12.5 12.5-32.8 0-45.3s-32.8-12.5-45.3 0L256 338.7 86.6 169.4c-12.5-12.5-32.8-12.5-45.3 0s-12.5 32.8 0 45.3l192 192z"></path>
                                        </svg>
                                    </label>
                                </div>
                            </div>

                            {isTypesExpanded && (
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
                            )}
                        </div>

                        <div className="filter-group">
                            <div className="filter-label-with-button">
                                <label>ODS:</label>
                                <div className="ods-button-group">
                                    {isOdsExpanded && (
                                        <button
                                            className="select-all-button"
                                            onClick={handleSelectAllOds}
                                        >
                                            {ods.length === availableOds.length ? "Limpar" : "Selecionar tudo"}
                                        </button>
                                    )}
                                    <label className="container">
                                        <input
                                            type="checkbox"
                                            checked={isOdsExpanded}
                                            onChange={() => setIsOdsExpanded(!isOdsExpanded)}
                                        />
                                        <svg viewBox="0 0 512 512" height="1em" xmlns="http://www.w3.org/2000/svg" className="chevron-down">
                                            <path d="M233.4 406.6c12.5 12.5 32.8 12.5 45.3 0l192-192c12.5-12.5 12.5-32.8 0-45.3s-32.8-12.5-45.3 0L256 338.7 86.6 169.4c-12.5-12.5-32.8-12.5-45.3 0s-12.5 32.8 0 45.3l192 192z"></path>
                                        </svg>
                                    </label>
                                </div>
                            </div>

                            {isOdsExpanded && (
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
                            )}
                        </div>

                    <div className="filter-group">
                        <div className="filter-label-with-button">
                            <label>Origem:</label>
                            <label className="container">
                                <input
                                    type="checkbox"
                                    checked={isOrigensExpanded}
                                    onChange={() => setIsOrigensExpanded(!isOrigensExpanded)}
                                />
                                <svg viewBox="0 0 512 512" height="1em" xmlns="http://www.w3.org/2000/svg" className="chevron-down">
                                    <path d="M233.4 406.6c12.5 12.5 32.8 12.5 45.3 0l192-192c12.5-12.5 12.5-32.8 0-45.3s-32.8-12.5-45.3 0L256 338.7 86.6 169.4c-12.5-12.5-32.8-12.5-45.3 0s-12.5 32.8 0 45.3l192 192z"></path>
                                </svg>
                            </label>
                        </div>

                        {isOrigensExpanded && (
                            <div className="origem-checkboxes">
                                {availableOrigens.map(origemOption => (
                                    <div key={origemOption} className="checkbox-item">
                                        <input
                                            id={`origem-${origemOption}`}
                                            type="checkbox"
                                            value={origemOption}
                                            checked={origens.includes(origemOption)}
                                            onChange={handleOrigemChange}
                                        />
                                        <label htmlFor={`origem-${origemOption}`}>{origemOption}</label>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>

                    <button onClick={onApplyFilters} className="apply-button">
                        {buttonLabel}
                    </button>
                </div>
            )}
        </div>
    );
};

export default FilterPanel;



