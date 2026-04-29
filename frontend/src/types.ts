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
    type: "ACAO_NA_SOCIEDADE" | "ARTISTICO" | "CIENTIFICO" | "ENSINO" | "UNDEFINED",
    origin: string,
}
