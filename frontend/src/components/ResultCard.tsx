import React from "react"
import { Result } from '../interfaces';
import { formatDateChecked } from "./Utilis";
import '../styles/ResultCard.css';

interface ResultCardProps {
    result: Result;
    selectedTax: string | null;
}

const ResultCard: React.FC<ResultCardProps> = ({ result, selectedTax }) => {
    const formatDate = (dateString: string): string => {
        const date = new Date(dateString);
        if (isNaN(date.getTime())) {
            return "";
        }
        return date.toLocaleDateString('pt-PT', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
        });
    };

    const odsList = selectedTax && result.odsMapeados
        ? result.odsMapeados[selectedTax] ?? []
        : [];

    const joinOdsPercentages = (odsList: string[]) => {
        return odsList.length > 0 ? (
        odsList.map((ods, index) => {
            const percentage = selectedTax && result.odsPercentages?.[selectedTax]?.[ods] !== undefined
                ? result.odsPercentages[selectedTax][ods]
                : 0;

            return (
                <span key={ods}>
                    {ods} ({percentage}%)
                    {index < odsList.length - 1 ? ', ' : ''}
                </span>
            );
        })
    ) : (
        'Nenhuma ODS identificada.'
    )}

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
                        <strong>Date Checked:</strong> {formatDateChecked(result.dateChecked)}
                    </p>
                )}
            </div>

            <div className="result-card-ods">
                <strong>ODS:</strong> { joinOdsPercentages(odsList) }
            </div>
            
            <div className="result-card-footer">
                <a href={String(result.id)} target="_blank" rel="noopener noreferrer" className="result-card-link">Ver mais</a>
            </div>
        </div>
    );
};

export default ResultCard;
