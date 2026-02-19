import React, { useState } from 'react';
import { Upload, X, FileText, CheckCircle, AlertCircle } from 'lucide-react';
import api from '../api';

const ImportHistoryModal = ({ isOpen, onClose, onSuccess }) => {
    const [file, setFile] = useState(null);
    const [strategy, setStrategy] = useState('cathay');
    const [uploading, setUploading] = useState(false);
    const [message, setMessage] = useState(null);
    const [status, setStatus] = useState(null); // 'success', 'error'

    if (!isOpen) return null;

    const handleFileChange = (e) => {
        if (e.target.files[0]) {
            setFile(e.target.files[0]);
            setMessage(null);
            setStatus(null);
        }
    };

    const handleUpload = async () => {
        if (!file) return;

        setUploading(true);
        setMessage(null);
        setStatus(null);

        const formData = new FormData();
        formData.append('file', file);
        formData.append('strategy', strategy);

        try {
            const response = await api.post('/upload/history', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });

            setStatus('success');
            setMessage(`Successfully imported ${response.data.imported_count} transactions.`);

            // Close after a short delay
            setTimeout(() => {
                onSuccess();
            }, 2000);

        } catch (error) {
            console.error("Upload failed", error);
            setStatus('error');
            setMessage(error.response?.data?.detail || "Import failed. Please checks the file format.");
        } finally {
            setUploading(false);
        }
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
            <div className="bg-slate-900 border border-white/10 rounded-2xl w-full max-w-md overflow-hidden shadow-2xl shadow-black/50">
                <div className="flex justify-between items-center p-6 border-b border-white/5 bg-white/5">
                    <h3 className="text-xl font-bold font-display text-white">Import History</h3>
                    <button onClick={onClose} className="text-slate-400 hover:text-white transition-colors">
                        <X size={24} />
                    </button>
                </div>

                <div className="p-6 space-y-6">
                    {/* Strategy Selection */}
                    <div className="space-y-2">
                        <label className="text-sm font-medium text-slate-400">Broker / Format</label>
                        <select
                            value={strategy}
                            onChange={(e) => setStrategy(e.target.value)}
                            className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-nebula-500 focus:ring-1 focus:ring-nebula-500 transition-all font-sans"
                        >
                            <option value="cathay">Cathay Securities (國泰證券)</option>
                            <option value="yuanta" disabled>Yuanta Securities (元大證券 - Coming Soon)</option>
                        </select>
                    </div>

                    {/* File Upload Area */}
                    <div className="border-2 border-dashed border-white/10 rounded-xl p-8 text-center bg-white/5 hover:bg-white/10 hover:border-nebula-500/50 transition-all group">
                        <input
                            type="file"
                            accept=".csv"
                            onChange={handleFileChange}
                            className="hidden"
                            id="file-upload"
                        />
                        <label htmlFor="file-upload" className="cursor-pointer block">
                            {file ? (
                                <div className="flex flex-col items-center gap-3">
                                    <div className="p-3 bg-nebula-500/20 rounded-full text-nebula-400">
                                        <FileText size={32} />
                                    </div>
                                    <span className="text-white font-medium">{file.name}</span>
                                    <span className="text-xs text-slate-500">Click to change</span>
                                </div>
                            ) : (
                                <div className="flex flex-col items-center gap-3">
                                    <div className="p-3 bg-white/5 rounded-full text-slate-400 group-hover:text-white transition-colors">
                                        <Upload size={32} />
                                    </div>
                                    <span className="text-slate-300 font-medium group-hover:text-white transition-colors">Click to upload CSV</span>
                                    <span className="text-xs text-slate-500">Supports Cathay format</span>
                                </div>
                            )}
                        </label>
                    </div>

                    {/* Status Message */}
                    {message && (
                        <div className={`p-4 rounded-xl flex items-center gap-3 ${status === 'success' ? 'bg-green-500/10 text-green-400 border border-green-500/20' : 'bg-red-500/10 text-red-400 border border-red-500/20'}`}>
                            {status === 'success' ? <CheckCircle size={20} /> : <AlertCircle size={20} />}
                            <span className="text-sm font-medium">{message}</span>
                        </div>
                    )}

                    {/* Actions */}
                    <div className="flex gap-3 pt-2">
                        <button
                            onClick={onClose}
                            className="flex-1 px-4 py-3 bg-white/5 hover:bg-white/10 text-slate-300 font-bold rounded-xl transition-all"
                        >
                            Cancel
                        </button>
                        <button
                            onClick={handleUpload}
                            disabled={!file || uploading}
                            className="flex-1 px-4 py-3 bg-gradient-to-r from-nebula-500 to-nebula-400 hover:from-nebula-400 hover:to-nebula-300 text-white font-bold rounded-xl shadow-lg shadow-nebula-500/25 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                        >
                            {uploading ? (
                                <>
                                    <div className="animate-spin rounded-full h-4 w-4 border-2 border-white/30 border-t-white"></div>
                                    Processing...
                                </>
                            ) : (
                                'Import'
                            )}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ImportHistoryModal;
