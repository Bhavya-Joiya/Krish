import React from 'react';
import { motion } from 'framer-motion';
import { Camera, Users, Clock, Wifi, TrendingUp } from 'lucide-react';
import type { StatCardData } from '../types';

const iconMap: Record<string, React.ReactNode> = {
  camera: <Camera size={20} strokeWidth={1.8} />,
  users:  <Users  size={20} strokeWidth={1.8} />,
  clock:  <Clock  size={20} strokeWidth={1.8} />,
  signal: <Wifi   size={20} strokeWidth={1.8} />,
};

const accentMap: Record<string, { iconBg: string; valClass: string }> = {
  camera: { iconBg: 'bg-emerald-500/12 text-emerald-400', valClass: 'text-white' },
  users:  { iconBg: 'bg-amber-400/12  text-amber-400',   valClass: 'text-white' },
  clock:  { iconBg: 'bg-emerald-500/12 text-emerald-400', valClass: 'text-white' },
  signal: { iconBg: 'bg-amber-400/12  text-amber-400',   valClass: 'text-white' },
};

interface StatStripProps {
  cards: StatCardData[];
}

export const StatStrip: React.FC<StatStripProps> = ({ cards }) => {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {cards.map((card, i) => {
        const ac = accentMap[card.icon] ?? accentMap.camera;
        return (
          <motion.div
            key={card.label}
            custom={i}
            initial={{ opacity: 0, y: 24 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, amount: 0.2 }}
            transition={{ duration: 0.55, delay: i * 0.09, ease: [0.22, 1, 0.36, 1] }}
            whileHover={{ y: -4, scale: 1.02, transition: { duration: 0.25 } }}
            className="glass rounded-2xl p-5 cursor-default"
            style={{ boxShadow: '0 4px 24px rgba(0,0,0,0.35), inset 0 1px 0 rgba(255,255,255,0.05)' }}
          >
            {/* Icon + badge */}
            <div className="flex items-start justify-between mb-4">
              <div className={`w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 ${ac.iconBg}`}>
                {iconMap[card.icon]}
              </div>
              {card.badge && (
                <span className="inline-flex items-center gap-1 text-[10px] font-semibold text-emerald-400 bg-emerald-400/8 border border-emerald-400/20 rounded-full px-2 py-0.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                  {card.badge}
                </span>
              )}
            </div>

            {/* Value */}
            <p
              className={`text-3xl font-bold leading-none tracking-tight ${ac.valClass}`}
              style={{ fontFamily: 'JetBrains Mono, monospace' }}
            >
              {card.value}
            </p>

            {/* Label */}
            <p className="text-gray-400 text-sm mt-1.5 font-medium leading-snug">{card.label}</p>

            {/* Trend */}
            {card.trend && (
              <p className="text-emerald-400 text-xs mt-2 flex items-center gap-1 font-medium">
                <TrendingUp size={12} />
                {card.trend}
              </p>
            )}
          </motion.div>
        );
      })}
    </div>
  );
};
