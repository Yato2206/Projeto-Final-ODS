import {useEffect, useReducer, useState} from "react";
import {useNavigate} from "react-router";
import Select from "react-select";
import {api, ApiError} from "../api";
import OutputList from "./OutputList";
import {useFetch} from "../hooks/useFetch";
import {Result, FilterObject, Ods} from "../interfaces";

const optionsODS = [
    { value: "ods1", label: "ODS 1" },
    { value: "ods2", label: "ODS 2" },
    { value: "ods3", label: "ODS 3" },
    { value: "ods4", label: "ODS 4" },
    { value: "ods5", label: "ODS 5" },
    { value: "ods6", label: "ODS 6" },
    { value: "ods7", label: "ODS 7" },
    { value: "ods8", label: "ODS 8" },
    { value: "ods9", label: "ODS 9" },
    { value: "ods10", label: "ODS 10" },
    { value: "ods11", label: "ODS 11" },
    { value: "ods12", label: "ODS 12" },
    { value: "ods13", label: "ODS 13" },
    { value: "ods14", label: "ODS 14" },
    { value: "ods15", label: "ODS 15" },
    { value: "ods16", label: "ODS 16" },
    { value: "ods17", label: "ODS 17" },
]

const optionsTipo = [
    { value: "tipo1", label: "Ação na Sociedade" },
    { value: "tipo2", label: "Artistico" },
    { value: "tipo3", label: "Cientifico" },
    { value: "tipo4", label: "Ensino" },
]

type State = {
    text: string;
    ods: string,
    tipo: string,
    minDate: Date,
    maxDate: Date,
    stage: "editing" | "getting" | "succeed" | "failed";
    error: string | undefined;
};

type Action =
    | { type: "input-change"; text: string; ods: string; tipo: string, minDate: Date, maxDate: Date }
    | { type: "get" }
    | { type: "success" }
    | { type: "error"; message: string };

function reducer(state: State, action: Action): State {
    switch (action.type) {
        case "input-change":
            return {
                ...state,
                text: action.text,
                ods: action.ods,
                tipo: action.tipo,
                minDate: action.minDate,
                maxDate: action.maxDate,
            };
        case "get":
            return {
                ...state,
                stage: "getting",
                error: undefined
            };
        case "success":
            return {
                ...state,
                text: "",
                ods: "",
                tipo: "",
                minDate: new Date(),
                maxDate: new Date(),
                stage: "succeed",
                error: undefined
            };
        case "error":
            return {
                ...state,
                stage: "failed",
                error: action.message
            };
        default:
            return state;
    }
}

const initialState: State = {
    text: "",
    ods: "",
    tipo: "",
    minDate: new Date(),
    maxDate: new Date(),
    stage: "editing",
    error: undefined,
};

export function SearchBar() {
    const [state, dispatch] = useReducer(reducer, initialState);
    const navigate = useNavigate();
    const [text, setText] = useState("");
    const [odsPicked, setOdsPicked] = useState("");
    const [typePicked, setTypePicked] = useState("");
    const [minDatePicked, setMinDatePicked] = useState(new Date());
    const [maxDatePicked, setMaxDatePicked] = useState(new Date());

    const { fetchJsonData } = useFetch();
    const [data, setData] = useState<any[]>([]);
    const [filteredData, setFilteredData] = useState<Result[]>([]);

    const [filters, setFilters] = useState<FilterObject>({
        searchTerm: "",
        ods: [],
        type: [],
        minDate: "",
        maxDate: "",
    })

    const sortAndFilterResults = (filterObj: FilterObject) => {
        return data.filter(item => {
            return (item.results.some((result: Result) => result.name.toLowerCase().indexOf(filterObj.searchTerm.toLowerCase()) > -1)) &&
                (filterObj.ods.length === 0 || filterObj.ods.some(ods => item.ods.includes(ods.id))) &&
                (filterObj.type.length === 0 || filterObj.type.some(type => item.type.includes(type))) &&
                (filterObj.minDate === "" || new Date(item.date) >= new Date(filterObj.minDate)) &&
                (filterObj.maxDate === "" || new Date(item.date) <= new Date(filterObj.maxDate))
        })
    }

    useEffect(() => {
        filepaths.forEach(fetchJsonData(it, setData))
    }), [])

    useEffect(() => {
        const data = sortAndFilterRecipes(filters);
        setFilteredData(data)
    }, [filters, data])


    const handleSearch = async(e: React.FormEvent) => {
        e.preventDefault();
        dispatch({type: "get"})

        try {
            const response = await api.getResults();

            navigate("results");
        } catch (err) {
            if (err instanceof ApiError) {
                dispatch({type: "error", message: err.message});
            } else {
                dispatch({
                    type: "error",
                    message: "An error occurred during login",
                });
            }
        }
    }

    return (
        <div>
            <h1>Search Bar</h1>
            <div>
                <input type="text" onChange={(value) => {
                    dispatch({type: "input-change", text: value, ods: state.ods, tipo: state.tipo, minDate: state.minDate, maxDate: state.maxDate})
                    setText(value)}
                } />
            </div>

            <div>
                <Select
                    options={optionsODS}
                    isMulti
                    onChange={(option) => {
                        dispatch({type: "input-change", text: state.text, ods: option.map((o) => o.value).join(","), tipo: state.tipo, minDate: state.minDate, maxDate: state.maxDate})
                        setOdsPicked(option)
                    }
                    }
                />
            </div>

            <div>
                <Select
                    options={optionsTipo}
                    isMulti
                    onChange={(option) => {
                        dispatch({type: "input-change", text: state.text, ods: state.ods, tipo: option.map((o) => o.value).join(","), minDate: state.minDate, maxDate: state.maxDate})
                        setTypePicked(option)
                    }
                    }
                />
            </div>

            <div>
                <input
                    type="date"
                    value={minDatePicked.toISOString().split("T")[0]}
                    onChange={(e) => {
                        dispatch({type: "input-change", text: state.text, ods: state.ods, tipo: state.tipo, minDate: new Date(e.target.value), maxDate: state.maxDate})
                        setMinDatePicked(new Date(e.target.value))}
                }
                    max={maxDatePicked.toISOString().split("T")[0]}
                />
            </div>

            <div>
                <input
                    type="date"
                    value={maxDatePicked.toISOString().split("T")[0]}
                    max={new Date().toISOString().split("T")[0]}
                    onChange={(e) => {
                            if (minDatePicked.toISOString().split("T")[0] > e.target.value) {
                                dispatch({type: "input-change", text: state.text, ods: state.ods, tipo: state.tipo, minDate: new Date(e.target.value), maxDate: new Date(e.target.value)})
                                setMinDatePicked(new Date(e.target.value))
                                setMaxDatePicked(new Date(e.target.value))
                            } else {
                                dispatch({type: "input-change", text: state.text, ods: state.ods, tipo: state.tipo, minDate: state.minDate, maxDate: new Date(e.target.value)})
                                setMaxDatePicked(new Date(e.target.value))
                            }
                        }
                    }
                />
            </div>

            <div>
                <button
                    onClick={() => {handleSearch}}
                    disabled={state.stage === "getting"}
                >
                    Search
                </button>
            </div>

            <div>
                <OutputList
                    data={filteredData}
                />
            </div>
        </div>
    )
}