import React, { useRef } from 'react';

export interface CosmicGlassPanelProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  variant?: 'default' | 'subtle' | 'elevated';
  className?: string;
  as?: React.ElementType;
  interactive?: boolean;
}

export const CosmicGlassPanel: React.FC<CosmicGlassPanelProps> = ({
  children,
  variant = 'default',
  className = '',
  as: Component = 'div',
  interactive = false,
  ...props
}) => {
  const panelRef = useRef<HTMLDivElement | null>(null);

  const baseClass =
    variant === 'subtle'
      ? 'cosmic-glass-subtle'
      : 'cosmic-glass';

  const interactiveClass = interactive ? 'cosmic-glass-interactive' : '';

  const handlePointerMove = (e: React.PointerEvent<HTMLDivElement>) => {
    if (!interactive || e.pointerType === 'touch') return;
    const target = e.currentTarget;
    const rect = target.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    target.style.setProperty('--mouse-x', `${x}px`);
    target.style.setProperty('--mouse-y', `${y}px`);
    target.style.setProperty('--card-opacity', '1');
    props.onPointerMove?.(e);
  };

  const handlePointerLeave = (e: React.PointerEvent<HTMLDivElement>) => {
    if (!interactive) return;
    e.currentTarget.style.setProperty('--card-opacity', '0');
    props.onPointerLeave?.(e);
  };

  return (
    <Component
      ref={panelRef}
      className={`${baseClass} ${interactiveClass} ${className}`}
      onPointerMove={interactive ? handlePointerMove : props.onPointerMove}
      onPointerLeave={interactive ? handlePointerLeave : props.onPointerLeave}
      {...props}
    >
      {interactive && (
        <>
          <div className="cosmic-glass-glow" aria-hidden="true" />
          <div className="cosmic-glass-border-spotlight" aria-hidden="true" />
        </>
      )}
      {children}
    </Component>
  );
};
