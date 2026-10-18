export interface DocumentCitation {
  title: string;
  category: string;
  score: number;
}

export interface ChatMessage {
  id: string;
  sender: 'user' | 'assistant' | 'system';
  content: string;
  sentiment?: string;
  sentiment_score?: number;
  intent?: string;
  agent_trajectory?: string[];
  citations?: DocumentCitation[];
  model_used?: string | null;
  model_transition?: string | null;
  pacing_notice?: string | null;
  model_error?: string | null;
  created_at: string;
}

export interface ChatResponse {
  session_id: string;
  message: string;
  sentiment_label: string;
  sentiment_score: number;
  intent: string;
  escalation_required: boolean;
  ticket_number?: string | null;
  confidence_score: number;
  agent_trajectory: string[];
  citations: DocumentCitation[];
  model_used?: string | null;
  model_transition?: string | null;
  pacing_notice?: string | null;
  model_error?: string | null;
}

export interface Ticket {
  id: string;
  ticket_number: string;
  session_id: string | null;
  customer_name: string;
  customer_email: string | null;
  issue_summary: string;
  details: string | null;
  priority: 'low' | 'medium' | 'high' | 'urgent';
  status: 'open' | 'escalated' | 'in_progress' | 'resolved' | 'closed';
  sentiment_score: number | null;
  agent_notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface TicketStats {
  total_tickets: number;
  open_tickets: number;
  escalated_tickets: number;
  resolved_tickets: number;
  high_priority_tickets: number;
}

export interface KnowledgeDoc {
  id: string;
  title: string;
  category: string;
  content: string;
  metadata?: Record<string, any>;
}

export interface ModelOption {
  id: string;
  name: string;
  provider: string;
  status: string;
  is_current: boolean;
}
