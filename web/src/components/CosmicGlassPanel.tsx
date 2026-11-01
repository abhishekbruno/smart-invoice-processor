import React from 'react';

export interface CosmicGlassPanelProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  variant?: 'default' | 'subtle' | 'elevated';
  className?: string;
  as?: React.ElementType;
}

export const CosmicGlassPanel: React.FC<CosmicGlassPanelProps> = ({
  children,
  variant = 'default',
  className = '',
  as: Component = 'div',
  ...props
}) => {
  const baseClass =
    variant === 'subtle'
      ? 'cosmic-glass-subtle'
      : 'cosmic-glass';

  return (
    <Component
      className={`${baseClass} ${className}`}
      {...props}
    >
      {children}
    </Component>
  );
};

