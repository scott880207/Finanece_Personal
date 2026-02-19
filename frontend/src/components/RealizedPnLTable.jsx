import React from 'react';

const RealizedPnLTable = ({ data }) => {
    return (
        <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
                <thead>
                    <tr className="text-slate-400 border-b border-slate-700">
                        <th className="p-4 font-medium">Date</th>
                        <th className="p-4 font-medium">Symbol</th>
                        <th className="p-4 font-medium text-right">Quantity</th>
                        <th className="p-4 font-medium text-right">Realized P&L</th>
                        <th className="p-4 font-medium">Notes</th>
                    </tr>
                </thead>
                <tbody>
                    {data.map((item) => (
                        <tr key={item.id} className="border-b border-slate-800 hover:bg-slate-800/30 transition-colors">
                            <td className="p-4 text-slate-300">{item.date}</td>
                            <td className="p-4 font-medium text-slate-200">{item.symbol}</td>
                            <td className="p-4 text-right text-slate-300">{item.quantity.toLocaleString()}</td>
                            <td className={`p-4 text-right font-bold ${item.pnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                                {item.pnl > 0 ? '+' : ''}{item.pnl.toLocaleString()} TWD
                            </td>
                            <td className="p-4 text-slate-400 text-sm">{item.notes}</td>
                        </tr>
                    ))}
                    {data.length === 0 && (
                        <tr>
                            <td colSpan="5" className="p-8 text-center text-slate-500">
                                No realized P&L history found.
                            </td>
                        </tr>
                    )}
                </tbody>
            </table>
        </div>
    );
};

export default RealizedPnLTable;
