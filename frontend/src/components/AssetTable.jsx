import React, { useState } from 'react';
import { Trash2, Save } from 'lucide-react';
import api from '../api';

const AssetTable = ({ assets, onDelete, onUpdate, usdRate, totalNetWorth }) => {
    const [editingId, setEditingId] = useState(null);
    const [tempLeverage, setTempLeverage] = useState({});

    const handleDelete = async (id) => {
        if (window.confirm('Are you sure you want to delete this asset?')) {
            try {
                await api.delete(`/assets/${id}`);
                onDelete();
            } catch (error) {
                console.error("Error deleting asset", error);
            }
        }
    };

    const handleLeverageChange = (id, value) => {
        setTempLeverage({ ...tempLeverage, [id]: value });
        setEditingId(id);
    };

    const saveLeverage = async (asset) => {
        const newLeverage = parseFloat(tempLeverage[asset.id]);
        if (isNaN(newLeverage)) return;

        try {
            await api.put(`/assets/${asset.id}`, {
                ...asset,
                leverage: newLeverage
            });
            setEditingId(null);
            onUpdate();
        } catch (error) {
            console.error("Error updating leverage", error);
        }
    };

    const calculatePnL = (asset) => {
        if (!asset.value_twd) return null;

        let totalCostTwd = 0;
        if (asset.currency === 'USD') {
            totalCostTwd = asset.cost * asset.quantity * usdRate;
        } else {
            totalCostTwd = asset.cost * asset.quantity;
        }

        return asset.value_twd - totalCostTwd;
    };

    return (
        <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
                <thead>
                    <tr className="text-slate-400 border-b border-white/10 text-xs uppercase tracking-wider">
                        <th className="p-4 font-bold">Type</th>
                        <th className="p-4 font-bold">Symbol</th>
                        <th className="p-4 font-bold text-right">Quantity</th>
                        <th className="p-4 font-bold text-right">Avg Cost</th>
                        <th className="p-4 font-bold text-right">Notional Value</th>
                        <th className="p-4 font-bold text-right">Equity</th>
                        <th className="p-4 font-bold text-right">Leverage</th>
                        <th className="p-4 font-bold text-right">Unweighted %</th>
                        <th className="p-4 font-bold text-right">Weighted %</th>
                        <th className="p-4 font-bold text-right">Unrealized P&L</th>
                        <th className="p-4 font-bold text-center">Actions</th>
                    </tr>
                </thead>
                <tbody className="divide-y divide-white/5">
                    {[...assets].sort((a, b) => {
                        const priority = {
                            'TW_STOCK': 1,
                            'US_STOCK': 2,
                            'TWD': 3,
                            'USD': 4
                        };
                        const pA = priority[a.type] || 5;
                        const pB = priority[b.type] || 5;
                        return pA - pB;
                    }).map((asset) => {
                        // Use backend provided P&L if available, otherwise fallback
                        const pnl = asset.pnl !== undefined ? asset.pnl : calculatePnL(asset);
                        const isPositive = pnl >= 0;

                        // Calculate Allocations
                        const unweightedAlloc = totalNetWorth > 0 && asset.equity ? (asset.equity / totalNetWorth) * 100 : 0;
                        const weightedAlloc = totalNetWorth > 0 && asset.notional_value ? (asset.notional_value / totalNetWorth) * 100 : 0;

                        return (
                            <tr key={asset.id} className="group hover:bg-white/5 transition-colors">
                                <td className="p-4">
                                    <span className={`px-2.5 py-1 rounded-md text-xs font-bold tracking-wide 
                      ${asset.type === 'TWD' ? 'bg-green-500/10 text-green-400 border border-green-500/20' :
                                            asset.type === 'USD' ? 'bg-blue-500/10 text-blue-400 border border-blue-500/20' :
                                                asset.type === 'TW_STOCK' ? 'bg-purple-500/10 text-purple-400 border border-purple-500/20' :
                                                    asset.type === 'TW_FUTURE' ? 'bg-red-500/10 text-red-400 border border-red-500/20' :
                                                        'bg-orange-500/10 text-orange-400 border border-orange-500/20'}`}>
                                        {asset.type}
                                    </span>
                                </td>
                                <td className="p-4 font-medium text-white group-hover:text-nebula-300 transition-colors">
                                    {asset.name || asset.symbol || '-'}
                                    {asset.type === 'TW_FUTURE' && <span className="block text-xs text-slate-500 font-mono mt-0.5">{asset.symbol} {asset.contract_month}</span>}
                                </td>
                                <td className="p-4 text-right text-slate-300 font-mono">{asset.quantity.toLocaleString()}</td>
                                <td className="p-4 text-right text-slate-400 font-mono">{asset.cost ? asset.cost.toLocaleString() : '-'}</td>
                                <td className="p-4 text-right text-slate-200 font-mono font-medium">
                                    {asset.notional_value ? asset.notional_value.toLocaleString(undefined, { maximumFractionDigits: 0 }) : '-'}
                                </td>
                                <td className="p-4 text-right font-bold text-white font-mono">
                                    {asset.equity ? asset.equity.toLocaleString(undefined, { maximumFractionDigits: 0 }) : (asset.value_twd ? asset.value_twd.toLocaleString(undefined, { maximumFractionDigits: 0 }) : '-')}
                                </td>
                                <td className="p-4 text-right">
                                    <div className="flex items-center justify-end gap-2">
                                        {asset.type === 'TW_FUTURE' ? (
                                            <span className={`font-bold font-mono ${asset.leverage > 2 ? 'text-red-400' : 'text-green-400'}`}>
                                                {asset.leverage ? `${asset.leverage.toFixed(2)}x` : '-'}
                                            </span>
                                        ) : (
                                            <input
                                                type="number"
                                                step="0.1"
                                                className="w-16 bg-black/20 border border-white/10 rounded px-2 py-1 text-right text-slate-200 focus:outline-none focus:border-nebula-500 focus:ring-1 focus:ring-nebula-500 font-mono transition-all"
                                                value={tempLeverage[asset.id] !== undefined ? tempLeverage[asset.id] : (asset.leverage || (asset.type === 'TWD' || asset.type === 'USD' ? 0 : 1))}
                                                onChange={(e) => handleLeverageChange(asset.id, e.target.value)}
                                                onBlur={() => saveLeverage(asset)}
                                                onKeyDown={(e) => {
                                                    if (e.key === 'Enter') saveLeverage(asset);
                                                }}
                                            />
                                        )}
                                    </div>
                                </td>
                                <td className="p-4 text-right text-slate-400 font-mono">
                                    {unweightedAlloc.toFixed(1)}%
                                </td>
                                <td className="p-4 text-right text-slate-400 font-mono">
                                    {weightedAlloc.toFixed(1)}%
                                </td>
                                <td className={`p-4 text-right font-bold font-mono ${isPositive ? 'text-neon-green' : 'text-red-400'}`}>
                                    {pnl !== null ? (
                                        <>
                                            {pnl > 0 ? '+' : ''}{pnl.toLocaleString(undefined, { maximumFractionDigits: 0 })}
                                            <span className={`text-xs ml-1 font-medium ${isPositive ? 'text-green-500/70' : 'text-red-500/70'}`}>
                                                ({asset.pnl_percentage ? (asset.pnl_percentage > 0 ? '+' : '') + asset.pnl_percentage.toFixed(1) : '0.0'}%)
                                            </span>
                                        </>
                                    ) : '-'}
                                </td>
                                <td className="p-4 text-center">
                                    <button
                                        onClick={() => handleDelete(asset.id)}
                                        className="p-2 text-slate-600 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-all"
                                        title="Delete Asset"
                                    >
                                        <Trash2 size={16} />
                                    </button>
                                </td>
                            </tr>
                        );
                    })}
                </tbody>
            </table>
        </div>
    );
};

export default AssetTable;
