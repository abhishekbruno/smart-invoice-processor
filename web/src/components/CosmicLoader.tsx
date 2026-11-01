import React from 'react';

interface CosmicLoaderProps {
  size?: 'sm' | 'md' | 'lg' | number;
  label?: string;
  className?: string;
}

/**
 * Lightweight, reusable cosmic energy loading indicator inspired by the celestial sun.
 * Used for in-page asynchronous operations (Gemini responses, Gmail sync, exports, queries).
 */
export const CosmicLoader: React.FC<CosmicLoaderProps> = ({
  size = 'md',
  label,
  className = '',
}) => {
  const pixelSize =
    typeof size === 'number'
      ? size
      : size === 'sm'
      ? 20
      : size === 'lg'
      ? 48
      : 32;

  const strokeWidth = pixelSize <= 24 ? 2 : 2.5;

  return (
    <div
      role="status"
      aria-label={label || 'Loading…'}
      className={`inline-flex items-center gap-3 ${className}`}
    >
      <div
        className="relative flex items-center justify-center shrink-0"
        style={{ width: pixelSize, height: pixelSize }}
      >
        {/* Soft atmospheric center glow */}
        <div
          className="absolute inset-1 rounded-full bg-[#BBA8F1]/20 blur-sm animate-pulse"
          style={{ animationDuration: '2s' }}
        />

        {/* Counter-rotating faint outer energy trail */}
        <svg
          className="absolute inset-0 w-full h-full animate-spin"
          style={{ animationDuration: '3.6s', animationDirection: 'reverse' }}
          viewBox="0 0 40 40"
          fill="none"
        >
          <circle
            cx="20"
            cy="20"
            r="17"
            stroke="url(#cosmic-loader-trail)"
            strokeWidth={1}
            strokeDasharray="6 14"
            opacity={0.45}
          />
          <defs>
            <linearGradient id="cosmic-loader-trail" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#C084FC" />
              <stop offset="100%" stopColor="#3B82F6" stopOpacity="0" />
            </linearGradient>
          </defs>
        </svg>

        {/* Main rotating luminous lavender orbital ring */}
        <svg
          className="absolute inset-0 w-full h-full animate-spin"
          style={{ animationDuration: '1.2s' }}
          viewBox="0 0 40 40"
          fill="none"
        >
          <circle
            cx="20"
            cy="20"
            r="16"
            stroke="url(#cosmic-loader-grad)"
            strokeWidth={strokeWidth}
            strokeLinecap="round"
            strokeDasharray="72 28"
          />
          <defs>
            <linearGradient id="cosmic-loader-grad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#FFFFFF" />
              <stop offset="35%" stopColor="#E9D5FF" />
              <stop offset="70%" stopColor="#A855F7" />
              <stop offset="100%" stopColor="#4F46E5" stopOpacity="0.1" />
            </linearGradient>
          </defs>
        </svg>

        {/* Central radiant stellar core dot */}
        <div
          className="w-1.5 h-1.5 rounded-full bg-[#F5F3FF] shadow-[0_0_6px_#C084FC]"
          style={{ width: Math.max(3, pixelSize * 0.12), height: Math.max(3, pixelSize * 0.12) }}
        />
      </div>

      {label && (
        <span className="text-xs font-mono tracking-wide text-[#C4B5FD] select-none">
          {label}
        </span>
      )}
    </div>
  );
};

