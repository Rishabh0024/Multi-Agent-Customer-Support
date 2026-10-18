import React, { useState, useEffect, useRef } from 'react';
import { RotateCcw, LifeBuoy } from 'lucide-react';
import { ChatMessage, ChatResponse } from '../../types';
import { ChatMessageItem } from './ChatMessageItem';
import { ChatInput } from './ChatInput';
import { useSendMessage, useChatHistory } from '../../services/api';

const generateSessionId = () => `sess_${Math.random().toString(36).substring(2, 10)}`;

export const ChatWindow: React.FC = () => {
  const [sessionId, setSessionId] = useState<string>(() => {
    return localStorage.getItem('active_chat_session') || generateSessionId();
  });
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [escalatedTicket, setEscalatedTicket] = useState<string | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const sendMessageMutation = useSendMessage();
  const { data: historyData } = useChatHistory(sessionId);

  // Sync session in localStorage
  useEffect(() => {
    localStorage.setItem('active_chat_session', sessionId);
  }, [sessionId]);

  // Load history if available
  useEffect(() => {
    if (historyData && historyData.length > 0) {
      setMessages(historyData);
    } else if (messages.length === 0) {
      // Default welcome message
      setMessages([
        {
          id: 'welcome',
          sender: 'assistant',
          content: 'Hello! I am your AI Customer Support Assistant. How can I assist you with your orders, returns, warranty, or account today?',
          sentiment: 'positive',
          sentiment_score: 0.8,
          created_at: new Date().toISOString(),
          agent_trajectory: ['CoordinatorAgent', 'ResponseAgent']
        }
      ]);
    }
  }, [historyData]);

  // Auto scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, sendMessageMutation.isPending]);

  const handleSendMessage = async (text: string) => {
    const userMsg: ChatMessage = {
      id: `user_${Date.now()}`,
      sender: 'user',
      content: text,
      created_at: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMsg]);

    try {
      const response: ChatResponse = await sendMessageMutation.mutateAsync({
        session_id: sessionId,
        message: text,
      });

      const assistantMsg: ChatMessage = {
        id: `ast_${Date.now()}`,
        sender: 'assistant',
        content: response.message,
        sentiment: response.sentiment_label,
        sentiment_score: response.sentiment_score,
        intent: response.intent,
        agent_trajectory: response.agent_trajectory,
        citations: response.citations,
        created_at: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, assistantMsg]);

      if (response.escalation_required && response.ticket_number) {
        setEscalatedTicket(response.ticket_number);
      }
    } catch (error) {
      const errorMsg: ChatMessage = {
        id: `err_${Date.now()}`,
        sender: 'assistant',
        content: 'I apologize, but I encountered an error communicating with our services. Please try again or refresh the page.',
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMsg]);
    }
  };

  const handleNewChat = () => {
    const newId = generateSessionId();
    setSessionId(newId);
    setEscalatedTicket(null);
    setMessages([
      {
        id: 'welcome',
        sender: 'assistant',
        content: 'Welcome to a new support session! How may I assist you today?',
        sentiment: 'positive',
        sentiment_score: 0.8,
        created_at: new Date().toISOString(),
        agent_trajectory: ['CoordinatorAgent', 'ResponseAgent']
      }
    ]);
  };

  return (
    <div className="flex h-[calc(100vh-80px)] max-w-5xl mx-auto flex-col rounded-2xl border border-slate-200 bg-white shadow-xl overflow-hidden my-4">
      {/* Chat Header */}
      <div className="flex items-center justify-between border-b border-slate-200 bg-slate-50/70 px-5 py-3.5 backdrop-blur-sm">
        <div className="flex items-center gap-3">
          <div className="flex h-3 w-3 relative">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
          </div>
          <div>
            <h2 className="text-sm font-bold text-slate-800">Support Chat Assistant</h2>
            <p className="text-xs text-slate-400 font-mono">Session: {sessionId}</p>
          </div>
        </div>

        <button
          onClick={handleNewChat}
          className="flex items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs font-semibold text-slate-700 shadow-sm hover:bg-slate-50 transition-colors"
        >
          <RotateCcw className="h-3.5 w-3.5 text-slate-500" />
          <span>New Session</span>
        </button>
      </div>

      {/* Escalation Notification Bar */}
      {escalatedTicket && (
        <div className="flex items-center justify-between bg-amber-50 border-b border-amber-200 px-5 py-2.5 text-xs text-amber-800">
          <div className="flex items-center gap-2">
            <LifeBuoy className="h-4 w-4 text-amber-600 animate-pulse" />
            <span>
              <strong>Ticket #{escalatedTicket} Created:</strong> This conversation has been escalated to our human support desk.
            </span>
          </div>
          <span className="rounded bg-amber-200/70 px-2 py-0.5 font-bold uppercase tracking-wider text-[10px]">
            In Queue
          </span>
        </div>
      )}

      {/* Message History Body */}
      <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-4">
        {messages.map((msg) => (
          <ChatMessageItem key={msg.id} message={msg} sessionId={sessionId} />
        ))}

        {/* Loading Indicator */}
        {sendMessageMutation.isPending && (
          <div className="flex w-full gap-3 py-3 justify-start items-center">
            <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-gradient-to-tr from-sky-600 to-indigo-600 text-white shadow-sm animate-pulse">
              <LifeBuoy className="h-5 w-5" />
            </div>
            <div className="rounded-2xl rounded-tl-sm bg-white border border-slate-200 px-4 py-3 text-sm text-slate-500 shadow-sm flex items-center gap-3">
              <span className="flex space-x-1.5">
                <span className="h-2 w-2 bg-sky-500 rounded-full animate-bounce [animation-delay:-0.3s]"></span>
                <span className="h-2 w-2 bg-sky-500 rounded-full animate-bounce [animation-delay:-0.15s]"></span>
                <span className="h-2 w-2 bg-sky-500 rounded-full animate-bounce"></span>
              </span>
              <span className="text-xs font-medium text-slate-500 font-mono">
                Multi-agents collaborating (Coordinator → RAG / Sentiment)...
              </span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <ChatInput onSendMessage={handleSendMessage} isLoading={sendMessageMutation.isPending} />
    </div>
  );
};
