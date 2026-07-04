import { useState } from 'react';
import { PendingFilters} from "../types";

export function usePendingFilters() {
    const [pendingFilters, setPendingFilters] = useState<PendingFilters>({
        minDate: "",
        maxDate: "",
        types: [],
        ods: [],
        origens: [],
        taxonomias: [],
    });

    const handleMinDateChange = (minDate: string) =>
        setPendingFilters(prev => ({ ...prev, minDate }));

    const handleMaxDateChange = (maxDate: string) =>
        setPendingFilters(prev => ({ ...prev, maxDate }));

    const handleTypesChange = (types: string[]) =>
        setPendingFilters(prev => ({ ...prev, types }));

    const handleOdsChange = (ods: string[]) =>
        setPendingFilters(prev => ({ ...prev, ods }));

    const handleOrigensChange = (origens: string[]) =>
        setPendingFilters(prev => ({ ...prev, origens }));

    const handleTaxonomiasChange = (taxonomias: string[]) =>
        setPendingFilters(prev => ({ ...prev, taxonomias, ods: [] }));

    return {
        pendingFilters,
        handleMinDateChange,
        handleMaxDateChange,
        handleTypesChange,
        handleOdsChange,
        handleOrigensChange,
        handleTaxonomiasChange,
    };
}