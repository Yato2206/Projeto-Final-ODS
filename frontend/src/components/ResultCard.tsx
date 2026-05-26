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
                {result.autores && (
                    <p className="result-card-autores">
                        <strong>Autores:</strong> {result.autores}
                    </p>
                )}
                {result.origin && (
                    <p className="result-card-origin">
                        <strong>Origem:</strong> {result.origin}
                    </p>
                )}
                {result.type && (
                    <p className="result-card-type">
                        <strong>Tipo:</strong> {result.type}
                    </p>
                )}
                {result.dateChecked && (
                    <p className="result-card-dateChecked">
                        <strong>Date Checked:</strong> {result.dateChecked}
                    </p>
                )}
            </div>

            <div className="result-card-ods">
                <strong>ODS:</strong> {result.ods && result.ods.length > 0 ? result.ods.join(', ') : 'NULL'}
            </div>
            
            <div className="result-card-footer">
                <a href={String(result.id)} target="_blank" rel="noopener noreferrer" className="result-card-link">Ver mais</a>
            </div>
        </div>
    );
};

export default ResultCard;
