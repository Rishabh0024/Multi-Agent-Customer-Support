import React from 'react';
import { NavLink } from 'react-router-dom';
import { MessageSquare, LifeBuoy, BookOpen, Activity, ShieldCheck } from 'lucide-react';

export const Navbar: React.FC = () => {
  return (
    <>
      {/* Top Navbar Header */}
      <header className="sticky top-0 z-40 border-b border-slate-200 bg-white/95 backdrop-blur-md">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-3 py-2.5 sm:px-6 sm:py-3">
          {/* Brand */}
          <NavLink to="/" className="flex items-center space-x-2.5">
            <div className="flex h-9 w-9 sm:h-10 sm:w-10 items-center justify-center rounded-xl bg-gradient-to-tr from-sky-600 to-indigo-600 text-white shadow-md shadow-sky-500/20">
              <ShieldCheck className="h-5 w-5 sm:h-6 sm:w-6" />
            </div>
            <div>
              <span className="text-base sm:text-lg font-bold tracking-tight text-slate-900 block leading-tight">
                Agentic Support
              </span>
              <span className="text-[10px] sm:text-xs font-medium text-sky-600">
                LangGraph Multi-Agent
              </span>
            </div>
          </NavLink>

          {/* Desktop Navigation Tabs (Hidden on mobile) */}
          <nav className="hidden md:flex items-center space-x-1 lg:space-x-2">
            <NavLink
              to="/"
              className={({ isActive }) =>
                `flex items-center space-x-2 rounded-xl px-3.5 py-2 text-sm font-medium transition-all ${
                  isActive
                    ? 'bg-sky-50 text-sky-700 font-semibold shadow-xs'
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
                `flex items-center space-x-2 rounded-xl px-3.5 py-2 text-sm font-medium transition-all ${
                  isActive
                    ? 'bg-sky-50 text-sky-700 font-semibold shadow-xs'
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
                `flex items-center space-x-2 rounded-xl px-3.5 py-2 text-sm font-medium transition-all ${
                  isActive
                    ? 'bg-sky-50 text-sky-700 font-semibold shadow-xs'
                    : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
                }`
              }
            >
              <BookOpen className="h-4 w-4" />
              <span>Knowledge Base</span>
            </NavLink>
          </nav>

          {/* System Status Pill */}
          <div className="flex items-center space-x-2 bg-slate-50 px-2.5 py-1 sm:px-3 sm:py-1.5 rounded-full border border-slate-200">
            <span className="flex h-2 w-2 relative">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
            <span className="text-[11px] sm:text-xs font-medium text-slate-600 flex items-center gap-1">
              <Activity className="h-3 w-3 text-emerald-600" />
              <span className="hidden sm:inline">System Active</span>
              <span className="sm:hidden font-semibold text-emerald-700">Live</span>
            </span>
          </div>
        </div>
      </header>

      {/* Mobile Bottom Navigation Bar (App-like feel, strictly mobile) */}
      <nav className="md:hidden fixed bottom-0 left-0 right-0 z-50 bg-white/95 backdrop-blur-md border-t border-slate-200 px-3 py-1 shadow-lg flex justify-around items-center">
        <NavLink
          to="/"
          className={({ isActive }) =>
            `flex flex-col items-center justify-center py-1.5 px-3 rounded-xl transition-all ${
              isActive
                ? 'text-sky-600 font-bold'
                : 'text-slate-400 hover:text-slate-600 font-medium'
            }`
          }
        >
          <MessageSquare className="h-5 w-5 mb-0.5" />
          <span className="text-[10px] tracking-tight">Chat</span>
        </NavLink>

        <NavLink
          to="/tickets"
          className={({ isActive }) =>
            `flex flex-col items-center justify-center py-1.5 px-3 rounded-xl transition-all ${
              isActive
                ? 'text-sky-600 font-bold'
                : 'text-slate-400 hover:text-slate-600 font-medium'
            }`
          }
        >
          <LifeBuoy className="h-5 w-5 mb-0.5" />
          <span className="text-[10px] tracking-tight">Support Desk</span>
        </NavLink>

        <NavLink
          to="/knowledge"
          className={({ isActive }) =>
            `flex flex-col items-center justify-center py-1.5 px-3 rounded-xl transition-all ${
              isActive
                ? 'text-sky-600 font-bold'
                : 'text-slate-400 hover:text-slate-600 font-medium'
            }`
          }
        >
          <BookOpen className="h-5 w-5 mb-0.5" />
          <span className="text-[10px] tracking-tight">Knowledge</span>
        </NavLink>
      </nav>
    </>
  );
};
