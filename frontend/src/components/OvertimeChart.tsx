import React from 'react';
import {BarChart, Line, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell} from 'recharts';

type MonthlyData = {
    month: string;
    totalCount: number;
    date: string;
    eachCount: number;
};

interface OvertimeChartComponentProps {
    data: MonthlyData[];
}

const COLORS = [
    '#E5243B', '#DDA63A', '#4C9F38', '#C7212F', '#FF3A21',
    '#26BDE2', '#FCC30B', '#A21942', '#FD6925', '#DD1367',
    '#FD9D24', '#C9992D', '#3F7E44', '#0A97D9', '#56C02B',
    '#00689D', '#19486A'
];

const OvertimeChartComponent: React.FC<OvertimeChartComponentProps> = ({ data }) => {
    return (
        <ResponsiveContainer width="100%" height={600}>
            <BarChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 100 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" angle={-55} textAnchor="end" height={230} />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="totalCount" fill="#CCCCCC" name="Contributions" label={{ position: 'top' }}/>
                <Line dataKey="eachCount" name="Documents" label={{ position: 'top' }}>
                    {data.map((entry, index) => (
                        <Cell
                            key={`cell-${index}`}
                            fill={COLORS[index % COLORS.length]}
                        />
                    ))}
                </Line>
            </BarChart>
        </ResponsiveContainer>
    );
};

export default OvertimeChartComponent;