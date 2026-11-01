import React from 'react';
import type { LucideIcon } from 'lucide-react';
import { CosmicGlassPanel } from './CosmicGlassPanel';
import { AnimatedMetric } from './AnimatedMetric';

interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: LucideIcon;
  trend?: string;
  badge?: string;
  format?: (value: number) => string;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  subtitle,
  icon: Icon,
  trend,
  badge,
  format,
}) => {
  return (
    <CosmicGlassPanel className="metric-card p-5.5 h-full flex flex-col justify-between group">
      <div className="flex items-center justify-between">
        <span className="text-[11px] font-sans font-medium tracking-wider uppercase text-[#B8B2C8]">
          {title}
        </span>
        {badge ? (
          <span className="cosmic-glass-pill text-[10px] py-0.5 px-2.5">
            {badge}
          </span>
        ) : Icon ? (
          <div className="w-7 h-7 rounded-lg cosmic-glass-control flex items-center justify-center">
            <Icon className="w-3.5 h-3.5 text-[#BBA8F1]" />
          </div>
        ) : null}
      </div>

      <div className="mt-4">
        <div className="text-2xl sm:text-[1.75rem] font-display font-semibold tracking-tight text-[#F1EDF8] tabular-nums font-mono">
          {typeof value === 'number' ? <AnimatedMetric value={value} format={format ?? integerFormat} /> : value}
        </div>
      </div>

      {(subtitle || trend) && (
        <div className="mt-3.5 pt-2.5 border-t border-white/6 flex items-center justify-between text-[11px] text-[#9892AB] font-sans">
          {subtitle && <span className="truncate">{subtitle}</span>}
          {trend && <span className="text-[#BBA8F1] font-medium shrink-0 ml-2 font-mono">{trend}</span>}
        </div>
      )}
    </CosmicGlassPanel>
  );
};

const integerFormat = (value: number) => Math.round(value).toLocaleString('en-IN');
