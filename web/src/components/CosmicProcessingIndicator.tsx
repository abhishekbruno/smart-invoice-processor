import React, { useState, useEffect } from 'react';
import { Sparkles } from 'lucide-react';
import { useEffects } from './EffectsProvider';

interface CosmicProcessingIndicatorProps {
  label?: string;
  steps?: string[];
  className?: string;
}

export const CosmicProcessingIndicator: React.FC<CosmicProcessingIndicatorProps> = ({
  label,
  steps = [
    'Analyzing document semantics...',
    'Querying ChromaDB vector index...',
    'Synthesizing audit-verified response...',
  ],
  className = '',
}) => {
  const { reduced } = useEffects();
  const [currentStepIndex, setCurrentStepIndex] = useState(0);

  useEffect(() => {
    if (reduced || !steps.length) return;
    const interval = setInterval(() => {
      setCurrentStepIndex((prev) => (prev + 1) % steps.length);
    }, 2400);
    return () => clearInterval(interval);
  }, [reduced, steps]);

  const activeText = label || steps[currentStepIndex] || 'Processing with Gemini...';

  return (
    <div
      role="status"
      aria-live="polite"
      className={`inline-flex items-center gap-3 px-4 py-2.5 rounded-2xl bg-[#0D0914]/80 border border-[#8B5CF6]/25 shadow-[0_4px_20px_rgba(0,0,0,0.4)] backdrop-blur-md ${className}`}
    >
      {/* 3 pulsing cosmic particles */}
      <div className="flex items-center gap-1.5 px-1 shrink-0" aria-hidden="true">
        <span
          className="w-2 h-2 rounded-full bg-[#BBA8F1] cosmic-particle-dot"
          style={{ animationDelay: '0ms' }}
        />
        <span
          className="w-2 h-2 rounded-full bg-[#A78BFA] cosmic-particle-dot"
          style={{ animationDelay: '200ms' }}
        />
        <span
          className="w-2 h-2 rounded-full bg-[#C4B5FD] cosmic-particle-dot"
          style={{ animationDelay: '400ms' }}
        />
      </div>

      <div className="flex items-center gap-2 min-w-0">
        <Sparkles size={13} className="text-[#BBA8F1]/80 shrink-0" />
        <span className="text-xs font-mono text-[#D8CDF0] tracking-wide truncate transition-opacity duration-300">
          {activeText}
        </span>
      </div>
    </div>
  );
};

