import { Tipo } from "./types";

export interface Ods {
    id: number,
    name: string,
}

export interface Terms {
    id: number,
    odsId: number,
    name: string,
    origin: string,
}

export interface Data {
    id: number,
    odsId: number[],
    type: Tipo,
    origin: string,
}

export interface Result {
    id: number | string;
    name: string;
    date: string;
    origin: string;
    type?: string;
    autores?: string;
    dateChecked: string;
    ods?: string[];
}

export interface FilterObject {
    searchTerm: string,
    ods: Ods[],
    type: any[],
    minDate: any,
    maxDate: any,
}