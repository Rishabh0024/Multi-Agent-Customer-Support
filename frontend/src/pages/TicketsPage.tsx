import React from 'react';
import { TicketStats } from '../components/Tickets/TicketStats';
import { TicketList } from '../components/Tickets/TicketList';

export const TicketsPage: React.FC = () => {
  return (
    <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6">
      <div className="mb-6">
        <h1 className="text-xl font-bold text-slate-800">Support Desk & Escalations</h1>
        <p className="text-xs text-slate-500 mt-1">
          Monitor conversations automatically escalated by the Sentiment & Escalation Agent.
        </p>
      </div>

      <TicketStats />
      <TicketList />
    </div>
  );
};
