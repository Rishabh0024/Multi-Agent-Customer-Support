import React from 'react';
import { Smile, Meh, Frown, AlertTriangle } from 'lucide-react';

interface SentimentBadgeProps {
  label?: string;
  score?: number;
}

export const SentimentBadge: React.FC<SentimentBadgeProps> = ({ label = 'neutral', score = 0.5 }) => {
  const normLabel = label.toLowerCase();

  let config = {
    bg: 'bg-slate-100',
    text: 'text-slate-700',
    border: 'border-slate-200',
    icon: <Meh className="h-3.5 w-3.5 text-slate-500" />,
    name: 'Neutral',
  };

  if (normLabel === 'positive') {
    config = {
      bg: 'bg-emerald-50',
      text: 'text-emerald-700',
      border: 'border-emerald-200',
      icon: <Smile className="h-3.5 w-3.5 text-emerald-600" />,
      name: 'Satisfied',
    };
  } else if (normLabel === 'frustrated') {
    config = {
      bg: 'bg-amber-50',
      text: 'text-amber-700',
      border: 'border-amber-200',
      icon: <Frown className="h-3.5 w-3.5 text-amber-600" />,
      name: 'Frustrated',
    };
  } else if (normLabel === 'angry') {
    config = {
      bg: 'bg-rose-50',
      text: 'text-rose-700',
      border: 'border-rose-200',
      icon: <AlertTriangle className="h-3.5 w-3.5 text-rose-600" />,
      name: 'Critical / Angry',
    };
  }

  return (
    <div
      className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-xs font-medium ${config.bg} ${config.text} ${config.border}`}
      title={`Sentiment Score: ${score.toFixed(2)}`}
    >
      {config.icon}
      <span>{config.name}</span>
      <span className="opacity-60 text-[10px]">({score.toFixed(2)})</span>
    </div>
  );
};
