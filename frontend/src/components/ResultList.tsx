import React from "react"
import ResultCard from './ResultCard';

import { Result } from '../interfaces'

interface ResultListProps {
    data: Result[],
    selectedTax: string | null;
}

const ResultList: React.FC<ResultListProps> = ({data, selectedTax}) => {
    return (
        <div className="result-list">
            {data.map((result) => (
                <ResultCard result={result}  selectedTax={selectedTax} key={result.id}></ResultCard>
            ))}
        </div>
    )
}

export default ResultList