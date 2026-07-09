import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LabelList } from 'recharts';
import { COLORS , sortOdsNumerically} from "./Utilis";

type YearlyData = {
    year: string;
    totalCount: number;
    [odsName: string]: number | string;
};

interface YearlyOvertimeChartComponentProps {
    data: YearlyData[];
    relevantOds: string[];
}

const CustomTooltip = ({active, payload, label, sortedOds}: any) => {
    if (active && payload && payload.length) {
        const payloadMap = new Map(payload.map((p: any) => [p.dataKey, p]));
        return (
            <div className={"custom-tooltip"}>
                <p style={{ fontWeight: 'bold', marginBottom: '6px' }}>{label}</p>
                {sortedOds.map((ods: string) => {
                    const entry = payloadMap.get(ods);
                    if (!entry) return null;
                    return (
                        <p key={ods} style={{ color: entry.color, margin: '2px 0' }}>
                            {ods}: {entry.value}
                        </p>
                    );
                })}
            </div>
        )
    }
}

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


const YearlyOvertimeChartComponent: React.FC<YearlyOvertimeChartComponentProps> = ({ data, relevantOds }) => {
    const sortedOds = sortOdsNumerically(relevantOds);

    const chartData = data.map(d => {
        const stackTotal = sortedOds.reduce((sum, ods) => sum + (Number(d[ods]) || 0), 0);
        return { ...d, labelAnchor: 0.0001, stackTotal: stackTotal };
    });

    return (
        <ResponsiveContainer width="100%" height={500}>
            <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 40 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="year"/>
                <YAxis />
                <Tooltip content={<CustomTooltip sortedOds={sortedOds} />} wrapperStyle={{ zIndex: 1000 }}/>
                <Legend content={() => renderCustomLegend(sortedOds)} />
                {sortedOds.map((ods, index) => (
                    <Bar key={ods} dataKey={ods} name={ods} stackId="ods" fill={COLORS[index % COLORS.length]} />
                ))}

                <Bar dataKey="labelAnchor" stackId="ods" fill="transparent" isAnimationActive={false}>
                    <LabelList dataKey="stackTotal" position="top" fontWeight="bold" />
                </Bar>
            </BarChart>
        </ResponsiveContainer>
    );
};

export default YearlyOvertimeChartComponent;