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
    id: number,
    name: string,
    date: string,
    origin: string,
}

export interface FilterObject {
    searchTerm: string,
    ods: Ods[],
    type: any[],
    minDate: any,
    maxDate: any,
}