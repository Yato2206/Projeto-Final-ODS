import React from 'react';
import {BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LabelList} from 'recharts';

type MonthlyData = {
    month: string;
    date: string;
    totalCount: number;
    [odsName: string]: number | string;
};

interface MonthlyOvertimeChartComponentProps {
    data: MonthlyData[];
    relevantOds: string[];
}

const COLORS = [
    '#E5243B', '#DDA63A', '#4C9F38', '#C7212F', '#FF3A21',
    '#26BDE2', '#FCC30B', '#A21942', '#FD6925', '#DD1367',
    '#FD9D24', '#C9992D', '#3F7E44', '#0A97D9', '#56C02B',
    '#00689D', '#19486A'
];

const sortOdsNumerically = (odsArray: string[]): string[] => {
    return [...odsArray].sort((a, b) => {
        const numA = parseInt(a.match(/\d+/)?.[0] || '0');
        const numB = parseInt(b.match(/\d+/)?.[0] || '0');
        return numA - numB;
    });
};

const renderCustomLegend = (sortedOds: string[]) => {
    return (
        <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(4, 1fr)',
            gap: '8px 16px',
            fontFamily: 'Inter, sans-serif',
            fontSize: '13px',
            fontWeight: 'bold',
            paddingTop: '10px',
            maxWidth: '900px',
            margin: '0 auto',
        }}>
            {sortedOds.map((ods, index) => (
                <div key={`legend-item-${index}`} style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <div style={{
                        width: '14px',
                        height: '14px',
                        backgroundColor: COLORS[index % COLORS.length],
                        flexShrink: 0,
                    }} />
                    <span style={{ color: COLORS[index % COLORS.length] }}>
                        {ods}
                    </span>
                </div>
            ))}
        </div>
    );
};

const MonthlyOvertimeChartComponent: React.FC<MonthlyOvertimeChartComponentProps> = ({ data , relevantOds }) => {
    const sortedOds = sortOdsNumerically(relevantOds);

    return (
        <ResponsiveContainer width="100%" height={700}>
            <BarChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 100 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month"/>
                <YAxis />
                <Tooltip />
                <Legend content={() => renderCustomLegend(sortedOds)} />
                {sortedOds.map((ods, index) => {
                    const isLast = index === sortedOds.length - 1;
                    return (
                        <Bar key={ods} dataKey={ods} name={ods} stackId="ods" fill={COLORS[index % COLORS.length]}>
                            {isLast && <LabelList dataKey="totalCount" position="top" fontWeight="bold" />}
                        </Bar>
                    );
                })}
            </BarChart>
        </ResponsiveContainer>
    );
};

export default MonthlyOvertimeChartComponent;