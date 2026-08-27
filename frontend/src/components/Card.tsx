import React from 'react';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  onClick?: () => void;
}

export const Card: React.FC<CardProps> = ({ children, className = '', onClick }) => (
  <div
    onClick={onClick}
    className={`bg-white rounded-2xl shadow-sm border border-gray-100 p-6 ${onClick ? 'cursor-pointer' : ''} ${className}`}
  >
    {children}
  </div>
);
