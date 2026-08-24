import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Send, MessageSquare, Phone, Globe, ChevronDown } from 'lucide-react';
import { StatusBadge } from './StatusBadge';
import { Magnetic } from './Magnetic';
import { TiltCard } from './TiltCard';
import type { ChannelData } from '../types';

const ChannelIcon: Record<string, React.ReactNode> = {
  telegram: <Send size={18} strokeWidth={2} />,
  whatsapp: <Phone size={18} strokeWidth={2} />,
  fallback: <MessageSquare size={18} strokeWidth={2} />,
  sms:      <Phone size={18} strokeWidth={2} />,
};

interface ChannelConnectorProps {
  channels: ChannelData[];
}

function openChannel(ch: ChannelData) {
  if (ch.disabled || !ch.href) return;
  const href = ch.href;
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
            initial={{ opacity: 0, y: 20, scale: 0.97 }}
            whileInView={{ opacity: 1, y: 0, scale: 1 }}
            viewport={{ once: true, amount: 0.2 }}
            transition={{ duration: 0.5, delay: i * 0.08, ease: [0.22, 1, 0.36, 1] }}
          >
            <TiltCard
              maxTilt={4}
              glow
              className="glass rounded-2xl overflow-hidden border border-krish-ochre/15 hover:border-krish-ochre/35 transition-colors"
            >
              <div>
                <div className="flex items-center gap-3 p-4">
                  {/* Channel icon */}
                  <motion.div
                    whileHover={{ scale: 1.12, rotate: 5 }}
                    transition={{ type: 'spring', stiffness: 350, damping: 15 }}
                    className="w-10 h-10 rounded-xl bg-krish-ochre/15 border border-krish-ochre/25 text-krish-wheat flex items-center justify-center flex-shrink-0 shadow"
                  >
                    {ChannelIcon[ch.icon] ?? <Globe size={18} />}
                  </motion.div>

                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="font-semibold text-white text-sm" style={{ fontFamily: 'var(--font-heading)' }}>
                        {ch.name}
                      </span>
                      <StatusBadge status={ch.status} />
                    </div>
                    <p className="text-gray-400 text-xs mt-0.5 truncate">{ch.meta1}</p>
                    <p className="text-krish-monsoon text-[10px] font-medium">{ch.meta2}</p>
                  </div>

                  <div className="flex flex-col items-end gap-1.5 flex-shrink-0">
                    <Magnetic strength={canAct ? 0.25 : 0}>
                      <motion.button
                        type="button"
                        whileHover={canAct ? { scale: 1.05 } : undefined}
                        whileTap={canAct ? { scale: 0.95 } : undefined}
                        disabled={!canAct}
                        onClick={() => openChannel(ch)}
                        className={`text-xs font-semibold px-4 py-1.5 rounded-lg transition-all shadow-md ${
                          !canAct
                            ? 'bg-krish-soil/20 text-gray-600 border border-krish-clay/10 cursor-not-allowed'
                            : isConnected
                              ? 'bg-krish-neem/20 text-krish-wheat border border-krish-neem/40 hover:bg-krish-neem/35 hover:shadow-[0_0_16px_rgba(45,106,53,0.3)] cursor-pointer'
                              : 'bg-gradient-to-r from-krish-ochre to-krish-wheat text-[#0D0A07] hover:shadow-[0_0_18px_rgba(200,129,26,0.4)] cursor-pointer font-bold'
                        }`}
                      >
                        {label}
                      </motion.button>
                    </Magnetic>

                    {ch.note && (
                      <button
                        type="button"
                        onClick={() => setExpanded(isOpen ? null : ch.id)}
                        className="text-[10px] text-gray-400 hover:text-krish-wheat flex items-center gap-0.5 transition-colors cursor-pointer"
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
                  <motion.div
                    initial={false}
                    animate={isOpen ? { height: 'auto', opacity: 1 } : { height: 0, opacity: 0 }}
                    transition={{ duration: 0.3, ease: 'easeInOut' }}
                    className="overflow-hidden"
                  >
                    <div className="mx-4 mb-4 rounded-xl p-3 bg-krish-soil/30 border border-krish-clay/25">
                      <p className="text-xs text-krish-wheat/90 leading-relaxed">{ch.note}</p>
                    </div>
                  </motion.div>
                )}
              </div>
            </TiltCard>
          </motion.div>
        );
      })}
    </div>
  );
};