import React from 'react';
import { TicketStats } from '../components/Tickets/TicketStats';
import { TicketList } from '../components/Tickets/TicketList';

export const TicketsPage: React.FC = () => {
  return (
    <div className="mx-auto max-w-7xl px-3 py-3.5 sm:px-6 sm:py-6">
      <div className="mb-4 sm:mb-6">
        <h1 className="text-lg sm:text-xl font-bold text-slate-800">Support Desk & Escalations</h1>
        <p className="text-xs text-slate-500 mt-0.5">
          Live tickets automatically escalated by the Multi-Agent Sentiment pipeline.
        </p>
      </div>

      <TicketStats />
      <TicketList />
    </div>
  );
};
