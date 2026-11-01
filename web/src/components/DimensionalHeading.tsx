import React from 'react';

export interface DimensionalHeadingProps extends React.HTMLAttributes<HTMLHeadingElement> {
  children: React.ReactNode;
  as?: 'h1' | 'h2' | 'h3';
  size?: 'hero' | 'section' | 'title';
  className?: string;
}

export const DimensionalHeading: React.FC<DimensionalHeadingProps> = ({
  children,
  as: Component = 'h1',
  size = 'hero',
  className = '',
  ...props
}) => {
  const sizeClasses = {
    hero: 'text-4xl sm:text-5xl lg:text-6xl font-light tracking-tight',
    section: 'text-2xl sm:text-3xl lg:text-4xl font-normal tracking-tight',
    title: 'text-xl sm:text-2xl font-medium tracking-tight',
  }[size];

  return (
    <Component
      className={`dimensional-heading select-none ${sizeClasses} ${className}`}
      {...props}
    >
      {children}
    </Component>
  );
};

