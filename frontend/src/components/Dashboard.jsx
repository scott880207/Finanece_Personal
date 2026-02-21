import React, { useState, useEffect } from 'react';
import api from '../api';
import AssetTable from './AssetTable';
import RealizedPnLTable from './RealizedPnLTable';
import AssetAllocationChart from './AssetAllocationChart';
import NetWorthHistoryChart from './NetWorthHistoryChart';
import ImportHistoryModal from './ImportHistoryModal';
import { Plus, RefreshCw, History, TrendingUp, Upload } from 'lucide-react';
import AddAssetModal from './AddAssetModal';
import { filterDataByTimeRange } from '../utils/dateFilter';

const Dashboard = () => {
    const [assets, setAssets] = useState([]);
    const [netWorth, setNetWorth] = useState(null);
    const [history, setHistory] = useState([]);
    const [pnlHistory, setPnlHistory] = useState([]);
    const [cumulativePnl, setCumulativePnl] = useState([]);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [loading, setLoading] = useState(true);
    const [isImportModalOpen, setIsImportModalOpen] = useState(false);

    // Unified View Mode: 'assets' or 'pnl'
    const [viewMode, setViewMode] = useState('assets');
    // Allocation Chart Mode: 'weighted' or 'unweighted'
    const [allocationMode, setAllocationMode] = useState('unweighted');
    // Grouping Mode: 'type' or 'asset'
    const [groupingMode, setGroupingMode] = useState('type');
    // History View Mode: 'total' or 'breakdown'
    const [historyViewMode, setHistoryViewMode] = useState('total');
    // Time Range Filter: '3M', '1Y', 'ALL'
    const [timeRange, setTimeRange] = useState('3M');

    const fetchData = async () => {
        setLoading(true);
        try {
            const [assetsRes, netWorthRes, historyRes, pnlHistoryRes, cumulativePnlRes] = await Promise.all([
                api.get('/assets/'),
                api.get('/net-worth/current'),
                api.get('/net-worth/history'),
                api.get('/pnl/history'),
                api.get('/pnl/cumulative')
            ]);
            setAssets(assetsRes.data);
            setNetWorth(netWorthRes.data);
            setHistory(historyRes.data);
            setPnlHistory(pnlHistoryRes.data);
            setCumulativePnl(cumulativePnlRes.data);
        } catch (error) {
            console.error("Error fetching data", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, []);

    const filteredHistory = filterDataByTimeRange(history, timeRange);
    const filteredCumulativePnl = filterDataByTimeRange(cumulativePnl, timeRange);

    return (
        <div className="space-y-8">
            {/* Header & Toggle */}
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                <h2 className="text-3xl font-bold font-display text-white tracking-tight">
                    {viewMode === 'assets' ? 'Overview' : 'Performance Analysis'}
                </h2>
                <div className="flex bg-slate-900/50 backdrop-blur-sm p-1 rounded-xl border border-white/10">
                    <button
                        onClick={() => setViewMode('assets')}
                        className={`px-6 py-2.5 text-sm font-semibold rounded-lg transition-all duration-300 ${viewMode === 'assets' ? 'bg-nebula-500 text-white shadow-lg shadow-nebula-500/25' : 'text-slate-400 hover:text-white hover:bg-white/5'}`}
                    >
                        Assets
                    </button>
                    <button
                        onClick={() => setViewMode('pnl')}
                        className={`px-6 py-2.5 text-sm font-semibold rounded-lg transition-all duration-300 ${viewMode === 'pnl' ? 'bg-nebula-500 text-white shadow-lg shadow-nebula-500/25' : 'text-slate-400 hover:text-white hover:bg-white/5'}`}
                    >
                        Realized P&L
                    </button>
                </div>
            </div>

            {/* Top Stats */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
                <div className="glass-panel p-6 relative overflow-hidden group">
                    <div className="absolute top-0 right-0 w-32 h-32 bg-nebula-500/10 rounded-full blur-2xl -mr-16 -mt-16 group-hover:bg-nebula-500/20 transition-all duration-500"></div>
                    <h3 className="text-slate-400 text-xs font-bold uppercase tracking-widest mb-1">Total Net Worth</h3>
                    <div className="flex items-baseline relative z-10">
                        <span className="text-4xl font-bold font-display text-white text-glow-blue">
                            {netWorth ? netWorth.total_twd.toLocaleString(undefined, { maximumFractionDigits: 0 }) : '...'}
                        </span>
                        <span className="ml-2 text-xs font-mono text-nebula-300">TWD</span>
                    </div>
                </div>

                <div className="glass-panel p-6 relative overflow-hidden group">
                    <div className="absolute top-0 right-0 w-32 h-32 bg-purple-500/10 rounded-full blur-2xl -mr-16 -mt-16 group-hover:bg-purple-500/20 transition-all duration-500"></div>
                    <h3 className="text-slate-400 text-xs font-bold uppercase tracking-widest mb-1">USD Value</h3>
                    <div className="flex items-baseline relative z-10">
                        <span className="text-3xl font-bold font-display text-white">
                            {netWorth ? netWorth.total_usd.toLocaleString(undefined, { style: 'currency', currency: 'USD' }) : '...'}
                        </span>
                    </div>
                </div>

                <div className="glass-panel p-6 relative overflow-hidden">
                    <h3 className="text-slate-400 text-xs font-bold uppercase tracking-widest mb-1">USD/TWD Rate</h3>
                    <div className="text-2xl font-bold font-display text-nebula-300">
                        {netWorth ? netWorth.usd_rate.toFixed(2) : '...'}
                    </div>
                </div>

                <div className="glass-panel p-6 flex items-center justify-between relative overflow-hidden">
                    <div>
                        <h3 className="text-slate-400 text-xs font-bold uppercase tracking-widest mb-1">Current Leverage</h3>
                        <div className={`text-2xl font-bold font-display ${netWorth && netWorth.leverage_ratio > 1.2 ? 'text-neon-green' : 'text-white'}`}>
                            {netWorth && netWorth.leverage_ratio ? `${netWorth.leverage_ratio.toFixed(2)}x` : '1.00x'}
                        </div>
                    </div>
                    <button
                        onClick={fetchData}
                        className="p-3 rounded-xl bg-white/5 hover:bg-white/10 border border-white/5 transition-all active:scale-95 group"
                        title="Refresh Data"
                    >
                        <RefreshCw size={18} className={`text-nebula-400 group-hover:rotate-180 transition-transform duration-700 ${loading ? "animate-spin" : ""}`} />
                    </button>
                </div>
            </div>

            {/* Charts Section */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="glass-panel p-6 glass-panel-hover">
                    <div className="flex justify-between items-center mb-6">
                        <h3 className="text-lg font-bold font-display text-white">Asset Allocation</h3>
                        <div className="flex gap-3">
                            <div className="flex bg-slate-900/50 rounded-lg p-0.5 border border-white/10">
                                <button
                                    onClick={() => setGroupingMode('type')}
                                    className={`px-3 py-1.5 text-xs font-bold uppercase tracking-wider rounded-md transition-colors ${groupingMode === 'type' ? 'bg-slate-700 text-white' : 'text-slate-500 hover:text-slate-300'}`}
                                >
                                    Type
                                </button>
                                <button
                                    onClick={() => setGroupingMode('asset')}
                                    className={`px-3 py-1.5 text-xs font-bold uppercase tracking-wider rounded-md transition-colors ${groupingMode === 'asset' ? 'bg-slate-700 text-white' : 'text-slate-500 hover:text-slate-300'}`}
                                >
                                    Asset
                                </button>
                            </div>
                            <div className="flex bg-slate-900/50 rounded-lg p-0.5 border border-white/10">
                                <button
                                    onClick={() => setAllocationMode('weighted')}
                                    className={`px-3 py-1.5 text-xs font-bold uppercase tracking-wider rounded-md transition-colors ${allocationMode === 'weighted' ? 'bg-slate-700 text-white' : 'text-slate-500 hover:text-slate-300'}`}
                                >
                                    Weighted
                                </button>
                                <button
                                    onClick={() => setAllocationMode('unweighted')}
                                    className={`px-3 py-1.5 text-xs font-bold uppercase tracking-wider rounded-md transition-colors ${allocationMode === 'unweighted' ? 'bg-slate-700 text-white' : 'text-slate-500 hover:text-slate-300'}`}
                                >
                                    Capital
                                </button>
                            </div>
                        </div>
                    </div>
                    <div className="h-72">
                        {netWorth && <AssetAllocationChart
                            data={netWorth.details}
                            dataKey={allocationMode === 'weighted' ? 'notional_value' : 'equity'}
                            totalNetWorth={netWorth.total_twd}
                            groupingMode={groupingMode}
                        />}
                    </div>
                </div>
                <div className="glass-panel p-6 glass-panel-hover">
                    <div className="flex justify-between items-center mb-6">
                        <h3 className="text-lg font-bold font-display text-white">
                            {viewMode === 'pnl' ? 'Cumulative Realized P&L' : 'History'}
                        </h3>
                        <div className="flex gap-3">
                            <div className="flex bg-slate-900/50 rounded-lg p-0.5 border border-white/10">
                                <button
                                    onClick={() => setTimeRange('3M')}
                                    className={`px-3 py-1.5 text-xs font-bold uppercase tracking-wider rounded-md transition-colors ${timeRange === '3M' ? 'bg-slate-700 text-white' : 'text-slate-500 hover:text-slate-300'}`}
                                >
                                    3M
                                </button>
                                <button
                                    onClick={() => setTimeRange('1Y')}
                                    className={`px-3 py-1.5 text-xs font-bold uppercase tracking-wider rounded-md transition-colors ${timeRange === '1Y' ? 'bg-slate-700 text-white' : 'text-slate-500 hover:text-slate-300'}`}
                                >
                                    1Y
                                </button>
                                <button
                                    onClick={() => setTimeRange('ALL')}
                                    className={`px-3 py-1.5 text-xs font-bold uppercase tracking-wider rounded-md transition-colors ${timeRange === 'ALL' ? 'bg-slate-700 text-white' : 'text-slate-500 hover:text-slate-300'}`}
                                >
                                    ALL
                                </button>
                            </div>
                            {viewMode !== 'pnl' && (
                                <div className="flex bg-slate-900/50 rounded-lg p-0.5 border border-white/10">
                                    <button
                                        onClick={() => setHistoryViewMode('total')}
                                        className={`px-3 py-1.5 text-xs font-bold uppercase tracking-wider rounded-md transition-colors ${historyViewMode === 'total' ? 'bg-slate-700 text-white' : 'text-slate-500 hover:text-slate-300'}`}
                                    >
                                        Total
                                    </button>
                                    <button
                                        onClick={() => setHistoryViewMode('breakdown')}
                                        className={`px-3 py-1.5 text-xs font-bold uppercase tracking-wider rounded-md transition-colors ${historyViewMode === 'breakdown' ? 'bg-slate-700 text-white' : 'text-slate-500 hover:text-slate-300'}`}
                                    >
                                        Breakdown
                                    </button>
                                </div>
                            )}
                        </div>
                    </div>
                    <div className="h-72">
                        {viewMode === 'pnl' ? (
                            <NetWorthHistoryChart data={filteredCumulativePnl} dataKey="cumulative_pnl" color="#0aff68" />
                        ) : (
                            <NetWorthHistoryChart
                                data={filteredHistory}
                                dataKey="total_twd"
                                color="#6366f1"
                                viewMode={historyViewMode}
                            />
                        )}
                    </div>
                </div>
            </div>

            {/* Assets / P&L Table */}
            <div className="glass-panel p-6">
                <div className="flex justify-between items-center mb-6">
                    <h3 className="text-lg font-bold font-display text-white">
                        {viewMode === 'pnl' ? 'Realized P&L History' : 'Holdings'}
                    </h3>

                    <div className="flex gap-3">
                        {viewMode === 'assets' && (
                            <>
                                <button
                                    onClick={() => setIsImportModalOpen(true)}
                                    className="flex items-center gap-2 px-5 py-2.5 bg-white/5 border border-white/10 hover:bg-white/10 hover:border-nebula-500/50 rounded-xl font-medium text-sm text-slate-300 hover:text-white transition-all active:scale-95 group"
                                >
                                    <Upload size={18} className="text-nebula-400 group-hover:text-nebula-300" />
                                    Import CSV
                                </button>
                                <button
                                    onClick={() => setIsModalOpen(true)}
                                    className="flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-nebula-500 to-nebula-400 hover:from-nebula-400 hover:to-nebula-300 rounded-xl font-medium text-sm text-white shadow-lg shadow-nebula-500/25 transition-all hover:scale-105 active:scale-95"
                                >
                                    <Plus size={18} /> New Position
                                </button>
                            </>
                        )}
                    </div>
                </div>

                {viewMode === 'pnl' ? (
                    <RealizedPnLTable data={pnlHistory} />
                ) : (
                    <AssetTable
                        assets={netWorth ? netWorth.details : assets}
                        onDelete={fetchData}
                        onUpdate={fetchData}
                        usdRate={netWorth ? netWorth.usd_rate : 32.0}
                        totalNetWorth={netWorth ? netWorth.total_twd : 0}
                    />
                )}
            </div>

            {isModalOpen && (
                <AddAssetModal
                    isOpen={isModalOpen}
                    onClose={() => setIsModalOpen(false)}
                    onSuccess={() => {
                        setIsModalOpen(false);
                        fetchData();
                    }}
                />
            )}

            {isImportModalOpen && (
                <ImportHistoryModal
                    isOpen={isImportModalOpen}
                    onClose={() => setIsImportModalOpen(false)}
                    onSuccess={() => {
                        setIsImportModalOpen(false);
                        fetchData();
                    }}
                />
            )}
        </div>
    );
};

export default Dashboard;
