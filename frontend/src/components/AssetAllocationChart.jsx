import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';

const COLORS = [
    '#6366f1', // Indigo (Nebula Primary)
    '#0aff68', // Neon Green
    '#00f0ff', // Neon Blue
    '#b829ea', // Neon Purple
    '#f43f5e', // Rose
    '#f59e0b', // Amber
];

const AssetAllocationChart = ({ data, dataKey = 'notional_value', totalNetWorth, groupingMode = 'type' }) => {
    // Group by type or symbol for better visualization
    const groupedData = (data || []).reduce((acc, item) => {
        let key;
        if (groupingMode === 'asset') {
            key = item.symbol || item.name || item.type;
        } else {
            key = item.type;
        }

        if (!acc[key]) {
            acc[key] = { name: key, value: 0 };
        }
        // Use provided dataKey for value
        acc[key].value += (item[dataKey] || 0);
        return acc;
    }, {});

    const chartData = Object.values(groupedData).filter(item => item.value > 0);

    return (
        <ResponsiveContainer width="100%" height="100%">
            <PieChart>
                <Pie
                    data={chartData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={90}
                    paddingAngle={4}
                    dataKey="value"
                    stroke="none"
                    label={({ name, value, percent }) => {
                        return `${name}`;
                    }}
                    labelLine={{ stroke: 'rgba(255, 255, 255, 0.2)', strokeWidth: 1 }}
                >
                    {chartData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} stroke="rgba(0,0,0,0.2)" strokeWidth={2} />
                    ))}
                </Pie>
                <Tooltip
                    contentStyle={{ backgroundColor: 'rgba(21, 25, 37, 0.9)', backdropFilter: 'blur(8px)', borderColor: 'rgba(255, 255, 255, 0.1)', color: '#f1f5f9', borderRadius: '12px', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)' }}
                    itemStyle={{ color: '#f1f5f9', fontFamily: 'Urbanist' }}
                    formatter={(value, name, props) => {
                        const percent = props?.payload?.payload?.percent || props?.payload?.percent || (totalNetWorth ? value / totalNetWorth : 0);
                        return [
                            `${new Intl.NumberFormat('en-US', { style: 'currency', currency: 'TWD', maximumFractionDigits: 0 }).format(value)} (${(percent * 100).toFixed(1)}%)`,
                            name
                        ];
                    }}
                />
                <Legend
                    formatter={(value) => <span style={{ color: '#94a3b8', fontFamily: 'Urbanist', fontSize: '12px' }}>{value}</span>}
                    iconType="circle"
                />
            </PieChart>
        </ResponsiveContainer>
    );
};

export default AssetAllocationChart;
