import React, { useState, useRef, useEffect } from 'react';
import {
  Send,
  Copy,
  Check,
  ChevronDown,
  ChevronUp,
  Sparkles,
  Receipt,
  Building2,
  Scale,
  ShieldCheck,
  Search,
  ExternalLink,
} from 'lucide-react';
import { Link } from 'react-router-dom';
import { sendChatMessage, fetchChatStatus } from '../services/api';
import { useQuery } from '@tanstack/react-query';
import type { ChatMessage } from '../types';
import { CosmicGlassPanel } from '../components/CosmicGlassPanel';
import { CosmicProcessingIndicator } from '../components/CosmicProcessingIndicator';
import { useEffects } from '../components/EffectsProvider';

interface SuggestionItem {
  icon: React.ElementType;
  text: string;
  category: string;
}

export const AskAI: React.FC = () => {
  const { reduced } = useEffects();
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 'welcome',
      sender: 'assistant',
      text: 'Hello. I can answer questions about your invoices using deterministic SQL financial totals, ECB currency rates, and Google Gemini 2.5 Flash document retrieval.',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    },
  ]);
  const [inputQuery, setInputQuery] = useState('');
  const [isSending, setIsSending] = useState(false);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [expandedCitations, setExpandedCitations] = useState<Record<string, boolean>>({});
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const { data: chatStatus } = useQuery({
    queryKey: ['chat-status'],
    queryFn: fetchChatStatus,
    staleTime: 30000,
  });

  const suggestions: SuggestionItem[] = [
    { icon: Receipt, category: 'Totals', text: 'What did we spend in total?' },
    { icon: Building2, category: 'Vendor', text: 'What did we spend on Amazon Web Services?' },
    { icon: Scale, category: 'Comparison', text: 'Compare AWS and Google Cloud spending' },
    { icon: Sparkles, category: 'Top Spend', text: 'Which vendor charged the highest amount?' },
    { icon: ShieldCheck, category: 'Duplicates', text: 'Are there any duplicate invoices flagged?' },
    { icon: Search, category: 'Deep Dive', text: 'What services were billed on invoice INV-AWS-2024-8192?' },
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: reduced ? 'instant' : 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isSending]);

  const handleSend = async (queryToSend?: string) => {
    const q = (queryToSend || inputQuery).trim();
    if (!q || isSending) return;

    setInputQuery('');
    const userMsg: ChatMessage = {
      id: `user-${Date.now()}`,
      sender: 'user',
      text: q,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userMsg]);
    setIsSending(true);

    try {
      const res = await sendChatMessage(q);
      const assistantMsg: ChatMessage = {
        id: `assistant-${Date.now()}`,
        sender: 'assistant',
        text: res.answer,
        query_type: res.query_type,
        citations: res.citations,
        verified_totals: res.verified_totals,
        is_fallback: res.is_fallback,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err: any) {
      const errorMsg: ChatMessage = {
        id: `err-${Date.now()}`,
        sender: 'assistant',
        text: `Error processing question: ${err.response?.data?.detail || err.message || 'Please verify API connection.'}`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsSending(false);
    }
  };

  const handleCopy = (id: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 1800);
  };

  const toggleCitations = (msgId: string) => {
    setExpandedCitations((prev) => ({ ...prev, [msgId]: !prev[msgId] }));
  };

  return (
    <div className="flex flex-col h-[calc(100vh-8.5rem)] max-w-4xl mx-auto animate-fade-in space-y-4">
      {/* Top Status Bar with Glass Glow */}
      <CosmicGlassPanel variant="subtle" className="px-5 py-3 rounded-2xl flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-[#7C3AED]/40 to-[#4C1D95]/60 border border-[#A78BFA]/40 flex items-center justify-center text-[#BBA8F1] shadow-[0_0_12px_rgba(139,92,246,0.25)]">
            <Sparkles size={14} />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-sm font-display font-medium text-[#F1EDF8] tracking-tight">
                Conversational RAG Intelligence
              </span>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-[#BBA8F1]/10 text-[#C4B5FD] border border-[#BBA8F1]/20">
                Gemini 2.5 Flash
              </span>
            </div>
            <p className="text-[11px] text-[#9A91AE] hidden sm:block">
              Deterministic SQL verification · Vector semantic retrieval
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-[11px] text-[#9892AB] font-mono">
            CHROMA: <strong className="text-[#D8CDF0]">{chatStatus?.total_indexed_chunks || 0}</strong> CHUNKS
          </span>
        </div>
      </CosmicGlassPanel>

      {/* Suggested question chips with icons */}
      <div className="py-1 flex items-center gap-2 overflow-x-auto no-scrollbar">
        {suggestions.map((s, idx) => {
          const Icon = s.icon;
          return (
            <button
              key={idx}
              onClick={() => handleSend(s.text)}
              disabled={isSending}
              className="inline-flex items-center gap-2 text-xs px-3.5 py-1.5 rounded-full bg-white/[0.03] border border-white/8 text-[#B8B2C8] hover:text-[#F1EDF8] hover:border-[#BBA8F1]/40 hover:bg-[#BBA8F1]/10 whitespace-nowrap transition cursor-pointer font-sans"
            >
              <Icon size={12} className="text-[#A78BFA]" />
              <span>{s.text}</span>
            </button>
          );
        })}
      </div>

      {/* Message Chat Feed */}
      <div className="flex-1 overflow-y-auto py-2 space-y-5 pr-2">
        {messages.map((m) => {
          const isUser = m.sender === 'user';
          const citationsOpen = !!expandedCitations[m.id];

          return (
            <div
              key={m.id}
              className={`flex gap-3 ${isUser ? 'justify-end' : 'justify-start'}`}
            >
              {!isUser && (
                <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-[#7C3AED]/30 to-[#3B1968]/50 border border-[#A78BFA]/30 flex items-center justify-center shrink-0 text-[#BBA8F1] shadow-[0_0_12px_rgba(139,92,246,0.2)] mt-1">
                  <Sparkles size={14} />
                </div>
              )}

              <div
                className={`max-w-2xl text-xs sm:text-sm leading-relaxed ${
                  isUser
                    ? 'p-4 sm:p-5 rounded-2xl rounded-tr-xs bg-gradient-to-br from-[#311d54]/90 to-[#1e1333]/95 border border-[#A78BFA]/30 text-[#F5F2FC] shadow-[0_8px_24px_rgba(139,92,246,0.18)]'
                    : 'p-5 sm:p-6 rounded-2xl rounded-tl-xs bg-[#0E0A17]/90 border border-white/10 text-[#F1EDF8] space-y-3.5 shadow-[0_12px_36px_rgba(0,0,0,0.45)] backdrop-blur-xl'
                }`}
              >
                {/* Assistant Message Header */}
                {!isUser && (
                  <div className="flex items-center justify-between pb-2.5 border-b border-white/8">
                    <span className="text-[10px] font-mono uppercase px-2.5 py-0.5 rounded-full bg-white/[0.04] text-[#C4B5FD] border border-white/10">
                      {m.query_type === 'SQL'
                        ? '// DETERMINISTIC SQL'
                        : m.query_type === 'RAG'
                        ? '// VECTOR RETRIEVAL'
                        : '// HYBRID SYNTHESIS'}
                    </span>
                    <button
                      onClick={() => handleCopy(m.id, m.text)}
                      className="text-[#9892AB] hover:text-[#F1EDF8] transition cursor-pointer p-1 rounded-md hover:bg-white/5"
                      title="Copy response"
                    >
                      {copiedId === m.id ? (
                        <Check className="w-3.5 h-3.5 text-emerald-400" />
                      ) : (
                        <Copy className="w-3.5 h-3.5" />
                      )}
                    </button>
                  </div>
                )}

                {/* Content body */}
                <div className="whitespace-pre-wrap font-sans font-light leading-relaxed text-[#F1EDF8]">
                  {m.text}
                </div>

                {/* Verified Totals Badge if available */}
                {!isUser && m.verified_totals && Object.keys(m.verified_totals).length > 0 && (
                  <div className="p-3 rounded-xl bg-white/[0.02] border border-[#BBA8F1]/15 text-xs font-mono space-y-1">
                    <span className="text-[10px] uppercase text-[#A78BFA] tracking-wider block">
                      // Verified Deterministic Data
                    </span>
                    <div className="grid grid-cols-2 gap-2 pt-1 text-[11px]">
                      {Object.entries(m.verified_totals).map(([k, v]) => (
                        <div key={k} className="flex justify-between border-b border-white/4 pb-1">
                          <span className="text-[#9892AB]">{k}:</span>
                          <span className="text-[#F1EDF8] font-medium">{String(v)}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Grounded Audit Citations */}
                {!isUser && m.citations && m.citations.length > 0 && (
                  <div className="pt-2.5 border-t border-white/8">
                    <button
                      onClick={() => toggleCitations(m.id)}
                      className="text-[11px] font-mono text-[#BBA8F1] hover:text-[#F1EDF8] flex items-center gap-1.5 transition cursor-pointer"
                    >
                      <span>// {m.citations.length} GROUNDED AUDIT CITATIONS</span>
                      {citationsOpen ? (
                        <ChevronUp className="w-3.5 h-3.5 text-[#BBA8F1]" />
                      ) : (
                        <ChevronDown className="w-3.5 h-3.5 text-[#8879A7]" />
                      )}
                    </button>

                    {citationsOpen && (
                      <div className="mt-2.5 space-y-2 animate-fade-in">
                        {m.citations.map((c, i) => (
                          <div
                            key={i}
                            className="p-3 rounded-xl bg-white/[0.02] border border-white/6 text-[11px] space-y-1.5 font-mono"
                          >
                            <div className="flex items-center justify-between text-[#F1EDF8] font-medium">
                              <span className="flex items-center gap-1.5">
                                <Receipt size={12} className="text-[#A78BFA]" />
                                {c.vendor || c.invoice_number || c.filename || 'Invoice Document'}
                              </span>
                              <div className="flex items-center gap-2">
                                {c.page_number && (
                                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-white/5 text-[#9892AB]">
                                    Page {c.page_number}
                                  </span>
                                )}
                                {(c.invoice_number || c.vendor) && (
                                  <Link
                                    to={`/invoices?search=${encodeURIComponent(c.invoice_number || c.vendor || '')}`}
                                    className="text-[10px] text-[#BBA8F1] hover:underline inline-flex items-center gap-0.5"
                                  >
                                    View <ExternalLink size={10} />
                                  </Link>
                                )}
                              </div>
                            </div>
                            {c.snippet && (
                              <p className="text-[10px] text-[#B8B2C8] font-sans italic bg-black/20 p-2 rounded-lg border-l-2 border-[#A78BFA]/50">
                                "{c.snippet}"
                              </p>
                            )}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}

                <div className="text-[10px] text-[#9892AB] font-mono text-right">{m.timestamp}</div>
              </div>

              {isUser && (
                <div className="w-8 h-8 rounded-xl bg-white/[0.06] border border-white/10 flex items-center justify-center shrink-0 text-[#B8B2C8] font-mono text-xs font-semibold mt-1">
                  U
                </div>
              )}
            </div>
          );
        })}

        {isSending && (
          <div className="flex gap-3 items-center py-2">
            <CosmicProcessingIndicator />
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Floating Input Bar in Cosmic Violet Glass */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleSend();
        }}
        className="pt-2 flex items-center gap-2.5"
      >
        <div className="relative flex-1">
          <input
            type="text"
            value={inputQuery}
            onChange={(e) => setInputQuery(e.target.value)}
            placeholder="Ask a question (e.g. 'Compare AWS and Google Cloud expenses')..."
            disabled={isSending}
            className="w-full px-5 py-3.5 bg-[#0F0B18]/90 border border-white/10 rounded-2xl text-xs sm:text-sm text-[#F1EDF8] placeholder-[#9892AB] focus:outline-none focus:border-[#BBA8F1]/60 focus:ring-1 focus:ring-[#BBA8F1]/30 transition font-sans font-light shadow-[inset_0_1px_0_rgba(255,255,255,0.06)]"
          />
        </div>
        <button
          type="submit"
          disabled={!inputQuery.trim() || isSending}
          className="aovix-gradient-btn px-6 py-3.5 rounded-2xl text-xs font-semibold tracking-wide transition flex items-center gap-2 disabled:opacity-40 cursor-pointer shadow-[0_4px_16px_rgba(124,58,237,0.3)] hover:shadow-[0_6px_20px_rgba(124,58,237,0.4)]"
        >
          <Send className="w-3.5 h-3.5" />
          <span className="hidden sm:inline">Ask</span>
        </button>
      </form>
    </div>
  );
};
