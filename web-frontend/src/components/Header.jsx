import React, { useState } from 'react';
import { useSearch } from '../context/SearchContext';
import { queryAI } from '../services/aiService';
import AIResultModal from './AIResultModal';
import { useNavigate } from 'react-router-dom';

const Header = ({ user, onLogout, toggleTheme, theme, onOpenHelp, data }) => {
    const { searchQuery, setSearchQuery } = useSearch();
    const navigate = useNavigate();
    const [aiResponse, setAiResponse] = useState('');
    const [isAiLoading, setIsAiLoading] = useState(false);
    const [showAiModal, setShowAiModal] = useState(false);

    const handleKeyDown = async (e) => {
        if (e.key === 'Enter' && searchQuery.trim()) {
            if (!data) {
                alert("Please upload log data first to use AI search.");
                return;
            }
            setShowAiModal(true);
            setIsAiLoading(true);

            // Prepare context (summary + first 50 rows of data for better context)
            const context = {
                summary: data.summary,
                sample_data: data.processed_data ? data.processed_data.slice(0, 50) : []
            };

            const response = await queryAI(context, searchQuery);

            // Parse for Actions
            let cleanResponse = response;
            // Radius of action tag detection: Look for tag at start or end
            const actionRegex = /\|ACTION:([A-Z]+):(.+)\|/;
            const match = response.match(actionRegex);

            if (match) {
                const actionType = match[1];
                const actionValue = match[2];

                console.log(`AI Action Triggered: ${actionType} -> ${actionValue}`);

                // Remove tag from display
                cleanResponse = response.replace(match[0], '').trim();

                if (actionType === 'NAVIGATE') {
                    navigate(actionValue);
                    setShowAiModal(false); // Close modal immediately
                    setIsAiLoading(false);
                    return;
                } else if (actionType === 'SEARCH') {
                    setSearchQuery(actionValue);
                    // Only close if the response is empty (pure action)
                    // If AI generated a table/text (cleanResponse has length), keep it open
                    if (cleanResponse.length < 5) {
                        setShowAiModal(false);
                    }
                }
            }

            setAiResponse(cleanResponse);
            setIsAiLoading(false);
        }
    };

    return (
        <>
            <header className="h-16 bg-white dark:bg-slate-850 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between px-6 flex-shrink-0 z-10 transition-colors">
                <div className="flex items-center gap-4">
                    <button className="lg:hidden p-2 text-slate-500 hover:bg-slate-100 rounded-lg">
                        <span className="material-symbols-outlined">menu</span>
                    </button>

                    {/* Search */}
                    <div className="relative hidden md:block w-96">
                        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                            <span className="material-symbols-outlined text-slate-400 text-[20px]">search</span>
                        </div>
                        <input
                            className="block w-full pl-10 pr-3 py-2 border-none ring-1 ring-slate-200 dark:ring-slate-700 rounded-lg bg-slate-50 dark:bg-slate-800 text-sm placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-primary dark:text-white transition-all"
                            placeholder="Type & Press Enter for AI Analysis..."
                            type="text"
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            onKeyDown={handleKeyDown}
                        />
                    </div>
                </div>

                <div className="flex items-center gap-3">
                    {/* Theme Toggle */}
                    <button
                        onClick={toggleTheme}
                        className="p-2 text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-full transition-colors"
                    >
                        {theme === 'dark' ? <span className="material-symbols-outlined text-[24px]">light_mode</span> : <span className="material-symbols-outlined text-[24px]">dark_mode</span>}
                    </button>

                    <button
                        onClick={onOpenHelp}
                        className="p-2 text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-full transition-colors"
                    >
                        <span className="material-symbols-outlined text-[24px]">help</span>
                    </button>

                    <div className="h-8 w-px bg-slate-200 dark:bg-slate-700 mx-2"></div>

                    <div className="flex items-center gap-3 cursor-pointer group relative">
                        <div className="text-right hidden md:block">
                            <p className="text-sm font-semibold text-slate-900 dark:text-white">{user || 'Guest User'}</p>
                            <p className="text-xs text-slate-500 dark:text-slate-400">Normal User</p>
                        </div>
                        {/* Placeholder Avatar */}
                        <div className="h-10 w-10 rounded-full bg-primary/20 flex items-center justify-center text-primary font-bold border-2 border-white shadow-sm dark:border-slate-700">
                            {user ? user[0].toUpperCase() : 'G'}
                        </div>

                        {/* Simple Dropdown for Logout */}
                        {/* Adjusted top position to top-10 to connect with the trigger area and prevent menu from disappearing on hover */}
                        <div className="absolute top-10 right-0 w-48 bg-white dark:bg-slate-800 rounded-lg shadow-lg border border-slate-200 dark:border-slate-700 py-1 hidden group-hover:block transition-all z-50">
                            <button
                                onClick={onLogout}
                                className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 flex items-center gap-2"
                            >
                                <span className="material-symbols-outlined text-[18px]">logout</span>
                                Logout
                            </button>
                        </div>
                    </div>
                </div>
            </header>
            <AIResultModal
                isOpen={showAiModal}
                onClose={() => setShowAiModal(false)}
                query={searchQuery}
                response={aiResponse}
                isLoading={isAiLoading}
            />
        </>
    );
};

export default Header;
