import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

const AIResultModal = ({ isOpen, onClose, query, response, isLoading }) => {
    if (!isOpen) return null;

    const handleBackdropClick = (e) => {
        if (e.target === e.currentTarget) {
            onClose();
        }
    };

    return (
        <div
            onClick={handleBackdropClick}
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 animate-in fade-in duration-200 cursor-pointer"
        >
            <div className="bg-white dark:bg-slate-900 rounded-xl shadow-2xl w-full max-w-2xl border border-slate-200 dark:border-slate-700 relative overflow-hidden flex flex-col max-h-[85vh] cursor-default">

                {/* Header */}
                <div className="flex items-center justify-between p-5 border-b border-slate-100 dark:border-slate-800 bg-gradient-to-r from-indigo-50 to-purple-50 dark:from-indigo-900/20 dark:to-purple-900/20">
                    <div className="flex items-center gap-3">
                        <div className="p-2 bg-indigo-500 rounded-lg text-white shadow-sm">
                            <span className="material-symbols-outlined text-[20px]">temp_preferences_custom</span>
                        </div>
                        <div>
                            <h3 className="text-lg font-bold text-slate-900 dark:text-white">AI Insights</h3>
                            <p className="text-xs text-slate-500 dark:text-slate-400">Analysis powered by OpenRouter</p>
                        </div>
                    </div>
                    <button onClick={onClose} className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition-colors">
                        <span className="material-symbols-outlined">close</span>
                    </button>
                </div>

                {/* Content */}
                <div className="p-6 overflow-y-auto custom-scrollbar">
                    {/* User Query */}
                    <div className="mb-6">
                        <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">Your Question</p>
                        <p className="text-slate-900 dark:text-white font-medium text-lg">"{query}"</p>
                    </div>

                    {/* AI Response */}
                    {isLoading ? (
                        <div className="flex flex-col items-center justify-center py-10 gap-4">
                            <div className="w-8 h-8 border-4 border-indigo-500/30 border-t-indigo-500 rounded-full animate-spin"></div>
                            <p className="text-slate-500 animate-pulse">Analyzing system data...</p>
                        </div>
                    ) : (
                        <div className="prose prose-sm dark:prose-invert max-w-none 
                            prose-p:text-slate-600 dark:prose-p:text-slate-300 
                            prose-headings:text-slate-900 dark:prose-headings:text-white 
                            prose-indigo 
                            
                            /* Table Styling */
                            [&_table]:w-full [&_table]:border-collapse [&_table]:border [&_table]:border-slate-300 [&_table]:dark:border-slate-600 [&_table]:mb-4
                            
                            /* Header Styling */
                            [&_th]:bg-slate-100 [&_th]:dark:bg-slate-800 [&_th]:text-slate-900 [&_th]:dark:text-white [&_th]:font-semibold [&_th]:p-3 [&_th]:border [&_th]:border-slate-300 [&_th]:dark:border-slate-600 [&_th]:text-left
                            
                            /* Cell Styling */
                            [&_td]:p-3 [&_td]:border [&_td]:border-slate-300 [&_td]:dark:border-slate-600 [&_td]:text-slate-700 [&_td]:dark:text-slate-300">
                            <ReactMarkdown remarkPlugins={[remarkGfm]}>{response}</ReactMarkdown>
                        </div>
                    )}
                </div>

                {/* Footer */}
                <div className="p-4 border-t border-slate-100 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/50 flex justify-end">
                    <button
                        onClick={onClose}
                        className="px-5 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-sm font-semibold transition-colors shadow-lg shadow-indigo-500/30"
                    >
                        Close
                    </button>
                </div>
            </div>
        </div>
    );
};

export default AIResultModal;
