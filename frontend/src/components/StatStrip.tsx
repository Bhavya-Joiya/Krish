import React from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, Camera, Users, Clock, Signal } from 'lucide-react';
import { CountUp } from './CountUp';
import type { StatCardData } from '../types';

interface StatStripProps {
  cards: StatCardData[];
}

const iconMap: Record<string, React.ReactNode> = {
  camera: <Camera size={18} strokeWidth={1.8} />,
  users:  <Users size={18} strokeWidth={1.8} />,
  clock:  <Clock size={18} strokeWidth={1.8} />,
  signal: <Signal size={18} strokeWidth={1.8} />,
};

const containerVariants = {
  hidden: {},
  show: {
    transition: {
      staggerChildren: 0.09,
    },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 16 },
  show: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.55, ease: [0.22, 1, 0.36, 1] as const },
  },
};

/* ─── Borderless Bloomberg-style data row with rich animations ────────────── */
export const StatStrip: React.FC<StatStripProps> = ({ cards }) => {
  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      whileInView="show"
      viewport={{ once: true, amount: 0.2 }}
      className="w-full flex flex-col sm:flex-row items-stretch divide-y sm:divide-y-0 sm:divide-x divide-krish-clay/30 rounded-2xl overflow-hidden border border-krish-clay/25 bg-[#130E0A]/90 shadow-xl backdrop-blur-md"
    >
      {cards.map((card, i) => (
        <motion.div
          key={card.label}
          variants={itemVariants}
          whileHover={{ backgroundColor: 'rgba(200, 129, 26, 0.08)', y: -2 }}
          transition={{ duration: 0.2 }}
          className="flex-1 flex flex-col justify-center px-6 py-6 relative group cursor-default"
        >
          {/* Top subtle row with icon and badge */}
          <div className="flex items-center justify-between mb-2">
            <div className="text-krish-wheat/60 group-hover:text-krish-wheat transition-colors">
              {iconMap[card.icon]}
            </div>
            {card.badge && (
              <span className="inline-flex items-center gap-1.5 text-[10px] font-semibold text-krish-wheat bg-krish-neem/25 border border-krish-neem/40 rounded-full px-2.5 py-0.5 w-fit shadow-sm">
                <span className="w-1.5 h-1.5 rounded-full bg-krish-wheat animate-pulse" />
                {card.badge}
              </span>
            )}
          </div>

          {/* Value with CountUp */}
          <p
            className="text-3xl sm:text-4xl font-bold text-krish-wheat leading-none tracking-tight text-shimmer"
            style={{ fontFamily: 'var(--font-mono)' }}
          >
            <CountUp value={card.value} duration={1.6 + i * 0.2} />
          </p>

          {/* Label */}
          <p className="text-gray-400 text-xs mt-2 font-medium leading-snug group-hover:text-gray-200 transition-colors">
            {card.label}
          </p>

          {/* Trend / subtitle */}
          {card.trend && (
            <p className="text-krish-ochre text-xs mt-2 flex items-center gap-1 font-medium">
              <TrendingUp size={12} className="animate-bounce" />
              {card.trend}
            </p>
          )}

          {/* Bottom animated accent bar */}
          <div className="absolute bottom-0 left-4 right-4 h-0.5 bg-gradient-to-r from-transparent via-krish-ochre/60 to-transparent scale-x-0 group-hover:scale-x-100 transition-transform duration-300 origin-center" />
        </motion.div>
      ))}
    </motion.div>
  );
};