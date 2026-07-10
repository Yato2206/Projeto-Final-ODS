export interface Result {
    id: number | string;
    name: string;
    date: string;
    origin: string;
    type?: string;
    autores?: string;
    dateChecked: string;
    odsMapeados?: Record<string, string[]>;
    odsPercentages?: Record<string, Record<string, number>>;
    taxonomias?: string[];
    link: string;
}