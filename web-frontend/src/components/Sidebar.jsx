import React from 'react';
import { NavLink } from 'react-router-dom';

const Sidebar = ({ onOpenSettings }) => {
    return (
        <aside className="w-64 bg-white dark:bg-slate-850 border-r border-slate-200 dark:border-slate-800 flex flex-col h-full flex-shrink-0 transition-colors">
            <div className="p-6 flex items-center gap-3">
                <img src="/logo.png" alt="Carbon Sleuth Logo" className="w-16 h-16 rounded-full object-cover bg-white shadow-sm" />
                <div className="flex flex-col">
                    <h1 className="text-slate-900 dark:text-white text-lg font-bold leading-tight tracking-tight">Carbon Sleuth</h1>
                    <p className="text-slate-500 dark:text-slate-400 text-xs font-medium">Emission Visualizer</p>
                </div>
            </div>

            <nav className="flex-1 px-4 flex flex-col gap-2 overflow-y-auto">
                <p className="px-2 text-xs font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider mt-4 mb-2">Main Menu</p>

                <NavLink
                    to="/"
                    className={({ isActive }) =>
                        `flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors group ${isActive
                            ? 'bg-primary/10 text-primary font-medium'
                            : 'hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-600 dark:text-slate-300'
                        }`
                    }
                >
                    <span className="material-symbols-outlined text-[24px]">dashboard</span>
                    <span className="text-sm">Dashboard</span>
                </NavLink>



                <NavLink
                    to="/analytics"
                    className={({ isActive }) =>
                        `flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors group ${isActive
                            ? 'bg-primary/10 text-primary font-medium'
                            : 'hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-600 dark:text-slate-300'
                        }`
                    }
                >
                    <span className="material-symbols-outlined text-[24px]">analytics</span>
                    <span className="text-sm font-medium">Reports & Analytics</span>
                </NavLink>

                <NavLink
                    to="/history"
                    className={({ isActive }) =>
                        `flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors group ${isActive
                            ? 'bg-primary/10 text-primary font-medium'
                            : 'hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-600 dark:text-slate-300'
                        }`
                    }
                >
                    <span className="material-symbols-outlined text-[24px]">database</span>
                    <span className="text-sm font-medium">Inventory Logs</span>
                </NavLink>

                <p className="px-2 text-xs font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider mt-6 mb-2">System</p>

                <button onClick={onOpenSettings} className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-600 dark:text-slate-300 transition-colors group text-left">
                    <span className="material-symbols-outlined text-[24px] text-slate-400 group-hover:text-primary transition-colors">settings</span>
                    <span className="text-sm font-medium">Configuration</span>
                </button>


            </nav>


        </aside>
    );
};

export default Sidebar;
