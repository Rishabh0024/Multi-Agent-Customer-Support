import React from 'react';
import { NavLink } from 'react-router-dom';
import { MessageSquare, LifeBuoy, BookOpen, Activity, ShieldCheck } from 'lucide-react';
import { useSystemHealth } from '../services/api';

export const Navbar: React.FC = () => {
  const { data: health } = useSystemHealth();

  return (
    <header className="sticky top-0 z-40 border-b border-slate-200 bg-white/90 backdrop-blur-md">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 sm:px-6">
        {/* Brand */}
        <div className="flex items-center space-x-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-tr from-sky-600 to-indigo-600 text-white shadow-md shadow-sky-500/20">
            <ShieldCheck className="h-6 w-6" />
          </div>
          <div>
            <span className="text-lg font-bold tracking-tight text-slate-900">
              Agentic Support
            </span>
            <span className="ml-2 inline-flex items-center rounded-md bg-sky-50 px-2 py-0.5 text-xs font-semibold text-sky-700">
              LangGraph Multi-Agent
            </span>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="flex items-center space-x-1 sm:space-x-2">
          <NavLink
            to="/"
            className={({ isActive }) =>
              `flex items-center space-x-2 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-sky-50 text-sky-700 font-semibold'
                  : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
              }`
            }
          >
            <MessageSquare className="h-4 w-4" />
            <span>Customer Chat</span>
          </NavLink>

          <NavLink
            to="/tickets"
            className={({ isActive }) =>
              `flex items-center space-x-2 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-sky-50 text-sky-700 font-semibold'
                  : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
              }`
            }
          >
            <LifeBuoy className="h-4 w-4" />
            <span>Support Desk</span>
          </NavLink>

          <NavLink
            to="/knowledge"
            className={({ isActive }) =>
              `flex items-center space-x-2 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-sky-50 text-sky-700 font-semibold'
                  : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
              }`
            }
          >
            <BookOpen className="h-4 w-4" />
            <span>Knowledge Base</span>
          </NavLink>
        </nav>

        {/* System Status Pill */}
        <div className="hidden items-center space-x-2 sm:flex">
          <span className="flex h-2 w-2 relative">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
          </span>
          <span className="text-xs font-medium text-slate-500 flex items-center gap-1">
            <Activity className="h-3 w-3 text-emerald-600" />
            {health?.components?.qdrant_vector_store === 'operational' ? 'Qdrant & Postgres Active' : 'Online'}
          </span>
        </div>
      </div>
    </header>
  );
};
