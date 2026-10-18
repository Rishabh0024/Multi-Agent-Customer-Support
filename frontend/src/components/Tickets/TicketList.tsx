import React, { useState } from 'react';
import { Filter, Clock, User } from 'lucide-react';
import { Ticket } from '../../types';
import { useTickets, useUpdateTicketStatus } from '../../services/api';
import { SentimentBadge } from '../Chat/SentimentBadge';

export const TicketList: React.FC = () => {
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [priorityFilter, setPriorityFilter] = useState<string>('all');
  const [selectedTicket, setSelectedTicket] = useState<Ticket | null>(null);
  const [agentNotes, setAgentNotes] = useState<string>('');

  const { data: tickets, isLoading, refetch } = useTickets(statusFilter, priorityFilter);
  const updateStatusMutation = useUpdateTicketStatus();

  const handleStatusChange = (ticketId: string, newStatus: string) => {
    updateStatusMutation.mutate({
      ticket_id: ticketId,
      status: newStatus,
      agent_notes: agentNotes || undefined,
    });
  };

  const priorityBadges: Record<string, string> = {
    urgent: 'bg-rose-100 text-rose-800 border-rose-200',
    high: 'bg-amber-100 text-amber-800 border-amber-200',
    medium: 'bg-sky-100 text-sky-800 border-sky-200',
    low: 'bg-slate-100 text-slate-800 border-slate-200',
  };

  return (
    <div className="rounded-2xl border border-slate-200 bg-white shadow-sm overflow-hidden">
      {/* Filters Toolbar */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-200 p-4 bg-slate-50/60">
        <div className="flex items-center gap-2">
          <Filter className="h-4 w-4 text-slate-500" />
          <span className="text-xs font-semibold text-slate-600 uppercase">Filters:</span>

          {/* Status Filter */}
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="rounded-lg border border-slate-300 bg-white px-2.5 py-1.5 text-xs font-medium text-slate-700 shadow-sm focus:border-sky-500 focus:outline-none"
          >
            <option value="all">All Statuses</option>
            <option value="escalated">Escalated by AI</option>
            <option value="open">Open</option>
            <option value="in_progress">In Progress</option>
            <option value="resolved">Resolved</option>
          </select>

          {/* Priority Filter */}
          <select
            value={priorityFilter}
            onChange={(e) => setPriorityFilter(e.target.value)}
            className="rounded-lg border border-slate-300 bg-white px-2.5 py-1.5 text-xs font-medium text-slate-700 shadow-sm focus:border-sky-500 focus:outline-none"
          >
            <option value="all">All Priorities</option>
            <option value="urgent">Urgent</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
        </div>

        <button
          onClick={() => refetch()}
          className="rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs font-medium text-slate-600 hover:bg-slate-50 shadow-sm"
        >
          Refresh Desk
        </button>
      </div>

      {/* Ticket Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs text-slate-600">
          <thead className="bg-slate-50 text-[11px] font-semibold uppercase text-slate-400 border-b border-slate-200">
            <tr>
              <th className="px-5 py-3">Ticket #</th>
              <th className="px-5 py-3">Customer</th>
              <th className="px-5 py-3">Issue Summary</th>
              <th className="px-5 py-3">Sentiment</th>
              <th className="px-5 py-3">Priority</th>
              <th className="px-5 py-3">Status</th>
              <th className="px-5 py-3">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200">
            {isLoading ? (
              <tr>
                <td colSpan={7} className="text-center py-8 text-slate-400">
                  Loading tickets from PostgreSQL...
                </td>
              </tr>
            ) : !tickets || tickets.length === 0 ? (
              <tr>
                <td colSpan={7} className="text-center py-10 text-slate-400">
                  No tickets found matching the filter criteria.
                </td>
              </tr>
            ) : (
              tickets.map((t) => (
                <tr key={t.id} className="hover:bg-slate-50/70 transition-colors">
                  <td className="px-5 py-3.5 font-mono font-bold text-sky-700">
                    {t.ticket_number}
                  </td>
                  <td className="px-5 py-3.5">
                    <div className="flex items-center gap-1.5 font-medium text-slate-800">
                      <User className="h-3.5 w-3.5 text-slate-400" />
                      {t.customer_name}
                    </div>
                    {t.customer_email && (
                      <span className="text-[10px] text-slate-400 block">{t.customer_email}</span>
                    )}
                  </td>
                  <td className="px-5 py-3.5 max-w-xs">
                    <p className="line-clamp-2 text-slate-700 font-medium">{t.issue_summary}</p>
                    <span className="text-[10px] text-slate-400 flex items-center gap-1 mt-0.5">
                      <Clock className="h-3 w-3" />
                      {new Date(t.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </span>
                  </td>
                  <td className="px-5 py-3.5">
                    <SentimentBadge
                      label={t.sentiment_score && t.sentiment_score <= 0.35 ? 'frustrated' : 'neutral'}
                      score={t.sentiment_score ?? 0.3}
                    />
                  </td>
                  <td className="px-5 py-3.5">
                    <span
                      className={`inline-block rounded-md border px-2 py-0.5 text-[11px] font-semibold uppercase tracking-wider ${
                        priorityBadges[t.priority] || priorityBadges.medium
                      }`}
                    >
                      {t.priority}
                    </span>
                  </td>
                  <td className="px-5 py-3.5">
                    <select
                      value={t.status}
                      onChange={(e) => handleStatusChange(t.id, e.target.value)}
                      className="rounded-md border border-slate-300 bg-white px-2 py-1 text-xs font-medium text-slate-800 shadow-xs focus:border-sky-500 focus:outline-none"
                    >
                      <option value="escalated">Escalated</option>
                      <option value="open">Open</option>
                      <option value="in_progress">In Progress</option>
                      <option value="resolved">Resolved</option>
                      <option value="closed">Closed</option>
                    </select>
                  </td>
                  <td className="px-5 py-3.5">
                    <button
                      onClick={() => {
                        setSelectedTicket(t);
                        setAgentNotes(t.agent_notes || '');
                      }}
                      className="rounded border border-slate-200 px-2 py-1 text-xs font-semibold text-sky-600 hover:bg-sky-50"
                    >
                      Details
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Detail Modal */}
      {selectedTicket && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 backdrop-blur-xs p-4">
          <div className="w-full max-w-lg rounded-2xl bg-white p-6 shadow-2xl border border-slate-200">
            <div className="flex items-center justify-between border-b pb-3 mb-4">
              <div>
                <h3 className="text-base font-bold text-slate-800">
                  Ticket #{selectedTicket.ticket_number}
                </h3>
                <span className="text-xs text-slate-400">Created: {selectedTicket.created_at}</span>
              </div>
              <button
                onClick={() => setSelectedTicket(null)}
                className="text-slate-400 hover:text-slate-600 text-sm font-bold"
              >
                ✕
              </button>
            </div>

            <div className="space-y-3 text-xs">
              <div>
                <label className="font-semibold text-slate-500 uppercase">Customer Details</label>
                <p className="text-sm font-medium text-slate-800">{selectedTicket.customer_name}</p>
                <p className="text-slate-500">{selectedTicket.customer_email || 'No email registered'}</p>
              </div>

              <div>
                <label className="font-semibold text-slate-500 uppercase">Issue Summary</label>
                <p className="rounded-lg bg-slate-50 p-2.5 text-slate-700 border border-slate-100">
                  {selectedTicket.issue_summary}
                </p>
              </div>

              {selectedTicket.details && (
                <div>
                  <label className="font-semibold text-slate-500 uppercase">Conversation Logs / Context</label>
                  <p className="rounded-lg bg-slate-50 p-2.5 text-slate-700 font-mono text-[11px] whitespace-pre-wrap border border-slate-100">
                    {selectedTicket.details}
                  </p>
                </div>
              )}

              <div>
                <label className="font-semibold text-slate-500 uppercase">Human Agent Notes</label>
                <textarea
                  value={agentNotes}
                  onChange={(e) => setAgentNotes(e.target.value)}
                  placeholder="Enter resolution notes, refund ID, or steps taken..."
                  className="w-full rounded-lg border border-slate-300 p-2.5 text-xs text-slate-800 focus:border-sky-500 focus:outline-none"
                  rows={3}
                />
              </div>
            </div>

            <div className="mt-5 flex justify-end gap-2 border-t pt-3">
              <button
                onClick={() => setSelectedTicket(null)}
                className="rounded-lg border border-slate-200 px-3 py-1.5 text-xs font-medium text-slate-600 hover:bg-slate-50"
              >
                Close
              </button>
              <button
                onClick={() => {
                  handleStatusChange(selectedTicket.id, 'resolved');
                  setSelectedTicket(null);
                }}
                className="rounded-lg bg-emerald-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-emerald-700"
              >
                Mark as Resolved
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
