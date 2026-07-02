export interface Result {
    id: number | string;
    name: string;
    date: string;
    origin: string;
    type?: string;
    autores?: string;
    dateChecked: string;
    odsMapeados?: Record<string, string[]>;
    taxonomias?: string[];

}