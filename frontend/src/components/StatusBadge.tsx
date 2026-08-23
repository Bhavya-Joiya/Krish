import React from 'react';
import type { StatusType } from '../types';

interface StatusBadgeProps {
  status: StatusType;
  label?: string;
}

const config: Record<StatusType, { dot: string; text: string; label: string }> = {
  connected: { dot: 'bg-emerald-400', text: 'text-emerald-400', label: 'Connected' },
  offline:   { dot: 'bg-gray-600',    text: 'text-gray-500',    label: 'Offline'   },
  pending:   { dot: 'bg-amber-400',   text: 'text-amber-400',   label: 'Pending'   },
};

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, label }) => {
  const c = config[status];
  return (
    <span className={`inline-flex items-center gap-1.5 text-xs font-medium ${c.text}`}>
      <span className="relative flex h-2 w-2 flex-shrink-0">
        {status === 'connected' && (
          <span className={`animate-ping absolute inline-flex h-full w-full rounded-full ${c.dot} opacity-50`} />
        )}
        <span className={`relative inline-flex rounded-full h-2 w-2 ${c.dot}`} />
      </span>
      {label ?? c.label}
    </span>
  );
};
