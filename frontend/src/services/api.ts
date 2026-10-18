import axios from 'axios';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { ChatResponse, Ticket, TicketStats, KnowledgeDoc } from '../types';

let rawApiUrl = (import.meta.env.VITE_API_URL || import.meta.env.VITE_API_BASE_URL || '').trim().replace(/\/+$/, '');
if (rawApiUrl.endsWith('/api')) {
  rawApiUrl = rawApiUrl.substring(0, rawApiUrl.length - 4);
}
const API_BASE_URL = rawApiUrl;

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Keys
export const queryKeys = {
  chatHistory: (sessionId: string) => ['chat', 'history', sessionId],
  tickets: (status?: string, priority?: string) => ['tickets', { status, priority }],
  ticketStats: ['tickets', 'stats'],
  ticketDetail: (id: string) => ['tickets', 'detail', id],
  knowledgeList: ['knowledge', 'list'],
  health: ['system', 'health'],
};

// Chat Hooks
export const useChatHistory = (sessionId: string) => {
  return useQuery({
    queryKey: queryKeys.chatHistory(sessionId),
    queryFn: async () => {
      const { data } = await apiClient.get(`/api/chat/${sessionId}/history`);
      return data;
    },
    enabled: Boolean(sessionId),
  });
};

export const useSendMessage = () => {
  return useMutation({
    mutationFn: async (payload: {
      session_id: string;
      message: string;
      user_name?: string;
      user_email?: string;
    }): Promise<ChatResponse> => {
      const { data } = await apiClient.post('/api/chat', payload);
      return data;
    },
  });
};

export const useSubmitFeedback = () => {
  return useMutation({
    mutationFn: async (payload: {
      session_id: string;
      message_id: string;
      rating: number;
      comment?: string;
    }) => {
      const { data } = await apiClient.post('/api/chat/feedback', payload);
      return data;
    },
  });
};

// Ticket Hooks
export const useTickets = (status?: string, priority?: string) => {
  return useQuery({
    queryKey: queryKeys.tickets(status, priority),
    queryFn: async (): Promise<Ticket[]> => {
      const params: Record<string, string> = {};
      if (status && status !== 'all') params.status = status;
      if (priority && priority !== 'all') params.priority = priority;
      const { data } = await apiClient.get('/api/tickets', { params });
      return data;
    },
    refetchInterval: 10000, // Poll every 10s for new escalated tickets
  });
};

export const useTicketStats = () => {
  return useQuery({
    queryKey: queryKeys.ticketStats,
    queryFn: async (): Promise<TicketStats> => {
      const { data } = await apiClient.get('/api/tickets/stats');
      return data;
    },
    refetchInterval: 10000,
  });
};

export const useUpdateTicketStatus = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: {
      ticket_id: string;
      status: string;
      agent_notes?: string;
    }) => {
      const { data } = await apiClient.patch(`/api/tickets/${payload.ticket_id}/status`, {
        status: payload.status,
        agent_notes: payload.agent_notes,
      });
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tickets'] });
    },
  });
};

// Knowledge Hooks
export const useKnowledgeDocs = () => {
  return useQuery({
    queryKey: queryKeys.knowledgeList,
    queryFn: async (): Promise<KnowledgeDoc[]> => {
      const { data } = await apiClient.get('/api/knowledge/list');
      return data;
    },
  });
};

export const useIndexKnowledgeDoc = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: { title: string; category: string; content: string }) => {
      const { data } = await apiClient.post('/api/knowledge/index', payload);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.knowledgeList });
    },
  });
};

export const useDeleteKnowledgeDoc = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (docId: string) => {
      const { data } = await apiClient.delete(`/api/knowledge/${docId}`);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.knowledgeList });
    },
  });
};

// Health Hook
export const useSystemHealth = () => {
  return useQuery({
    queryKey: queryKeys.health,
    queryFn: async () => {
      const { data } = await apiClient.get('/api/health');
      return data;
    },
  });
};
