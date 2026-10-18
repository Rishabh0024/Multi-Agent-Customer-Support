import React, { useState, useEffect, useRef } from 'react';
import { RotateCcw, LifeBuoy, AlertCircle, Clock } from 'lucide-react';
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
  const [loadingSeconds, setLoadingSeconds] = useState(0);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const sendMessageMutation = useSendMessage();
  const { data: historyData } = useChatHistory(sessionId);

  // Track pending duration for queue & rate pacing transparency
  useEffect(() => {
    let interval: any;
    if (sendMessageMutation.isPending) {
      setLoadingSeconds(0);
      interval = setInterval(() => {
        setLoadingSeconds((prev) => prev + 1);
      }, 1000);
    } else {
      setLoadingSeconds(0);
    }
    return () => clearInterval(interval);
  }, [sendMessageMutation.isPending]);

  // Sync session in localStorage
  useEffect(() => {
    localStorage.setItem('active_chat_session', sessionId);
  }, [sessionId]);

  // Load history if available
  useEffect(() => {
    if (historyData && historyData.length > 0) {
      setMessages(historyData);
      // Check if any message was escalated
      const lastEscalated = [...historyData].reverse().find((m) => m.intent === 'escalation_request' || m.content.includes('Support Ticket Created'));
      if (lastEscalated) {
        const match = lastEscalated.content.match(/#?TICK-\d+/);
        if (match) setEscalatedTicket(match[0].replace('#', ''));
      }
    } else if (messages.length === 0) {
      // Default clean welcome message
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
        model_used: response.model_used,
        model_transition: response.model_transition,
        pacing_notice: response.pacing_notice,
        model_error: response.model_error,
        created_at: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, assistantMsg]);

      if (response.escalation_required && response.ticket_number) {
        setEscalatedTicket(response.ticket_number);
      }
    } catch (error: any) {
      const errDetail = error?.response?.data?.detail || error?.message || 'Connection failure';
      const errorMsg: ChatMessage = {
        id: `err_${Date.now()}`,
        sender: 'assistant',
        content: '⚠️ **System Error:** Hamare backend ya AI model service se communicate karne me error aaya hai. Hallucination se bachne ke liye answer ko yahin rok diya gaya hai.',
        model_error: `Network/Server Error: ${errDetail}`,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMsg]);
    }
  };

  const handleNewChat = () => {
    const newId = generateSessionId();
    localStorage.setItem('active_chat_session', newId);
    setSessionId(newId);
    setEscalatedTicket(null);
    setMessages([
      {
        id: 'welcome',
        sender: 'assistant',
        content: 'Welcome to a fresh support session! How may I assist you today?',
        sentiment: 'positive',
        sentiment_score: 0.85,
        created_at: new Date().toISOString(),
        agent_trajectory: ['CoordinatorAgent', 'ResponseAgent']
      }
    ]);
  };

  return (
    <div className="flex h-[calc(100dvh-112px)] md:h-[calc(100vh-80px)] max-w-5xl mx-auto flex-col rounded-none md:rounded-2xl border-0 md:border border-slate-200 bg-white shadow-none md:shadow-xl overflow-hidden my-0 md:my-4">
      {/* Chat Header */}
      <div className="flex items-center justify-between border-b border-slate-200 bg-slate-50/80 px-3.5 py-2.5 sm:px-5 sm:py-3 backdrop-blur-sm">
        <div className="flex items-center gap-2.5">
          <div className="flex h-2.5 w-2.5 relative">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
          </div>
          <div>
            <h2 className="text-xs sm:text-sm font-bold text-slate-800 flex items-center gap-1.5">
              Support AI Assistant
              <span className="hidden sm:inline-flex rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200/60 text-[10px] px-2 py-0.2">
                Active
              </span>
            </h2>
            <p className="text-[10px] sm:text-xs text-slate-400 font-mono">
              Session: <span className="text-slate-600 font-semibold">{sessionId}</span>
            </p>
          </div>
        </div>

        <button
          onClick={handleNewChat}
          title="Start fresh conversation"
          className="flex items-center gap-1.5 rounded-xl border border-sky-200 bg-sky-50 px-2.5 py-1.5 sm:px-3 text-xs font-semibold text-sky-700 shadow-xs hover:bg-sky-100 transition-all active:scale-95"
        >
          <RotateCcw className="h-3.5 w-3.5 text-sky-600" />
          <span>New Chat</span>
        </button>
      </div>

      {/* Escalation Notification Bar */}
      {escalatedTicket && (
        <div className="flex items-center justify-between bg-amber-50/90 border-b border-amber-200 px-3.5 py-2 sm:px-5 sm:py-2.5 text-xs text-amber-900 animate-fadeIn">
          <div className="flex items-center gap-2">
            <AlertCircle className="h-4 w-4 text-amber-600 shrink-0" />
            <span className="text-[11px] sm:text-xs">
              <strong>Ticket #{escalatedTicket}:</strong> Assigned to human support desk.
            </span>
          </div>
          <button
            onClick={handleNewChat}
            className="text-[11px] text-amber-800 underline font-semibold hover:text-amber-950 shrink-0 ml-2"
          >
            Start Fresh Chat
          </button>
        </div>
      )}

      {/* Message History Body */}
      <div className="flex-1 overflow-y-auto px-3 py-3 sm:p-6 space-y-3.5 sm:space-y-4">
        {messages.map((msg) => (
          <ChatMessageItem key={msg.id} message={msg} sessionId={sessionId} />
        ))}

        {/* Loading Indicator with Queue & Rate Pacing Transparency */}
        {sendMessageMutation.isPending && (
          <div className="flex w-full gap-2.5 py-2 justify-start items-start animate-fadeIn">
            <div className="flex h-8 w-8 sm:h-9 sm:w-9 shrink-0 items-center justify-center rounded-xl bg-gradient-to-tr from-sky-600 to-indigo-600 text-white shadow-sm mt-0.5">
              <LifeBuoy className="h-4 w-4 sm:h-5 sm:w-5 animate-spin-slow" />
            </div>
            <div className="rounded-2xl rounded-tl-sm bg-white border border-slate-200 px-3.5 py-2.5 text-xs text-slate-600 shadow-xs flex flex-col gap-1.5 max-w-[85%] sm:max-w-[70%]">
              <div className="flex items-center gap-2">
                <span className="flex space-x-1 shrink-0">
                  <span className="h-2 w-2 bg-sky-500 rounded-full animate-bounce [animation-delay:-0.3s]"></span>
                  <span className="h-2 w-2 bg-sky-500 rounded-full animate-bounce [animation-delay:-0.15s]"></span>
                  <span className="h-2 w-2 bg-sky-500 rounded-full animate-bounce"></span>
                </span>
                <span className="text-[11px] sm:text-xs font-semibold text-slate-700">
                  {loadingSeconds < 3
                    ? 'Multi-agents coordinating (LangGraph RAG)...'
                    : 'Queue & rate-pacing active (Please be patient...)'}
                </span>
              </div>
              {loadingSeconds >= 2 && (
                <div className="flex items-center gap-1.5 text-[10px] sm:text-[11px] text-amber-800 bg-amber-50 rounded-lg px-2 py-1 border border-amber-200/80 font-mono">
                  <Clock className="h-3 w-3 text-amber-600 shrink-0" />
                  <span>Protecting model quota: request paced in FIFO queue ({loadingSeconds}s)...</span>
                </div>
              )}
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
