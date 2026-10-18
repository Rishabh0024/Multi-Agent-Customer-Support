import React, { useState, KeyboardEvent } from 'react';
import { Send, Sparkles } from 'lucide-react';

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  isLoading: boolean;
}

const SAMPLE_PROMPTS = [
  'What is your 30-day return policy?',
  'My item arrived completely broken, this is unacceptable!',
  'How do I claim the 1-year hardware warranty?',
  'Can I cancel an order placed 30 minutes ago?',
  'Connect me with a human support manager right now.',
];

export const ChatInput: React.FC<ChatInputProps> = ({ onSendMessage, isLoading }) => {
  const [input, setInput] = useState('');

  const handleSend = () => {
    if (input.trim() && !isLoading) {
      onSendMessage(input.trim());
      setInput('');
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="w-full">
      {/* Quick Prompts Suggestions */}
      <div className="mb-2 flex items-center gap-1.5 overflow-x-auto pb-1 text-xs no-scrollbar scroll-smooth">
        <span className="flex items-center gap-1 font-semibold text-slate-400 shrink-0 text-[10px] sm:text-[11px] uppercase tracking-wider">
          <Sparkles className="h-3 w-3 text-amber-500 shrink-0" />
          <span>Suggestions:</span>
        </span>
        {SAMPLE_PROMPTS.map((prompt, idx) => (
          <button
            key={idx}
            type="button"
            disabled={isLoading}
            onClick={() => onSendMessage(prompt)}
            className="shrink-0 rounded-full bg-slate-100/90 hover:bg-sky-50 hover:text-sky-700 hover:border-sky-200 px-3 py-1 text-[11px] sm:text-xs text-slate-600 font-medium transition-all border border-slate-200/80 active:scale-95 disabled:opacity-50"
          >
            {prompt}
          </button>
        ))}
      </div>

      {/* Input Form Capsule */}
      <div className="flex items-center gap-2 rounded-2xl border border-slate-300/90 bg-white px-3.5 py-1.5 sm:py-2 focus-within:border-sky-500 focus-within:ring-3 focus-within:ring-sky-500/15 transition-all shadow-sm">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type your question or support issue..."
          disabled={isLoading}
          className="w-full bg-transparent text-xs sm:text-sm text-slate-800 placeholder-slate-400 focus:outline-none disabled:opacity-50 py-1"
        />

        <button
          type="button"
          onClick={handleSend}
          disabled={!input.trim() || isLoading}
          className="flex h-8 w-8 sm:h-9 sm:w-9 shrink-0 items-center justify-center rounded-xl bg-gradient-to-tr from-sky-600 to-indigo-600 text-white shadow-sm transition-all hover:brightness-105 disabled:opacity-40 disabled:hover:brightness-100 active:scale-95"
          title="Send message"
        >
          <Send className="h-3.5 w-3.5 sm:h-4 sm:w-4" />
        </button>
      </div>

      <p className="mt-1.5 text-center text-[10px] text-slate-400 select-none hidden sm:block">
        Agentic Support AI Assistant. For official service records, refer to generated Support Ticket IDs.
      </p>
    </div>
  );
};
