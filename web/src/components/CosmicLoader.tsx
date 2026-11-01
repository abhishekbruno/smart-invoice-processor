import React from 'react';

interface CosmicLoaderProps {
  size?: 'sm' | 'md' | 'lg' | number;
  label?: string;
  className?: string;
}

/**
 * CosmicLoader — Reusable Cosmic Energy Loading Indicator
 *
 * Designed for genuine asynchronous loading states (FastAPI queries, exports, syncs):
 * - Small rotating orbital ring.
 * - Soft glowing violet center.
 * - Delicate orbiting micro-particles.
 * - Minimal context-specific status text.
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
          {/* Orbiting micro-particle 1 */}
          <circle cx="20" cy="4" r="1.5" fill="#FFFFFF" opacity={0.9} />
          {/* Orbiting micro-particle 2 */}
          <circle cx="36" cy="20" r="1.2" fill="#E9D5FF" opacity={0.75} />
          <defs>
            <linearGradient id="cosmic-loader-grad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#FFFFFF" />
              <stop offset="35%" stopColor="#E9D5FF" />
              <stop offset="70%" stopColor="#A855F7" />
              <stop offset="100%" stopColor="#4F46E5" stopOpacity="0.1" />
            </linearGradient>
          </defs>
        </svg>

        {/* Central radiant violet energy core dot */}
        <div
          className="rounded-full bg-gradient-to-tr from-[#7C3AED] via-[#C084FC] to-[#F5EDFF] shadow-[0_0_8px_#C084FC]"
          style={{
            width: Math.max(4, pixelSize * 0.16),
            height: Math.max(4, pixelSize * 0.16),
          }}
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

/**
 * Reusable frosted skeleton placeholder for table rows
 */
export const CosmicTableSkeleton: React.FC<{ rows?: number; cols?: number }> = ({
  rows = 4,
  cols = 5,
}) => (
  <tbody className="divide-y divide-white/5 animate-pulse">
    {Array.from({ length: rows }).map((_, r) => (
      <tr key={r}>
        {Array.from({ length: cols }).map((_, c) => (
          <td key={c} className="px-6 py-4">
            <div
              className="h-3.5 rounded bg-white/[0.04] border border-white/[0.03]"
              style={{ width: `${45 + ((r * 17 + c * 29) % 45)}%` }}
            />
          </td>
        ))}
      </tr>
    ))}
  </tbody>
);

/**
 * Reusable frosted skeleton placeholder for cards
 */
export const CosmicCardSkeleton: React.FC<{ className?: string }> = ({ className = '' }) => (
  <div
    className={`p-6 rounded-2xl bg-white/[0.02] border border-white/5 animate-pulse flex flex-col justify-between ${className}`}
  >
    <div className="h-4 w-28 bg-white/[0.05] rounded mb-4" />
    <div className="h-8 w-36 bg-white/[0.07] rounded mb-2" />
    <div className="h-3 w-48 bg-white/[0.04] rounded" />
  </div>
);
