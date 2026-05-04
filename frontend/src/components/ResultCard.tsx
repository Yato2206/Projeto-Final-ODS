import { Result } from '../interfaces';
import '../styles/ResultCard.css';

interface ResultCardProps {
    result: Result;
}

const ResultCard: React.FC<ResultCardProps> = ({ result }) => {
    const formatDate = (dateString: string): string => {
        const date = new Date(dateString);
        return date.toLocaleDateString('pt-PT', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
        });
    };

    return (
        <div className="result-card">
            <div className="result-card-header">
                <h3 className="result-card-title">{result.name}</h3>
                <span className="result-card-date">{formatDate(result.date)}</span>
            </div>
            
            <div className="result-card-body">
                {result.origin && (
                    <p className="result-card-origin">
                        <strong>Origem:</strong> {result.origin}
                    </p>
                )}
            </div>

            <div className="result-card-ods">
                <strong>ODS:</strong>  NULL
            </div>
            
            <div className="result-card-footer">
                <a href="#" className="result-card-link">Ver mais</a>
            </div>
        </div>
    );
};

export default ResultCard;
