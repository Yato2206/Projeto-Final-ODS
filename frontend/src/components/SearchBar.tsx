import {useEffect, useReducer, useState} from "react";
import OutputList from "./OutputList";
import FilterPanel from "./FilterPanel";
import {Result} from "../interfaces";
import '../styles/SearchBar.css';

type State = {
    text: string;
    minDate: string;
    maxDate: string;
    // TODO: Add ODS and type when implementing those filters
    // ods: any[];
    // type: any[];
};

type Action =
    | { type: "input-change"; text: string; minDate: string; maxDate: string };

function reducer(state: State, action: Action): State {
    switch (action.type) {
        case "input-change":
            return {
                ...state,
                text: action.text,
                minDate: action.minDate,
                maxDate: action.maxDate,
            };
        default:
            return state;
    }
}

const initialState: State = {
    text: "",
    minDate: "",
    maxDate: "",
};

export function SearchBar() {
    const [state, dispatch] = useReducer(reducer, initialState);
    const [data, setData] = useState<any[]>([]);
    const [filteredData, setFilteredData] = useState<Result[]>([]);

    // Calculate the year range (current year - 5 years to current year)
    const getYearRange = (): { minYear: number; maxYear: number } => {
        const currentYear = new Date().getFullYear();
        const minYear = currentYear - 5;
        return { minYear, maxYear: currentYear };
    };

    // Helper function to extract newsletter number from key
    const getNewsletterNumber = (key: string): string | null => {
        const match = key.match(/#?(\d+)/);
        return match ? match[1] : null;
    };

    // Fetch and merge newsletter content with newsletter dates
    const fetchNewsletterData = async () => {
        try {
            const [contentResponse, newsletterResponse] = await Promise.all([
                fetch('/newsletter-content.json'),
                fetch('/newsletter.json')
            ]);

            if (!contentResponse.ok || !newsletterResponse.ok) {
                throw new Error('Failed to fetch data');
            }

            const contentData = await contentResponse.json();
            const newsletterData = await newsletterResponse.json();

            // Merge the data: use newsletter.json for dates and newsletter-content.json for content
            const mergedData = Object.entries(contentData).map(([key, content]: [string, any]) => {
                // Extract newsletter number to find matching entry
                const contentNumber = getNewsletterNumber(key);
                const newsletterEntry = Object.entries(newsletterData).find(
                    ([newsKey, _]) => getNewsletterNumber(newsKey) === contentNumber
                );

                // Use "date" field from newsletter.json (e.g., "2024-04-19"), not dateChecked
                const newsDate = newsletterEntry ? (newsletterEntry[1] as any).date : content.dateChecked;

                return {
                    id: key,
                    name: content.politecnicoTitulo,
                    date: newsDate,
                    origin: "Politécnico de Lisboa",
                    // TODO: Add ODS and type fields when available
                    // ods: [],
                    // type: undefined,
                };
            });

            // Sort by date descending
            mergedData.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
            setData(mergedData);
        } catch (error) {
            console.error("Error fetching newsletter data:", error);
        }
    }

    // Helper function to convert month input to date range
    const getMonthDateRange = (monthStr: string): { startDate: Date; endDate: Date } | null => {
        if (!monthStr) return null;
        const [year, month] = monthStr.split('-');
        const startDate = new Date(parseInt(year), parseInt(month) - 1, 1);
        const endDate = new Date(parseInt(year), parseInt(month), 0);
        return { startDate, endDate };
    };

    // Filter data based on text and date filters
    const applyFilters = () => {
        let filtered = [...data];

        // Text filter - search in name
        if (state.text.trim()) {
            const searchTerm = state.text.toLowerCase();
            filtered = filtered.filter(item =>
                item.name.toLowerCase().includes(searchTerm)
            );
        }

        // Date range filter - uses "date" field from newsletter.json
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

        // TODO: ODS filter - when ODS data is available
        // if (state.ods && state.ods.length > 0) {
        //     filtered = filtered.filter(item =>
        //         item.ods && state.ods.some(ods => item.ods.includes(ods.id))
        //     );
        // }

        // TODO: Type filter - when Type data is available
        // if (state.type && state.type.length > 0) {
        //     filtered = filtered.filter(item =>
        //         item.type && state.type.includes(item.type)
        //     );
        // }

        setFilteredData(filtered);
    };

    useEffect(() => {
        fetchNewsletterData();
    }, []);

    useEffect(() => {
        applyFilters();
    }, [state, data]);

    const handleTextChange = (text: string) => {
        dispatch({
            type: "input-change",
            text,
            minDate: state.minDate,
            maxDate: state.maxDate
        });
    };

    const handleMinDateChange = (minDate: string) => {
        dispatch({
            type: "input-change",
            text: state.text,
            minDate,
            maxDate: state.maxDate
        });
    };

    const handleMaxDateChange = (maxDate: string) => {
        dispatch({
            type: "input-change",
            text: state.text,
            minDate: state.minDate,
            maxDate
        });
    };

    return (
        <div className="search-bar-container">
            <h1>Pesquisar Newsletters</h1>
            
            <FilterPanel
                onTextChange={handleTextChange}
                onMinDateChange={handleMinDateChange}
                onMaxDateChange={handleMaxDateChange}
                minDate={state.minDate}
                maxDate={state.maxDate}
                yearRange={getYearRange()}
            />

            <div className="results-container">
                <h2>Resultados ({filteredData.length})</h2>
                <OutputList data={filteredData} />
            </div>
        </div>
    )
}