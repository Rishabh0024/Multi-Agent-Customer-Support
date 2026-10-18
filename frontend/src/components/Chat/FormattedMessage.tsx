import React, { useState } from 'react';
import { Copy, Check, Ticket, ChevronRight } from 'lucide-react';

interface FormattedMessageProps {
  content: string;
}

export const FormattedMessage: React.FC<FormattedMessageProps> = ({ content }) => {
  const [copiedTicket, setCopiedTicket] = useState<string | null>(null);

  const handleCopyTicket = (ticketNum: string) => {
    navigator.clipboard.writeText(ticketNum);
    setCopiedTicket(ticketNum);
    setTimeout(() => setCopiedTicket(null), 2500);
  };

  // Helper to parse inline markdown (bold, italic, code)
  const renderInlineFormatted = (text: string) => {
    // Regex for: `code`, **bold**, *italic*
    const parts: React.ReactNode[] = [];
    let keyIdx = 0;

    // Pattern matches `code` OR **bold** OR *italic*
    const regex = /(`[^`]+`|\*\*[^*]+\*\*|\*[^*]+\*)/g;
    let lastIndex = 0;
    let match: RegExpExecArray | null;

    while ((match = regex.exec(text)) !== null) {
      // Text before match
      if (match.index > lastIndex) {
        parts.push(text.substring(lastIndex, match.index));
      }

      const matchText = match[0];
      if (matchText.startsWith('`') && matchText.endsWith('`')) {
        parts.push(
          <code
            key={keyIdx++}
            className="rounded-md bg-slate-100 px-1.5 py-0.5 font-mono text-[11px] sm:text-xs text-indigo-700 font-semibold border border-slate-200/80 shadow-2xs"
          >
            {matchText.slice(1, -1)}
          </code>
        );
      } else if (matchText.startsWith('**') && matchText.endsWith('**')) {
        parts.push(
          <strong key={keyIdx++} className="font-bold text-slate-900 tracking-tight">
            {matchText.slice(2, -2)}
          </strong>
        );
      } else if (matchText.startsWith('*') && matchText.endsWith('*')) {
        parts.push(
          <em key={keyIdx++} className="italic text-slate-700 font-serif">
            {matchText.slice(1, -1)}
          </em>
        );
      }

      lastIndex = match.index + matchText.length;
    }

    if (lastIndex < text.length) {
      parts.push(text.substring(lastIndex));
    }

    return parts.length > 0 ? parts : text;
  };

  // Parse lines into structured blocks
  const lines = content.split('\n');
  const renderedBlocks: React.ReactNode[] = [];

  let idx = 0;
  while (idx < lines.length) {
    const rawLine = lines[idx];
    const trimmed = rawLine.trim();

    // 1. Empty lines
    if (!trimmed) {
      renderedBlocks.push(<div key={`empty_${idx}`} className="h-2" />);
      idx++;
      continue;
    }

    // 2. Horizontal Divider (---)
    if (trimmed === '---' || trimmed === '***') {
      renderedBlocks.push(
        <div key={`hr_${idx}`} className="my-3 border-t border-slate-200/80" />
      );
      idx++;
      continue;
    }

    // 3. Special Support Ticket Card Detection
    // e.g. "📋 **Support Ticket Created: #TICK-12345**" or "📋 Support Ticket Created: #TICK-12345"
    const ticketMatch = trimmed.match(/(?:📋\s*)?\*?\*?Support Ticket Created:?\*?\*?\s*#?(TICK-\d+)/i) ||
                        trimmed.match(/Support Ticket.*?#?(TICK-\d+)/i);

    if (ticketMatch && ticketMatch[1]) {
      const ticketNum = ticketMatch[1];
      renderedBlocks.push(
        <div
          key={`ticket_${idx}`}
          className="my-3 rounded-2xl border border-indigo-200/90 bg-gradient-to-br from-indigo-50/90 via-sky-50/50 to-white p-3.5 sm:p-4 text-slate-800 shadow-sm shadow-indigo-500/5 transition-all"
        >
          <div className="flex items-center justify-between pb-2 border-b border-indigo-100/80">
            <div className="flex items-center gap-2">
              <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-indigo-600 text-white shadow-xs">
                <Ticket className="h-4 w-4" />
              </div>
              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider text-indigo-700 block">
                  Official Support Ticket
                </span>
                <span className="text-sm font-extrabold text-slate-900 font-mono">
                  #{ticketNum}
                </span>
              </div>
            </div>

            <button
              type="button"
              onClick={() => handleCopyTicket(ticketNum)}
              className="flex items-center gap-1 rounded-lg border border-indigo-200 bg-white px-2 py-1 text-[11px] font-semibold text-indigo-700 shadow-2xs hover:bg-indigo-50 transition-all active:scale-95"
            >
              {copiedTicket === ticketNum ? (
                <>
                  <Check className="h-3 w-3 text-emerald-600" />
                  <span className="text-emerald-700">Copied</span>
                </>
              ) : (
                <>
                  <Copy className="h-3 w-3 text-indigo-600" />
                  <span>Copy ID</span>
                </>
              )}
            </button>
          </div>

          <div className="mt-2.5 flex items-center justify-between text-[11px] text-slate-600">
            <span className="flex items-center gap-1.5 font-medium">
              <span className="flex h-2 w-2 relative">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-amber-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-amber-500"></span>
              </span>
              Priority: High / Escalated
            </span>
            <span className="text-[10px] font-mono bg-indigo-100/70 text-indigo-800 px-2 py-0.5 rounded-full font-semibold">
              Assigned to Leadership
            </span>
          </div>
        </div>
      );
      idx++;
      continue;
    }

    // 4. Headings (###, ##, #)
    if (trimmed.startsWith('#')) {
      const level = trimmed.match(/^#+/)?.[0].length || 1;
      const headingText = trimmed.replace(/^#+\s*/, '');

      if (level === 1) {
        renderedBlocks.push(
          <h2
            key={`h1_${idx}`}
            className="text-base sm:text-lg font-bold text-slate-900 mt-3 mb-1.5 tracking-tight border-b border-slate-100 pb-1"
          >
            {renderInlineFormatted(headingText)}
          </h2>
        );
      } else if (level === 2) {
        renderedBlocks.push(
          <h3
            key={`h2_${idx}`}
            className="text-sm sm:text-base font-bold text-slate-800 mt-2.5 mb-1 tracking-tight"
          >
            {renderInlineFormatted(headingText)}
          </h3>
        );
      } else {
        renderedBlocks.push(
          <h4
            key={`h3_${idx}`}
            className="text-xs sm:text-sm font-bold text-slate-700 mt-2 mb-1 flex items-center gap-1.5"
          >
            <ChevronRight className="h-3 w-3 text-sky-600 shrink-0" />
            <span>{renderInlineFormatted(headingText)}</span>
          </h4>
        );
      }
      idx++;
      continue;
    }

    // 5. Numbered Steps (e.g. "1. Items must be in original condition...")
    const numberedMatch = trimmed.match(/^(\d+)\.\s+(.*)/);
    if (numberedMatch) {
      const stepNum = numberedMatch[1];
      const stepContent = numberedMatch[2];
      renderedBlocks.push(
        <div key={`num_${idx}`} className="flex items-start gap-2.5 my-1.5 leading-relaxed">
          <span className="flex h-5 w-5 shrink-0 select-none items-center justify-center rounded-full bg-sky-100 text-sky-700 text-[10px] font-bold font-mono shadow-2xs mt-0.5">
            {stepNum}
          </span>
          <div className="flex-1 text-slate-800 text-xs sm:text-sm font-normal">
            {renderInlineFormatted(stepContent)}
          </div>
        </div>
      );
      idx++;
      continue;
    }

    // 6. Bullet Points (e.g. "- Items must..." or "* Items must...")
    const bulletMatch = trimmed.match(/^[-*•]\s+(.*)/);
    if (bulletMatch) {
      const bulletContent = bulletMatch[1];
      renderedBlocks.push(
        <div key={`bullet_${idx}`} className="flex items-start gap-2.5 my-1 leading-relaxed pl-1">
          <span className="h-1.5 w-1.5 shrink-0 rounded-full bg-sky-500 mt-2"></span>
          <div className="flex-1 text-slate-800 text-xs sm:text-sm font-normal">
            {renderInlineFormatted(bulletContent)}
          </div>
        </div>
      );
      idx++;
      continue;
    }

    // 7. Regular Text Paragraph
    renderedBlocks.push(
      <p key={`p_${idx}`} className="my-1 text-xs sm:text-sm leading-relaxed text-slate-800 font-normal">
        {renderInlineFormatted(trimmed)}
      </p>
    );
    idx++;
  }

  return <div className="space-y-0.5 text-slate-800 font-sans">{renderedBlocks}</div>;
};
