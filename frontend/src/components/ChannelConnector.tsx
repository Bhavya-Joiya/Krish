import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { StatusBadge } from './StatusBadge';
import type { ChannelData } from '../types';
import { Send, Smartphone, Globe, ChevronDown } from 'lucide-react';

const ChannelIcon: Record<string, React.ReactNode> = {
  telegram: <Send size={20} strokeWidth={1.8} />,
  sms: <Smartphone size={20} strokeWidth={1.8} />,
  fallback: <Globe size={20} strokeWidth={1.8} />,
};

const floatY = [
  [0, -4, 0, 4, 0],
  [0, 3, 0, -3, 0],
  [0, -3, 0, 3, 0],
];

interface ChannelConnectorProps {
  channels: ChannelData[];
}

function openChannel(ch: ChannelData) {
  if (ch.disabled || !ch.href) return;
  const href = ch.href;
  // External (Telegram) → new tab; same-origin Web Chat → same tab is fine, new tab OK too
  if (href.startsWith('http')) {
    window.open(href, '_blank', 'noopener,noreferrer');
    return;
  }
  window.open(href, '_blank', 'noopener,noreferrer');
}

export const ChannelConnector: React.FC<ChannelConnectorProps> = ({ channels }) => {
  const [expanded, setExpanded] = useState<string | null>(null);

  return (
    <div className="space-y-3">
      {channels.map((ch, i) => {
        const isOpen = expanded === ch.id;
        const isConnected = ch.status === 'connected';
        const label = ch.actionLabel ?? (isConnected ? 'Open' : 'Connect');
        const canAct = !ch.disabled && Boolean(ch.href);

        return (
          <motion.div
            key={ch.id}
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, amount: 0.2 }}
            transition={{ duration: 0.5, delay: i * 0.09, ease: [0.22, 1, 0.36, 1] }}
            whileHover={{ y: 0, scale: 1.015, transition: { duration: 0.25 } }}
            className="glass rounded-2xl overflow-hidden"
          >
            <motion.div
              animate={{ y: floatY[i % floatY.length] }}
              transition={{ duration: 7 + i * 1.3, repeat: Infinity, ease: 'easeInOut', delay: i * 1.8 }}
              whileHover={{ y: 0 }}
            >
              <div className="flex items-center gap-3 p-4">
                <div className="w-10 h-10 rounded-xl bg-emerald-500/10 text-emerald-400 flex items-center justify-center flex-shrink-0">
                  {ChannelIcon[ch.icon] ?? <Globe size={20} />}
                </div>

                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="font-semibold text-white text-sm" style={{ fontFamily: 'Sora, sans-serif' }}>
                      {ch.name}
                    </span>
                    <StatusBadge status={ch.status} />
                  </div>
                  <p className="text-gray-400 text-xs mt-0.5 truncate">{ch.meta1}</p>
                  <p className="text-gray-500 text-[10px]">{ch.meta2}</p>
                </div>

                <div className="flex flex-col items-end gap-1.5 flex-shrink-0">
                  <motion.button
                    type="button"
                    whileHover={canAct ? { scale: 1.06 } : undefined}
                    whileTap={canAct ? { scale: 0.97 } : undefined}
                    disabled={!canAct}
                    onClick={() => openChannel(ch)}
                    className={`text-xs font-semibold px-4 py-1.5 rounded-lg transition-all ${
                      !canAct
                        ? 'bg-white/6 text-gray-500 border border-white/10 cursor-not-allowed'
                        : isConnected
                          ? 'bg-emerald-500/12 text-emerald-400 border border-emerald-500/25 hover:bg-emerald-500/20 cursor-pointer'
                          : 'bg-gradient-to-r from-emerald-500 to-amber-400 text-black hover:shadow-[0_0_16px_rgba(52,211,153,0.35)] cursor-pointer'
                    }`}
                  >
                    {label}
                  </motion.button>
                  {ch.note && (
                    <button
                      type="button"
                      onClick={() => setExpanded(isOpen ? null : ch.id)}
                      className="text-[10px] text-gray-600 hover:text-emerald-400 flex items-center gap-0.5 transition-colors cursor-pointer"
                    >
                      Details
                      <ChevronDown
                        size={12}
                        className={`transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`}
                      />
                    </button>
                  )}
                </div>
              </div>

              {ch.note && (
                <div
                  className={`transition-all duration-300 ease-in-out overflow-hidden ${
                    isOpen ? 'max-h-48 opacity-100' : 'max-h-0 opacity-0'
                  }`}
                >
                  <div className="mx-4 mb-4 rounded-xl p-3 bg-emerald-500/6 border border-emerald-500/20">
                    <p className="text-xs text-emerald-200/80 leading-relaxed">{ch.note}</p>
                  </div>
                </div>
              )}
            </motion.div>
          </motion.div>
        );
      })}
    </div>
  );
};
