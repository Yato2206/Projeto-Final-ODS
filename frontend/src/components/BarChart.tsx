import React from 'react';
import { BarChart, Bar, Cell, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

type ChartData = {
    name: string,
    count: number
};

interface BarChartComponentProps {
    data: ChartData[];
}

const COLORS = [
    '#E5243B', '#DDA63A', '#4C9F38', '#C7212F', '#FF3A21',
    '#26BDE2', '#FCC30B', '#A21942', '#FD6925', '#DD1367',
    '#FD9D24', '#C9992D', '#3F7E44', '#0A97D9', '#56C02B',
    '#00689D', '#19486A'
];

const BarChartComponent: React.FC<BarChartComponentProps> = ({ data }) => {
    if (!data || data.length === 0) {
        return;
    }

    return (
        <ResponsiveContainer width="100%" height={600}>
                <BarChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 100 }}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis
                        dataKey="name"
                        angle={-55}
                        textAnchor="end"
                        height={230}
                        fontSize={14}
                        fontFamily="Inter, sans-serif"
                        fontWeight="bold"
                    />
                    <YAxis />
                    <Bar
                        dataKey="count"
                        label={{ position: 'top' }}
                    >
                        {data.map((entry, index) => (
                            <Cell
                                key={`cell-${index}`}
                                fill={COLORS[index]}
                            />
                        ))}
                    </Bar>
                    <Tooltip />
                </BarChart>
        </ResponsiveContainer>
    );
};

export default BarChartComponent;