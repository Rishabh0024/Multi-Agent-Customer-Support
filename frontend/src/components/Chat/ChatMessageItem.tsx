import React, { useState } from 'react';
import { Bot, User, ThumbsUp, ThumbsDown, GitFork, BookOpen, Check, Cpu, AlertTriangle } from 'lucide-react';
import { ChatMessage, DocumentCitation } from '../../types';
import { SentimentBadge } from './SentimentBadge';
import { useSubmitFeedback } from '../../services/api';

interface ChatMessageItemProps {
  message: ChatMessage;
  sessionId: string;
}

export const ChatMessageItem: React.FC<ChatMessageItemProps> = ({ message, sessionId }) => {
  const isAssistant = message.sender === 'assistant';
  const [feedbackGiven, setFeedbackGiven] = useState<'positive' | 'negative' | null>(null);
  const [showSources, setShowSources] = useState(false);
  const feedbackMutation = useSubmitFeedback();

  const handleFeedback = (rating: number) => {
    if (feedbackGiven) return;
    setFeedbackGiven(rating === 5 ? 'positive' : 'negative');
    feedbackMutation.mutate({
      session_id: sessionId,
      message_id: message.id,
      rating,
    });
  };

  return (
    <div className={`flex w-full gap-3 py-3 ${isAssistant ? 'justify-start' : 'justify-end'}`}>
      {/* Bot Icon */}
      {isAssistant && (
        <div className="flex h-7 w-7 sm:h-9 sm:w-9 shrink-0 select-none items-center justify-center rounded-xl bg-gradient-to-tr from-sky-600 to-indigo-600 text-white shadow-sm mt-0.5">
          <Bot className="h-4 w-4 sm:h-5 sm:w-5" />
        </div>
      )}

      {/* Message Bubble Container */}
      <div className={`flex flex-col max-w-[92%] sm:max-w-[80%] ${isAssistant ? 'items-start' : 'items-end'}`}>
        {/* Header Details for Assistant */}
        {isAssistant && (
          <div className="mb-1.5 flex flex-wrap items-center gap-1.5 sm:gap-2">
            <span className="text-[11px] sm:text-xs font-semibold text-slate-800">Support AI</span>

            {/* Active Model Badge */}
            <span className="inline-flex items-center gap-1 rounded-md bg-indigo-50 px-1.5 py-0.5 text-[10px] sm:text-[11px] font-mono font-medium text-indigo-700 border border-indigo-200/80">
              <Cpu className="h-2.5 w-2.5 sm:h-3 sm:w-3 text-indigo-600" />
              {message.model_used || 'gemini-flash-latest'}
            </span>

            {message.sentiment && (
              <SentimentBadge label={message.sentiment} score={message.sentiment_score ?? 0.5} />
            )}
            {message.intent && (
              <span className="rounded-md bg-slate-100 px-1.5 py-0.5 text-[10px] sm:text-[11px] font-medium text-slate-600 border border-slate-200">
                {message.intent}
              </span>
            )}
          </div>
        )}

        {/* Model Error / Failover Alert Card */}
        {isAssistant && message.model_error && (
          <div className="mb-2 w-full rounded-xl border border-amber-200 bg-amber-50/90 p-2.5 text-xs text-amber-900 shadow-xs">
            <div className="flex items-center gap-1.5 font-bold text-amber-950 text-[11px] sm:text-xs">
              <AlertTriangle className="h-3.5 w-3.5 text-amber-600 shrink-0" />
              <span>Model Failover / System Alert</span>
            </div>
            <p className="mt-1 text-[10px] sm:text-[11px] text-amber-800 font-mono leading-relaxed">
              {message.model_error}
            </p>
          </div>
        )}

        {/* Message Bubble */}
        <div
          className={`rounded-2xl px-3.5 py-2.5 sm:px-4 sm:py-3 text-xs sm:text-sm leading-relaxed shadow-xs transition-all ${
            isAssistant
              ? 'bg-white text-slate-800 border border-slate-200/90 rounded-tl-sm'
              : 'bg-sky-600 text-white rounded-tr-sm shadow-sky-600/10'
          }`}
        >
          <div className="whitespace-pre-wrap">{message.content}</div>

          {/* Citations Box */}
          {isAssistant && message.citations && message.citations.length > 0 && (
            <div className="mt-3 border-t border-slate-100 pt-2.5">
              <button
                onClick={() => setShowSources(!showSources)}
                className="flex items-center gap-1.5 text-xs font-medium text-sky-600 hover:text-sky-700"
              >
                <BookOpen className="h-3.5 w-3.5" />
                <span>{showSources ? 'Hide Sources' : `View ${message.citations.length} Knowledge Sources`}</span>
              </button>

              {showSources && (
                <div className="mt-2 space-y-1.5">
                  {message.citations.map((c: DocumentCitation, idx: number) => (
                    <div
                      key={idx}
                      className="flex items-center justify-between rounded-lg bg-slate-50 px-2.5 py-1.5 text-xs text-slate-600 border border-slate-100"
                    >
                      <span className="font-medium text-slate-700 truncate max-w-[80%]">
                        📄 {c.title}
                      </span>
                      <span className="rounded bg-sky-100 px-1.5 py-0.5 text-[10px] font-semibold text-sky-700">
                        Match {(c.score * 100).toFixed(0)}%
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Agent Trajectory Footer for Assistant */}
        {isAssistant && (
          <div className="mt-1.5 flex flex-wrap items-center gap-3 text-xs text-slate-400">
            {message.agent_trajectory && message.agent_trajectory.length > 0 && (
              <div className="flex items-center gap-1 text-[11px] text-slate-500 bg-slate-100/70 rounded-md px-2 py-0.5">
                <GitFork className="h-3 w-3 text-indigo-500" />
                <span className="font-mono">{message.agent_trajectory.join(' → ')}</span>
              </div>
            )}

            {/* Feedback Actions */}
            <div className="flex items-center gap-1">
              {feedbackGiven ? (
                <span className="flex items-center gap-1 text-[11px] text-emerald-600 font-medium">
                  <Check className="h-3 w-3" /> Feedback saved
                </span>
              ) : (
                <>
                  <button
                    onClick={() => handleFeedback(5)}
                    className="rounded p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-600 transition-colors"
                    title="Helpful response"
                  >
                    <ThumbsUp className="h-3.5 w-3.5" />
                  </button>
                  <button
                    onClick={() => handleFeedback(1)}
                    className="rounded p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-600 transition-colors"
                    title="Needs improvement"
                  >
                    <ThumbsDown className="h-3.5 w-3.5" />
                  </button>
                </>
              )}
            </div>
          </div>
        )}
      </div>

      {/* User Icon */}
      {!isAssistant && (
        <div className="flex h-9 w-9 shrink-0 select-none items-center justify-center rounded-xl bg-slate-200 text-slate-700">
          <User className="h-5 w-5" />
        </div>
      )}
    </div>
  );
};
