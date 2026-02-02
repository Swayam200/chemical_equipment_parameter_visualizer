import React, { useState } from 'react';
import Sidebar from './Sidebar';
import Header from './Header';
import ThresholdModal from './ThresholdModal';
import HelpModal from './HelpModal';
import { SearchProvider } from '../context/SearchContext';

const Layout = ({ children, user, onLogout, toggleTheme, theme, data }) => {
    const [showSettings, setShowSettings] = useState(false);
    const [showHelp, setShowHelp] = useState(false);

    return (
        <SearchProvider>
            <div className="flex h-screen w-full bg-background-light dark:bg-background-dark text-slate-900 dark:text-slate-50 overflow-hidden font-display">
                <Sidebar onOpenSettings={() => setShowSettings(true)} />
                <div className="flex-1 flex flex-col h-full overflow-hidden relative">
                    <Header
                        user={user}
                        onLogout={onLogout}
                        toggleTheme={toggleTheme}
                        theme={theme}
                        onOpenHelp={() => setShowHelp(true)}
                        data={data}
                    />
                    <main className="flex-1 overflow-y-auto p-6 lg:p-10 scroll-smooth">
                        <div className="max-w-7xl mx-auto flex flex-col gap-6">
                            {children}
                        </div>
                    </main>
                    {showSettings && <ThresholdModal onClose={() => setShowSettings(false)} />}
                    {showHelp && <HelpModal onClose={() => setShowHelp(false)} />}
                </div>
            </div>
        </SearchProvider>
    );
};

export default Layout;
