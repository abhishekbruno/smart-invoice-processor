import React from 'react';

interface StatusBadgeProps {
  status: string;
  size?: 'sm' | 'md';
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, size = 'sm' }) => {
  const norm = status?.toLowerCase() || 'unknown';

  let bg = 'bg-[#12101B] text-[#B7B7B9] border-[#1A1625]';
  let dot = 'bg-[#72707D]';
  let label = status;

  if (norm === 'verified') {
    bg = 'bg-emerald-950/20 text-emerald-300 border-emerald-800/30';
    dot = 'bg-emerald-400 shadow-[0_0_6px_rgba(52,211,153,0.5)]';
    label = 'Verified';
  } else if (norm === 'processed') {
    bg = 'bg-[#4B37B2]/15 text-[#BAA7D1] border-[#8879A7]/25';
    dot = 'bg-[#BAA7D1] shadow-[0_0_6px_rgba(186,167,209,0.5)]';
    label = 'Processed';
  } else if (norm === 'needs_review') {
    bg = 'bg-amber-950/20 text-amber-200 border-amber-800/30';
    dot = 'bg-amber-400 shadow-[0_0_6px_rgba(251,191,36,0.5)]';
    label = 'Needs Review';
  } else if (norm === 'suspected_duplicate' || norm === 'duplicate') {
    bg = 'bg-[#923F53]/20 text-rose-300 border-[#923F53]/40';
    dot = 'bg-rose-400 shadow-[0_0_6px_rgba(244,63,94,0.5)]';
    label = 'Duplicate';
  } else if (norm === 'online' || norm === 'healthy' || norm === 'success' || norm === 'active') {
    bg = 'bg-emerald-950/20 text-emerald-300 border-emerald-800/30';
    dot = 'bg-emerald-400 shadow-[0_0_6px_rgba(52,211,153,0.5)]';
    label = norm.toUpperCase();
  } else if (norm === 'offline' || norm === 'failed' || norm === 'error' || norm === 'idle') {
    bg = 'bg-[#12101B] text-[#B7B7B9] border-[#1A1625]';
    dot = 'bg-[#72707D]';
    label = norm.toUpperCase();
  }

  const px = size === 'sm' ? 'px-2.5 py-0.5 text-[11px]' : 'px-3 py-1 text-xs';

  return (
    <span className={`inline-flex items-center gap-1.5 font-medium rounded-full border backdrop-blur-xs ${bg} ${px} select-none`}>
      <span className={`w-1.5 h-1.5 rounded-full ${dot} shrink-0`} />
      <span>{label}</span>
    </span>
  );
};
