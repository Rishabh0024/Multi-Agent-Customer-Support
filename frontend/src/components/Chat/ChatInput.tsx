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
    <div className="border-t border-slate-200 bg-white px-3 py-2.5 sm:p-4">
      {/* Quick Prompts */}
      <div className="mb-2 flex items-center gap-1.5 overflow-x-auto pb-1 text-xs no-scrollbar scroll-smooth">
        <span className="flex items-center gap-1 font-semibold text-slate-400 shrink-0 text-[11px]">
          <Sparkles className="h-3.5 w-3.5 text-amber-500 shrink-0" />
          <span>Suggestions:</span>
        </span>
        {SAMPLE_PROMPTS.map((prompt, idx) => (
          <button
            key={idx}
            disabled={isLoading}
            onClick={() => onSendMessage(prompt)}
            className="shrink-0 rounded-full bg-slate-100 hover:bg-sky-50 hover:text-sky-700 px-2.5 py-1 text-[11px] sm:text-xs text-slate-600 font-medium transition-colors border border-slate-200/60 active:scale-95 disabled:opacity-50"
          >
            {prompt}
          </button>
        ))}
      </div>

      {/* Input Form */}
      <div className="flex items-center gap-2 rounded-xl border border-slate-300 bg-slate-50 px-3 py-1.5 sm:py-2 focus-within:border-sky-500 focus-within:bg-white focus-within:ring-2 focus-within:ring-sky-500/20 transition-all shadow-inner">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask a question or explain your problem..."
          disabled={isLoading}
          className="w-full bg-transparent text-xs sm:text-sm text-slate-800 placeholder-slate-400 focus:outline-none disabled:opacity-50 py-1"
        />

        <button
          onClick={handleSend}
          disabled={!input.trim() || isLoading}
          className="flex h-8 w-8 sm:h-9 sm:w-9 shrink-0 items-center justify-center rounded-lg bg-sky-600 text-white shadow-sm transition-all hover:bg-sky-700 disabled:opacity-40 disabled:hover:bg-sky-600 active:scale-95"
        >
          <Send className="h-3.5 w-3.5 sm:h-4 sm:w-4" />
        </button>
      </div>
    </div>
  );
};
