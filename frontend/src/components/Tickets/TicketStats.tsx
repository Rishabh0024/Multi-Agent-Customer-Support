import React from 'react';
import { LifeBuoy, CheckCircle2, Flame, Layers } from 'lucide-react';
import { useTicketStats } from '../../services/api';

export const TicketStats: React.FC = () => {
  const { data: stats, isLoading } = useTicketStats();

  const cards = [
    {
      title: 'Total Tickets',
      value: stats?.total_tickets ?? 0,
      icon: <Layers className="h-4 w-4 sm:h-5 sm:w-5 text-indigo-600" />,
      bg: 'bg-indigo-50/80 border-indigo-100',
    },
    {
      title: 'AI Escalated',
      value: stats?.escalated_tickets ?? 0,
      icon: <LifeBuoy className="h-4 w-4 sm:h-5 sm:w-5 text-amber-600" />,
      bg: 'bg-amber-50/80 border-amber-100',
    },
    {
      title: 'High / Urgent',
      value: stats?.high_priority_tickets ?? 0,
      icon: <Flame className="h-4 w-4 sm:h-5 sm:w-5 text-rose-600" />,
      bg: 'bg-rose-50/80 border-rose-100',
    },
    {
      title: 'Resolved',
      value: stats?.resolved_tickets ?? 0,
      icon: <CheckCircle2 className="h-4 w-4 sm:h-5 sm:w-5 text-emerald-600" />,
      bg: 'bg-emerald-50/80 border-emerald-100',
    },
  ];

  return (
    <div className="grid grid-cols-2 gap-2.5 sm:gap-4 lg:grid-cols-4 mb-4 sm:mb-6">
      {cards.map((card, idx) => (
        <div
          key={idx}
          className={`flex items-center justify-between rounded-xl border p-3 sm:p-4 shadow-xs transition-all hover:shadow-sm ${card.bg}`}
        >
          <div>
            <p className="text-[10px] sm:text-xs font-semibold text-slate-500 uppercase tracking-tight">{card.title}</p>
            <h3 className="text-xl sm:text-2xl font-bold text-slate-900 mt-0.5">
              {isLoading ? '...' : card.value}
            </h3>
          </div>
          <div className="rounded-lg bg-white/90 p-2 sm:p-2.5 shadow-xs shrink-0 ml-1.5">{card.icon}</div>
        </div>
      ))}
    </div>
  );
};
