
import ResultCard from './ResultCard';

import { Result } from '../interfaces'

interface OutputListProps {
    data: Result[]
}

const OutputList: React.FC<OutputListProps> = ({data}) => {
    return (
        <div className="result-list">
            {data.map((result) => (
                <ResultCard result={result} key={result.id}></ResultCard>
            ))}
        </div>
    )
}

export default OutputList