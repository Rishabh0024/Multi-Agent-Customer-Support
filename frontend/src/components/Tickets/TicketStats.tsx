import React from 'react';
import { LifeBuoy, CheckCircle2, Flame, Layers } from 'lucide-react';
import { useTicketStats } from '../../services/api';

export const TicketStats: React.FC = () => {
  const { data: stats, isLoading } = useTicketStats();

  const cards = [
    {
      title: 'Total Tickets',
      value: stats?.total_tickets ?? 0,
      icon: <Layers className="h-5 w-5 text-indigo-600" />,
      bg: 'bg-indigo-50 border-indigo-100',
    },
    {
      title: 'Escalated by AI',
      value: stats?.escalated_tickets ?? 0,
      icon: <LifeBuoy className="h-5 w-5 text-amber-600" />,
      bg: 'bg-amber-50 border-amber-100',
    },
    {
      title: 'High / Urgent Priority',
      value: stats?.high_priority_tickets ?? 0,
      icon: <Flame className="h-5 w-5 text-rose-600" />,
      bg: 'bg-rose-50 border-rose-100',
    },
    {
      title: 'Resolved Cases',
      value: stats?.resolved_tickets ?? 0,
      icon: <CheckCircle2 className="h-5 w-5 text-emerald-600" />,
      bg: 'bg-emerald-50 border-emerald-100',
    },
  ];

  return (
    <div className="grid grid-cols-2 gap-4 sm:grid-cols-4 mb-6">
      {cards.map((card, idx) => (
        <div
          key={idx}
          className={`flex items-center justify-between rounded-xl border p-4 shadow-sm transition-all hover:shadow-md ${card.bg}`}
        >
          <div>
            <p className="text-xs font-medium text-slate-500 uppercase tracking-wider">{card.title}</p>
            <h3 className="text-2xl font-bold text-slate-900 mt-1">
              {isLoading ? '...' : card.value}
            </h3>
          </div>
          <div className="rounded-lg bg-white/80 p-2.5 shadow-sm">{card.icon}</div>
        </div>
      ))}
    </div>
  );
};
