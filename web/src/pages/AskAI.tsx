import React, { useState, useRef, useEffect } from 'react';
import {
  Send,
  Copy,
  Check,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';
import { sendChatMessage, fetchChatStatus } from '../services/api';
import { useQuery } from '@tanstack/react-query';
import type { ChatMessage } from '../types';
import { CosmicGlassPanel } from '../components/CosmicGlassPanel';
import { CosmicLoader } from '../components/CosmicLoader';
import { useEffects } from '../components/EffectsProvider';

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

  const suggestions = [
    'What did we spend in total?',
    'What did we spend on Amazon Web Services?',
    'Compare AWS and Google Cloud spending',
    'Which vendor charged the highest amount?',
    'What services were billed on invoice INV-AWS-2024-8192?',
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
      {/* Quiet Top Status Bar */}
      <CosmicGlassPanel variant="subtle" className="px-5 py-3 rounded-2xl flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="w-6 h-6 rounded-lg cosmic-glass-control flex items-center justify-center text-[10px] font-mono text-[#BBA8F1] font-semibold">
            AI
          </div>
          <span className="text-sm font-display font-semibold text-[#F1EDF8] tracking-tight">Intelligence Assistant</span>
          <span className="text-[10px] font-mono px-2.5 py-0.5 rounded-full cosmic-glass-pill">
            Gemini 2.5 Flash
          </span>
        </div>
        <span className="text-[11px] text-[#9892AB] font-mono">
          CHROMA : <strong className="text-[#B8B2C8]">{chatStatus?.total_indexed_chunks || 0}</strong> CHUNKS
        </span>
      </CosmicGlassPanel>

      {/* Suggested chips */}
      <div className="py-1 flex items-center gap-2 overflow-x-auto no-scrollbar">
        {suggestions.map((s, idx) => (
          <button
            key={idx}
            onClick={() => handleSend(s)}
            disabled={isSending}
            className="text-xs px-3.5 py-1.5 rounded-full cosmic-glass-control text-[#B8B2C8] hover:text-[#F1EDF8] hover:border-[#BBA8F1]/40 whitespace-nowrap transition cursor-pointer font-sans font-light"
          >
            {s}
          </button>
        ))}
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
                <div className="w-7 h-7 rounded-lg cosmic-glass-control flex items-center justify-center shrink-0 text-[#BBA8F1] font-mono text-[10px] font-semibold mt-1">
                  AI
                </div>
              )}

              <div
                className={`max-w-2xl rounded-3xl p-5 text-xs sm:text-sm leading-relaxed ${
                  isUser
                    ? 'aovix-gradient-btn text-white rounded-br-xs shadow-[0_8px_20px_rgba(75,55,178,0.3)]'
                    : 'cosmic-glass text-[#F1EDF8] rounded-bl-xs space-y-3.5 shadow-[0_10px_30px_rgba(0,0,0,0.4)]'
                }`}
              >
                {/* Assistant Message Header */}
                {!isUser && m.query_type && (
                  <div className="flex items-center justify-between pb-2.5 border-b border-white/6">
                    <span className="text-[10px] font-mono uppercase px-2.5 py-0.5 rounded-full cosmic-glass-pill">
                      {m.query_type === 'SQL' ? '// DETERMINISTIC SQL' : m.query_type === 'RAG' ? '// VECTOR RETRIEVAL' : '// HYBRID SYNTHESIS'}
                    </span>
                    <button
                      onClick={() => handleCopy(m.id, m.text)}
                      className="text-[#9892AB] hover:text-[#F1EDF8] transition cursor-pointer"
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
                <div className="whitespace-pre-wrap font-sans font-light leading-relaxed">{m.text}</div>

                {/* Collapsible Citations */}
                {!isUser && m.citations && m.citations.length > 0 && (
                  <div className="pt-2.5 border-t border-white/6">
                    <button
                      onClick={() => toggleCitations(m.id)}
                      className="text-[11px] font-mono text-[#BBA8F1] hover:text-[#F1EDF8] flex items-center gap-1.5 transition cursor-pointer"
                    >
                      <span>// {m.citations.length} GROUNDED AUDIT CITATIONS</span>
                      {citationsOpen ? <ChevronUp className="w-3.5 h-3.5 text-[#BBA8F1]" /> : <ChevronDown className="w-3.5 h-3.5 text-[#8879A7]" />}
                    </button>

                    {citationsOpen && (
                      <div className="mt-2.5 space-y-2 animate-fade-in">
                        {m.citations.map((c, i) => (
                          <div
                            key={i}
                            className="p-3 rounded-2xl cosmic-glass-subtle text-[11px] space-y-1 font-mono"
                          >
                            <div className="flex items-center justify-between text-[#F1EDF8] font-medium">
                              <span>{c.vendor || c.filename}</span>
                              {c.page_number && <span className="text-[#9892AB]">p. {c.page_number}</span>}
                            </div>
                            {c.snippet && (
                              <p className="text-[10px] text-[#B8B2C8] font-sans italic">"{c.snippet}"</p>
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
                <div className="w-7 h-7 rounded-lg cosmic-glass-control flex items-center justify-center shrink-0 text-[#B8B2C8] font-mono text-[10px] font-semibold mt-1">
                  U
                </div>
              )}
            </div>
          );
        })}

        {isSending && (
          <div className="flex gap-3 items-center py-2">
            <CosmicLoader size="sm" label="// GENERATING GROUNDED AUDIT REASONING WITH GEMINI..." />
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Sleek Floating Input Bar in Cosmic Violet Glass */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleSend();
        }}
        className="pt-2 flex items-center gap-2.5"
      >
        <input
          type="text"
          value={inputQuery}
          onChange={(e) => setInputQuery(e.target.value)}
          placeholder="Ask a question (e.g. 'Compare AWS and Google Cloud expenses')..."
          disabled={isSending}
          className="flex-1 px-5 py-3 cosmic-glass-control rounded-full text-xs sm:text-sm text-[#F1EDF8] placeholder-[#9892AB] focus:outline-none focus:border-[#BBA8F1]/60 transition font-sans font-light"
        />
        <button
          type="submit"
          disabled={!inputQuery.trim() || isSending}
          className="aovix-gradient-btn px-6 py-3 rounded-full text-xs font-semibold tracking-wide transition flex items-center gap-2 disabled:opacity-40 cursor-pointer shadow-[0_4px_15px_rgba(75,55,178,0.3)]"
        >
          <Send className="w-3.5 h-3.5" />
          <span className="hidden sm:inline">Ask</span>
        </button>
      </form>
    </div>
  );
};
