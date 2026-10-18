import React, { useState } from 'react';
import { Filter, Clock, User, X, RefreshCw } from 'lucide-react';
import { Ticket } from '../../types';
import { useTickets, useUpdateTicketStatus } from '../../services/api';
import { SentimentBadge } from '../Chat/SentimentBadge';

export const TicketList: React.FC = () => {
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [priorityFilter, setPriorityFilter] = useState<string>('all');
  const [selectedTicket, setSelectedTicket] = useState<Ticket | null>(null);
  const [agentNotes, setAgentNotes] = useState<string>('');

  const { data: tickets, isLoading, isFetching, refetch } = useTickets(statusFilter, priorityFilter);
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
    <div className="rounded-2xl border border-slate-200 bg-white shadow-xs overflow-hidden">
      {/* Filters Toolbar */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 border-b border-slate-200 p-3.5 sm:p-4 bg-slate-50/70">
        <div className="flex flex-wrap items-center gap-2">
          <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-600 uppercase tracking-wider shrink-0">
            <Filter className="h-3.5 w-3.5 text-slate-500" />
            <span>Filter:</span>
          </div>

          {/* Status Filter */}
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="flex-1 sm:flex-none rounded-lg border border-slate-300 bg-white px-2.5 py-1.5 text-xs font-medium text-slate-700 shadow-xs focus:border-sky-500 focus:outline-none"
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
            className="flex-1 sm:flex-none rounded-lg border border-slate-300 bg-white px-2.5 py-1.5 text-xs font-medium text-slate-700 shadow-xs focus:border-sky-500 focus:outline-none"
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
          disabled={isFetching}
          className="flex items-center justify-center gap-1.5 rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs font-semibold text-slate-700 hover:bg-slate-50 shadow-xs active:scale-95 transition-all"
        >
          <RefreshCw className={`h-3.5 w-3.5 text-slate-500 ${isFetching ? 'animate-spin' : ''}`} />
          <span>{isFetching ? 'Refreshing...' : 'Refresh Desk'}</span>
        </button>
      </div>

      {/* Mobile Card Feed (Smartphones < 768px) */}
      <div className="md:hidden divide-y divide-slate-100">
        {isLoading ? (
          <div className="text-center py-10 text-xs text-slate-400">Loading escalated tickets...</div>
        ) : !tickets || tickets.length === 0 ? (
          <div className="text-center py-12 text-xs text-slate-400 px-4">
            No escalated tickets matching filter criteria.
          </div>
        ) : (
          tickets.map((t) => (
            <div key={t.id} className="p-3.5 space-y-2.5 bg-white hover:bg-slate-50/50 transition-colors">
              <div className="flex items-center justify-between">
                <span className="font-mono font-bold text-sky-700 text-xs tracking-tight">
                  {t.ticket_number}
                </span>
                <span
                  className={`rounded-md border px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider ${
                    priorityBadges[t.priority] || priorityBadges.medium
                  }`}
                >
                  {t.priority}
                </span>
              </div>

              <div>
                <p className="text-xs font-semibold text-slate-800 line-clamp-2 leading-relaxed">
                  {t.issue_summary}
                </p>
                <div className="flex items-center justify-between mt-1.5 text-[11px] text-slate-400">
                  <span className="flex items-center gap-1 text-slate-600 font-medium truncate max-w-[160px]">
                    <User className="h-3 w-3 text-slate-400 shrink-0" />
                    {t.customer_name}
                  </span>
                  <span className="flex items-center gap-1 shrink-0">
                    <Clock className="h-3 w-3" />
                    {new Date(t.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>
              </div>

              <div className="flex items-center justify-between pt-1 border-t border-slate-100">
                <select
                  value={t.status}
                  onChange={(e) => handleStatusChange(t.id, e.target.value)}
                  className="rounded-lg border border-slate-300 bg-white px-2 py-1 text-xs font-medium text-slate-800 shadow-xs focus:border-sky-500 focus:outline-none"
                >
                  <option value="escalated">Escalated</option>
                  <option value="open">Open</option>
                  <option value="in_progress">In Progress</option>
                  <option value="resolved">Resolved</option>
                  <option value="closed">Closed</option>
                </select>

                <button
                  onClick={() => {
                    setSelectedTicket(t);
                    setAgentNotes(t.agent_notes || '');
                  }}
                  className="rounded-lg border border-sky-200 bg-sky-50 px-3 py-1 text-xs font-semibold text-sky-700 hover:bg-sky-100 transition-colors"
                >
                  View Details
                </button>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Desktop Table (Tablet/Desktop >= 768px) */}
      <div className="hidden md:block overflow-x-auto">
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

      {/* Responsive Detail Modal */}
      {selectedTicket && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-xs p-3 sm:p-4">
          <div className="w-full max-w-lg rounded-2xl bg-white p-5 sm:p-6 shadow-2xl border border-slate-200 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between border-b border-slate-200 pb-3 mb-4">
              <div>
                <h3 className="text-base font-bold text-slate-800">
                  Ticket #{selectedTicket.ticket_number}
                </h3>
                <span className="text-[11px] text-slate-400">
                  Created: {new Date(selectedTicket.created_at).toLocaleString()}
                </span>
              </div>
              <button
                onClick={() => setSelectedTicket(null)}
                className="text-slate-400 hover:text-slate-600 rounded-lg p-1"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            <div className="space-y-3.5 text-xs">
              <div>
                <label className="font-semibold text-slate-400 uppercase tracking-tight text-[10px]">
                  Customer Details
                </label>
                <p className="text-sm font-semibold text-slate-800 mt-0.5">{selectedTicket.customer_name}</p>
                <p className="text-slate-500">{selectedTicket.customer_email || 'No email registered'}</p>
              </div>

              <div>
                <label className="font-semibold text-slate-400 uppercase tracking-tight text-[10px]">
                  Issue Summary
                </label>
                <p className="rounded-xl bg-slate-50 p-3 text-slate-700 border border-slate-200/80 mt-1 leading-relaxed">
                  {selectedTicket.issue_summary}
                </p>
              </div>

              {selectedTicket.details && (
                <div>
                  <label className="font-semibold text-slate-400 uppercase tracking-tight text-[10px]">
                    Context & Reasoning
                  </label>
                  <p className="rounded-xl bg-slate-50 p-3 text-slate-700 font-mono text-[11px] whitespace-pre-wrap border border-slate-200/80 mt-1">
                    {selectedTicket.details}
                  </p>
                </div>
              )}

              <div>
                <label className="font-semibold text-slate-400 uppercase tracking-tight text-[10px]">
                  Support Specialist Notes
                </label>
                <textarea
                  value={agentNotes}
                  onChange={(e) => setAgentNotes(e.target.value)}
                  placeholder="Add resolution notes, refund confirmation ID, or actions taken..."
                  className="w-full rounded-xl border border-slate-300 p-2.5 text-xs text-slate-800 focus:border-sky-500 focus:outline-none mt-1"
                  rows={3}
                />
              </div>
            </div>

            <div className="mt-5 flex justify-end gap-2 border-t border-slate-200 pt-3">
              <button
                onClick={() => setSelectedTicket(null)}
                className="rounded-xl border border-slate-200 px-3.5 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-50 transition-colors"
              >
                Close
              </button>
              <button
                onClick={() => {
                  handleStatusChange(selectedTicket.id, 'resolved');
                  setSelectedTicket(null);
                }}
                className="rounded-xl bg-emerald-600 px-4 py-2 text-xs font-semibold text-white hover:bg-emerald-700 transition-colors shadow-xs"
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
