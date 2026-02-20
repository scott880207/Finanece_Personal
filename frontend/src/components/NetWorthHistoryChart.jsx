import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart } from 'recharts';

const NetWorthHistoryChart = ({ data, dataKey = "total_twd", color = "#3b82f6", viewMode = 'total' }) => {
    // Process data to calculate breakdown if needed
    const processedData = (data || []).map(entry => {
        if (viewMode === 'breakdown' && entry.details) {
            let cash = 0;
            let twStock = 0;
            let usStock = 0;

            entry.details.forEach(item => {
                // Calculate value in TWD
                let valueTwd = 0;
                if (item.type === 'TWD') {
                    valueTwd = item.quantity;
                } else if (item.type === 'USD') {
                    valueTwd = item.quantity * (entry.usd_rate || 32.0); // Use entry rate if available, else fallback
                    // Note: entry.usd_rate might not be in history object directly if not stored, 
                    // but usually total_twd / total_usd gives rate if both exist.
                    // Actually, let's look at how value_twd is stored in details.
                    // The details in DB is a JSON snapshot which includes 'value_twd' calculated at that time.
                    // So we should use item.value_twd directly if available.
                    valueTwd = item.value_twd || 0;
                } else {
                    valueTwd = item.value_twd || 0;
                }

                // Categorize
                if (item.type === 'TWD' || item.type === 'USD') {
                    cash += valueTwd;
                } else if (item.type === 'TW_STOCK' || item.type === 'TW_FUTURE') {
                    twStock += valueTwd;
                } else if (item.type === 'US_STOCK') {
                    usStock += valueTwd;
                }
            });

            return {
                ...entry,
                cash_twd: cash,
                tw_stock_twd: twStock,
                us_stock_twd: usStock
            };
        }
        return entry;
    });

    const sortedData = [...processedData].sort((a, b) => new Date(a.date) - new Date(b.date));

    return (
        <ResponsiveContainer width="100%" height="100%">
            {viewMode === 'breakdown' ? (
                <LineChart
                    data={sortedData}
                    margin={{ top: 10, right: 10, left: 0, bottom: 0 }}
                >
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.05)" vertical={false} />
                    <XAxis
                        dataKey="date"
                        stroke="#64748b"
                        tick={{ fill: '#94a3b8', fontSize: 12, fontFamily: 'Urbanist' }}
                        tickFormatter={(str) => new Date(str).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}
                        axisLine={{ stroke: 'rgba(255, 255, 255, 0.1)' }}
                    />
                    <YAxis
                        stroke="#64748b"
                        tick={{ fill: '#94a3b8', fontSize: 12, fontFamily: 'Urbanist' }}
                        tickFormatter={(val) => `${(val / 10000).toFixed(0)}W`}
                        axisLine={false}
                    />
                    <Tooltip
                        contentStyle={{ backgroundColor: 'rgba(21, 25, 37, 0.9)', backdropFilter: 'blur(8px)', borderColor: 'rgba(255, 255, 255, 0.1)', color: '#f1f5f9', borderRadius: '12px', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)' }}
                        labelStyle={{ color: '#94a3b8', fontFamily: 'Urbanist', marginBottom: '0.5rem' }}
                        itemStyle={{ fontFamily: 'Urbanist', padding: '2px 0' }}
                        formatter={(value, name) => [
                            new Intl.NumberFormat('en-US', { style: 'currency', currency: 'TWD', maximumFractionDigits: 0 }).format(value),
                            name === 'cash_twd' ? 'Cash' : name === 'tw_stock_twd' ? 'TW Stock' : name === 'us_stock_twd' ? 'US Stock' : name
                        ]}
                    />
                    <Line type="monotone" dataKey="cash_twd" name="Cash" stroke="#0aff68" strokeWidth={2} dot={false} activeDot={{ r: 6, strokeWidth: 0, fill: '#0aff68' }} />
                    <Line type="monotone" dataKey="tw_stock_twd" name="TW Stock" stroke="#b829ea" strokeWidth={2} dot={false} activeDot={{ r: 6, strokeWidth: 0, fill: '#b829ea' }} />
                    <Line type="monotone" dataKey="us_stock_twd" name="US Stock" stroke="#00f0ff" strokeWidth={2} dot={false} activeDot={{ r: 6, strokeWidth: 0, fill: '#00f0ff' }} />
                </LineChart>
            ) : (
                <AreaChart
                    data={sortedData}
                    margin={{ top: 10, right: 10, left: 0, bottom: 0 }}
                >
                    <defs>
                        <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor={color} stopOpacity={0.4} />
                            <stop offset="95%" stopColor={color} stopOpacity={0} />
                        </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.05)" vertical={false} />
                    <XAxis
                        dataKey="date"
                        stroke="#64748b"
                        tick={{ fill: '#94a3b8', fontSize: 12, fontFamily: 'Urbanist' }}
                        tickFormatter={(str) => new Date(str).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}
                        axisLine={{ stroke: 'rgba(255, 255, 255, 0.1)' }}
                    />
                    <YAxis
                        stroke="#64748b"
                        tick={{ fill: '#94a3b8', fontSize: 12, fontFamily: 'Urbanist' }}
                        tickFormatter={(val) => `${(val / 10000).toFixed(0)}W`}
                        axisLine={false}
                    />
                    <Tooltip
                        contentStyle={{ backgroundColor: 'rgba(21, 25, 37, 0.9)', backdropFilter: 'blur(8px)', borderColor: 'rgba(255, 255, 255, 0.1)', color: '#f1f5f9', borderRadius: '12px', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)' }}
                        labelStyle={{ color: '#94a3b8', fontFamily: 'Urbanist', marginBottom: '0.5rem' }}
                        itemStyle={{ fontFamily: 'Urbanist' }}
                        cursor={{ stroke: 'rgba(255, 255, 255, 0.2)', strokeDasharray: '5 5' }}
                        formatter={(value) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'TWD', maximumFractionDigits: 0 }).format(value)}
                    />
                    <Area type="monotone" dataKey={dataKey} stroke={color} fillOpacity={1} fill="url(#colorValue)" strokeWidth={3} activeDot={{ r: 6, strokeWidth: 0, fill: color }} />
                </AreaChart>
            )}
        </ResponsiveContainer>
    );
};

export default NetWorthHistoryChart;
