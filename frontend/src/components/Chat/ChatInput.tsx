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
  'I placed an order 30 minutes ago, can I cancel it?',
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
    <div className="border-t border-slate-200 bg-white p-4">
      {/* Quick Prompts */}
      <div className="mb-3 flex items-center gap-1.5 overflow-x-auto pb-1 text-xs no-scrollbar">
        <span className="flex items-center gap-1 font-medium text-slate-400 shrink-0">
          <Sparkles className="h-3.5 w-3.5 text-amber-500" />
          Try:
        </span>
        {SAMPLE_PROMPTS.map((prompt, idx) => (
          <button
            key={idx}
            disabled={isLoading}
            onClick={() => onSendMessage(prompt)}
            className="shrink-0 rounded-full bg-slate-100 px-3 py-1 text-slate-600 transition-colors hover:bg-sky-50 hover:text-sky-700 disabled:opacity-50"
          >
            {prompt}
          </button>
        ))}
      </div>

      {/* Input Form */}
      <div className="flex items-center gap-2 rounded-xl border border-slate-300 bg-slate-50 px-3 py-2 focus-within:border-sky-500 focus-within:bg-white focus-within:ring-2 focus-within:ring-sky-500/20 transition-all shadow-inner">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask a question or explain your problem..."
          disabled={isLoading}
          className="w-full bg-transparent text-sm text-slate-800 placeholder-slate-400 focus:outline-none disabled:opacity-50"
        />

        <button
          onClick={handleSend}
          disabled={!input.trim() || isLoading}
          className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-sky-600 text-white shadow-sm transition-all hover:bg-sky-700 disabled:opacity-40 disabled:hover:bg-sky-600"
        >
          <Send className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
};
