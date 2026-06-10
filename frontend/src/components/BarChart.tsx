import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

type ChartData = {
    name: string,
    count: number
};

interface BarChartComponentProps {
    data: ChartData[];
}

const BarChartComponent: React.FC<BarChartComponentProps> = ({ data }) => {
    if (!data || data.length === 0) {
        return <div>Nenhum dado disponível para os filtros selecionados. (Selecione pelo menos 1 ODS)</div>;
    }

    return (
        <ResponsiveContainer width="100%" height={600}>
            <BarChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 100 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" angle={-55} textAnchor="end" height={230} />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="count" fill="#8884d8" name="Documentos" label={{ position: 'top' }}/>
            </BarChart>
        </ResponsiveContainer>
    );
};

export default BarChartComponent;