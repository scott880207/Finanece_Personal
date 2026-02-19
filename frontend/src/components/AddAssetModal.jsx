import React, { useState, useEffect } from 'react';
import api from '../api';
import { X } from 'lucide-react';

const AddAssetModal = ({ isOpen, onClose, onSuccess }) => {
    const [formData, setFormData] = useState({
        type: 'TW_STOCK',
        symbol: '',
        quantity: '',
        cost: '',
        currency: 'TWD',
        // Future specific
        date: new Date().toISOString().split('T')[0],
        contract_month: '',
        action: 'OPEN_LONG', // OPEN_LONG, OPEN_SHORT, CLOSE_LONG, CLOSE_SHORT
        multiplier: 1,
        assigned_margin: 0,
        fee: 0,
        tax: 0
    });

    useEffect(() => {
        if (formData.type === 'TW_FUTURE') {
            // Auto-fill multiplier logic
            if (formData.symbol === 'QSF' || formData.symbol === 'Small Phison') {
                setFormData(prev => ({ ...prev, multiplier: 100 }));
            } else if (formData.symbol === 'Phison' || formData.symbol === '8299') { // Assuming 8299 is Phison stock code, but futures might use different code. User said "QSF (or 8299)"
                setFormData(prev => ({ ...prev, multiplier: 2000 }));
            } else if (formData.symbol === 'TX' || formData.symbol === 'Big Tai') {
                setFormData(prev => ({ ...prev, multiplier: 200 }));
            } else if (formData.symbol === 'MTX' || formData.symbol === 'Small Tai') {
                setFormData(prev => ({ ...prev, multiplier: 50 }));
            }
        }
    }, [formData.symbol, formData.type]);

    // Simple Fee & Tax calc (Placeholder logic based on user description)
    useEffect(() => {
        if (formData.type === 'TW_FUTURE' && formData.cost && formData.multiplier) {
            const price = parseFloat(formData.cost);
            const mult = parseFloat(formData.multiplier);
            const qty = parseFloat(formData.quantity) || 1;

            // Tax: 100,000th of 2 (0.00002)
            const tax = Math.round(price * mult * qty * 0.00002);
            // Fee: Fixed rate, let's assume 50 for now or leave 0
            const fee = 50 * qty;

            setFormData(prev => ({ ...prev, tax, fee }));
        }
    }, [formData.cost, formData.multiplier, formData.quantity, formData.type]);


    if (!isOpen) return null;

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            if (formData.type === 'TW_FUTURE') {
                await api.post('/transactions/future', {
                    date: formData.date,
                    asset_type: formData.type,
                    symbol: formData.symbol,
                    action: formData.action,
                    price: parseFloat(formData.cost),
                    quantity: parseFloat(formData.quantity),
                    contract_month: formData.contract_month,
                    multiplier: parseFloat(formData.multiplier),
                    fee: parseFloat(formData.fee),
                    tax: parseFloat(formData.tax),
                    assigned_margin: parseFloat(formData.assigned_margin)
                });
            } else {
                await api.post('/assets/', {
                    type: formData.type,
                    symbol: formData.symbol,
                    quantity: parseFloat(formData.quantity),
                    cost: parseFloat(formData.cost),
                    currency: formData.currency
                });
            }
            onSuccess();
            onClose();
        } catch (error) {
            console.error("Error adding asset", error);
            alert("Failed to add asset");
        }
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
            <div className="bg-slate-800 border border-slate-700 rounded-xl w-full max-w-md p-6 shadow-2xl overflow-y-auto max-h-[90vh]">
                <div className="flex justify-between items-center mb-6">
                    <h3 className="text-xl font-bold text-white">Add New Asset</h3>
                    <button onClick={onClose} className="text-slate-400 hover:text-white">
                        <X size={24} />
                    </button>
                </div>

                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-slate-400 mb-1">Type</label>
                        <select
                            value={formData.type}
                            onChange={(e) => setFormData({ ...formData, type: e.target.value, currency: (e.target.value === 'US_STOCK' || e.target.value === 'USD') ? 'USD' : 'TWD' })}
                            className="w-full bg-slate-900 border border-slate-700 rounded-lg p-3 text-white focus:ring-2 focus:ring-blue-500 outline-none"
                        >
                            <option value="TWD">TWD Cash</option>
                            <option value="USD">USD Cash</option>
                            <option value="TW_STOCK">Taiwan Stock</option>
                            <option value="US_STOCK">US Stock</option>
                            <option value="TW_FUTURE">Taiwan Future</option>
                        </select>
                    </div>

                    {formData.type === 'TW_FUTURE' && (
                        <>
                            <div>
                                <label className="block text-sm font-medium text-slate-400 mb-1">Date</label>
                                <input
                                    type="date"
                                    value={formData.date}
                                    onChange={(e) => setFormData({ ...formData, date: e.target.value })}
                                    className="w-full bg-slate-900 border border-slate-700 rounded-lg p-3 text-white focus:ring-2 focus:ring-blue-500 outline-none"
                                    required
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-slate-400 mb-1">Action</label>
                                <select
                                    value={formData.action}
                                    onChange={(e) => setFormData({ ...formData, action: e.target.value })}
                                    className="w-full bg-slate-900 border border-slate-700 rounded-lg p-3 text-white focus:ring-2 focus:ring-blue-500 outline-none"
                                >
                                    <option value="OPEN_LONG">New - Buy (Open Long)</option>
                                    <option value="OPEN_SHORT">New - Sell (Open Short)</option>
                                    <option value="CLOSE_LONG">Close - Sell (Close Long)</option>
                                    <option value="CLOSE_SHORT">Close - Buy (Close Short)</option>
                                </select>
                            </div>
                        </>
                    )}

                    {(formData.type === 'TW_STOCK' || formData.type === 'US_STOCK' || formData.type === 'TW_FUTURE') && (
                        <div>
                            <label className="block text-sm font-medium text-slate-400 mb-1">Symbol</label>
                            <input
                                type="text"
                                value={formData.symbol}
                                onChange={(e) => setFormData({ ...formData, symbol: e.target.value.toUpperCase() })}
                                placeholder={formData.type === 'TW_STOCK' ? 'e.g. 2330' : (formData.type === 'TW_FUTURE' ? 'e.g. QSF' : 'e.g. AAPL')}
                                className="w-full bg-slate-900 border border-slate-700 rounded-lg p-3 text-white focus:ring-2 focus:ring-blue-500 outline-none"
                                required
                            />
                        </div>
                    )}

                    {formData.type === 'TW_FUTURE' && (
                        <div>
                            <label className="block text-sm font-medium text-slate-400 mb-1">Contract Month (YYYYMM)</label>
                            <input
                                type="text"
                                value={formData.contract_month}
                                onChange={(e) => setFormData({ ...formData, contract_month: e.target.value })}
                                placeholder="e.g. 202512"
                                className="w-full bg-slate-900 border border-slate-700 rounded-lg p-3 text-white focus:ring-2 focus:ring-blue-500 outline-none"
                                required
                            />
                        </div>
                    )}

                    <div>
                        <label className="block text-sm font-medium text-slate-400 mb-1">Quantity</label>
                        <input
                            type="number"
                            step="any"
                            value={formData.quantity}
                            onChange={(e) => setFormData({ ...formData, quantity: e.target.value })}
                            className="w-full bg-slate-900 border border-slate-700 rounded-lg p-3 text-white focus:ring-2 focus:ring-blue-500 outline-none"
                            required
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-slate-400 mb-1">{formData.type === 'TW_FUTURE' ? 'Price' : 'Cost per Unit'}</label>
                        <input
                            type="number"
                            step="any"
                            value={formData.cost}
                            onChange={(e) => setFormData({ ...formData, cost: e.target.value })}
                            className="w-full bg-slate-900 border border-slate-700 rounded-lg p-3 text-white focus:ring-2 focus:ring-blue-500 outline-none"
                            required
                        />
                    </div>

                    {formData.type === 'TW_FUTURE' && (
                        <>
                            <div>
                                <label className="block text-sm font-medium text-slate-400 mb-1">Multiplier</label>
                                <input
                                    type="number"
                                    value={formData.multiplier}
                                    onChange={(e) => setFormData({ ...formData, multiplier: e.target.value })}
                                    className="w-full bg-slate-900 border border-slate-700 rounded-lg p-3 text-white focus:ring-2 focus:ring-blue-500 outline-none"
                                />
                            </div>
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium text-slate-400 mb-1">Fee (Est.)</label>
                                    <input
                                        type="number"
                                        value={formData.fee}
                                        readOnly
                                        className="w-full bg-slate-800 border border-slate-700 rounded-lg p-3 text-slate-400 outline-none"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-slate-400 mb-1">Tax (Est.)</label>
                                    <input
                                        type="number"
                                        value={formData.tax}
                                        readOnly
                                        className="w-full bg-slate-800 border border-slate-700 rounded-lg p-3 text-slate-400 outline-none"
                                    />
                                </div>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-slate-400 mb-1">Assigned Margin (Optional)</label>
                                <input
                                    type="number"
                                    value={formData.assigned_margin}
                                    onChange={(e) => setFormData({ ...formData, assigned_margin: e.target.value })}
                                    placeholder="0 if using remaining margin"
                                    className="w-full bg-slate-900 border border-slate-700 rounded-lg p-3 text-white focus:ring-2 focus:ring-blue-500 outline-none"
                                />
                            </div>
                        </>
                    )}

                    <button
                        type="submit"
                        className="w-full bg-blue-600 hover:bg-blue-500 text-white font-bold py-3 rounded-lg transition-colors mt-4"
                    >
                        Add Asset
                    </button>
                </form>
            </div>
        </div>
    );
};

export default AddAssetModal;
