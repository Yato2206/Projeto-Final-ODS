import React from 'react';
import { PieChart, Pie , Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';
import '../styles/PieChart.css';
import odsLogo from "../assets/odsLogo.png"

const COLORS = [
    '#E5243B', '#DDA63A', '#4C9F38', '#C7212F', '#FF3A21',
    '#26BDE2', '#FCC30B', '#A21942', '#FD6925', '#DD1367',
    '#FD9D24', '#C9992D', '#3F7E44', '#0A97D9', '#56C02B',
    '#00689D', '#19486A'
];

const renderCustomizedLabel = ({
    cx,
    cy,
    midAngle,
    innerRadius,
    outerRadius,
    percent
}: {
    cx: number;
    cy: number;
    midAngle: number;
    innerRadius: number;
    outerRadius: number;
    percent: number;
}) => {
    if (percent < 0.035) return null;

    const RADIAN = Math.PI / 180;
    const radius = innerRadius + (outerRadius - innerRadius) * 0.5;
    const x = cx + radius * Math.cos(-midAngle * RADIAN);
    const y = cy + radius * Math.sin(-midAngle * RADIAN);

    return (
        <text
            x={x}
            y={y}
            fill={"white"}
            fontSize={16}
            fontWeight="bold"
            fontFamily="Inter, sans-serif"
            textAnchor="middle"
            dominantBaseline="central"
        >
            {`${(percent * 100).toFixed(1)}%`}
        </text>
    )
}

const renderCustomLegend = (data) => {
    return (
        <div className={"custom-legend"}
        style={{
            flexDirection: 'column',
            fontFamily: 'Inter, sans-serif',
            fontSize: '14px',
            fontWeight: 'bold',
        }}
        >
            {data.map((entry, index) => (
                <div key={`legend-item-${index}`} style={{ display: 'flex', alignItems: 'center', gap: '7px' }}>
                    <div style={{
                        width: '16px',
                        height: '16px',
                        backgroundColor: COLORS[index % COLORS.length]
                    }} />
                    <span style={{ color: COLORS[index % COLORS.length] }}>
                        {entry.name}
                    </span>
                </div>
            ))}
        </div>
    );
};

const CustomTooltip = ({active, payload}: any) => {
    if (active && payload && payload.length) {
        return (
            <div className={"custom-tooltip"}>
                <p className="label">
                    {payload[0].name}: {payload[0].value}
                </p>
            </div>
        )
    }
}

const PieChartComponent = ({ data }) => {
    if (!data || data.length === 0) {
        return;
    }

    return (
        <div style={{ display: 'flex', alignItems: 'center' }}>
            <div style={{ position: 'relative', width: 650, height: 600 }}>
                <PieChart width={650} height={600}>
                    <Pie
                        data={data}
                        dataKey="count"
                        label={renderCustomizedLabel}
                        labelLine={false}
                        innerRadius={125}
                        outerRadius={200}
                        isAnimationActive={false}
                    >
                        {data.map((entry: any, index: number) => (
                            <Cell key={`cell-${index}`} fill={COLORS[index]} />
                        ))}
                    </Pie>
                    <Tooltip content={<CustomTooltip />} wrapperStyle={{ zIndex: 1000 }}/>
                </PieChart>

                <img
                    src={odsLogo}
                    alt="ODS logo"
                    style={{
                        position: 'absolute',
                        top: '50%',
                        left: '50%',
                        transform: 'translate(-50%, -50%)',
                        width: 200,
                        height: 200,
                        pointerEvents: 'none',
                        zIndex: 1,
                    }}
                />
            </div>

            <div style={{
                display: 'flex',
                flexDirection: 'column',
                fontFamily: 'Inter, sans-serif',
                fontSize: '14px',
                fontWeight: 'bold',
                gap: '5px',
            }}>
                {data.map((entry: any, index: number) => (
                    <div key={`legend-item-${index}`} style={{ display: 'flex', alignItems: 'center', gap: '7px' }}>
                        <div style={{ width: '16px', height: '16px', backgroundColor: COLORS[index % COLORS.length] }} />
                        <span style={{ color: COLORS[index % COLORS.length] }}>{entry.name}</span>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default PieChartComponent;