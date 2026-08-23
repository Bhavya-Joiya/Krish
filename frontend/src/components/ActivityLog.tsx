import React, { useEffect, useRef, useState } from 'react';
import { motion } from 'framer-motion';
import { Microscope, Link, Bell, Mic } from 'lucide-react';
import type { LogEntry } from '../types';

const typeConfig: Record<LogEntry['type'], { dot: string; badge: string; icon: React.ReactNode }> = {
  diagnosis:  { dot: 'bg-emerald-400', badge: 'text-emerald-400 bg-emerald-400/8',   icon: <Microscope size={11} /> },
  connection: { dot: 'bg-blue-400',    badge: 'text-blue-400   bg-blue-400/8',         icon: <Link size={11} /> },
  alert:      { dot: 'bg-amber-400',   badge: 'text-amber-400  bg-amber-400/8',        icon: <Bell size={11} /> },
  voice:      { dot: 'bg-purple-400',  badge: 'text-purple-400 bg-purple-400/8',       icon: <Mic size={11} /> },
};

interface ActivityLogProps {
  entries: LogEntry[];
}

export const ActivityLog: React.FC<ActivityLogProps> = ({ entries }) => {
  const scrollRef = useRef<HTMLDivElement>(null);
  const [liveEntries, setLiveEntries] = useState<LogEntry[]>(entries);

  useEffect(() => {
    const newEntries: LogEntry[] = [
      { id: 'live-1', timestamp: 'just now', message: 'Photo diagnosis: Powdery Mildew detected — Pune region — 14s', type: 'diagnosis' },
      { id: 'live-2', timestamp: 'just now', message: 'SMS alert sent to 120 users — Nashik rainfall advisory',        type: 'alert'     },
      { id: 'live-3', timestamp: 'just now', message: 'Voice query processed — Hindi — 8s response time',               type: 'voice'     },
    ];
    let i = 0;
    const timer = setInterval(() => {
      if (i >= newEntries.length) return;
      setLiveEntries((prev) => [{ ...newEntries[i], id: `live-${Date.now()}` }, ...prev]);
      i++;
    }, 8000);
    return () => clearInterval(timer);
  }, []);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, amount: 0.15 }}
      transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
      className="glass rounded-2xl overflow-hidden"
    >
      {/* Header */}
      <div className="flex items-center justify-between px-5 py-4 border-b border-white/6">
        <div className="flex items-center gap-2.5">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse flex-shrink-0" />
          <p className="font-semibold text-white text-sm" style={{ fontFamily: 'Sora, sans-serif' }}>Activity Log</p>
          <span className="text-[10px] text-gray-600 bg-white/4 border border-white/8 rounded-full px-2 py-0.5">Live feed</span>
        </div>
        <div className="hidden sm:flex items-center gap-3">
          {(Object.entries(typeConfig) as [LogEntry['type'], typeof typeConfig[LogEntry['type']]][]).map(([t, c]) => (
            <span key={t} className="flex items-center gap-1 text-[10px] text-gray-600">
              <span className={`w-1.5 h-1.5 rounded-full ${c.dot}`} />
              {t.charAt(0).toUpperCase() + t.slice(1)}
            </span>
          ))}
        </div>
      </div>

      {/* Feed */}
      <div ref={scrollRef} className="overflow-y-auto max-h-80 divide-y divide-white/4">
        {liveEntries.map((entry, idx) => {
          const c = typeConfig[entry.type];
          return (
            <div
              key={entry.id}
              className={`flex items-start gap-3 px-5 py-3 hover:bg-white/3 transition-colors ${idx === 0 ? 'bg-emerald-400/4' : ''}`}
            >
              <div className={`mt-1.5 w-2 h-2 rounded-full flex-shrink-0 ${c.dot}`} />
              <div className="flex-1 min-w-0">
                <p
                  className="text-sm text-gray-300 leading-snug"
                  style={{ fontFamily: 'JetBrains Mono, monospace' }}
                >
                  {entry.message}
                </p>
                <div className="flex items-center gap-2 mt-0.5">
                  <span className="text-[10px] text-gray-700">{entry.timestamp}</span>
                  <span className={`inline-flex items-center gap-1 text-[10px] font-semibold px-1.5 py-0.5 rounded-full ${c.badge}`}>
                    {c.icon}
                    {entry.type.charAt(0).toUpperCase() + entry.type.slice(1)}
                  </span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </motion.div>
  );
};
