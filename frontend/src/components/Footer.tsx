import React from 'react';
import { motion } from 'framer-motion';
import { Magnetic } from './Magnetic';

const SeedlingIcon: React.FC<{ className?: string }> = ({ className = 'w-4 h-4' }) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" className={className}>
    <path d="M12 22V12" />
    <path d="M12 12C12 7.5 8.5 4 4 4C4 8.5 7.5 12 12 12Z" fill="currentColor" fillOpacity="0.18" />
    <path d="M12 12C12 7.5 15.5 4 20 4C20 8.5 16.5 12 12 12Z" fill="currentColor" fillOpacity="0.18" />
    <path d="M12 14c1.5-1 3.5-1 5 0" />
    <path d="M12 16c-1.5-1-3.5-1-5 0" />
  </svg>
);

export const Footer: React.FC = () => {
  return (
    <footer className="relative mt-20 border-t border-krish-clay/20 bg-[#0A0705]/60 backdrop-blur-md">
      {/* Subtle warm soil gradient */}
      <div className="absolute inset-0 bg-gradient-to-b from-transparent to-[#0D0A07]/90 pointer-events-none" />

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="flex flex-col md:flex-row items-center justify-between gap-8">
          {/* Logo with Magnetic effect */}
          <div className="flex items-center gap-3">
            <Magnetic strength={0.3}>
              <motion.div
                whileHover={{ scale: 1.15, rotate: 8 }}
                className="w-10 h-10 rounded-xl bg-krish-ochre/15 border border-krish-ochre/25 flex items-center justify-center text-krish-wheat shadow-md cursor-pointer"
              >
                <SeedlingIcon className="w-5 h-5" />
              </motion.div>
            </Magnetic>
            <div>
              <p
                className="text-white font-bold text-lg italic text-shimmer"
                style={{ fontFamily: 'var(--font-display)' }}
              >
                Krish
              </p>
              <p className="text-krish-monsoon text-xs font-medium">AI-Powered Crop Advisory</p>
            </div>
          </div>

          {/* Center */}
          <div className="text-center">
            <p className="text-gray-300 text-sm">
              Built for{' '}
              <span className="grad-text font-bold text-shimmer">Indian farmers</span>
              {' '}— Telegram · Web Chat · SMS (soon)
            </p>
            <p className="text-krish-monsoon text-xs mt-1 font-medium">Hindi · Hinglish · English support</p>
          </div>

          {/* Version */}
          <div className="flex flex-col items-center md:items-end gap-1">
            <div className="flex items-center gap-2">
              <span className="text-[10px] text-krish-monsoon uppercase tracking-widest font-bold">Version</span>
              <motion.code
                whileHover={{ scale: 1.06 }}
                className="text-krish-wheat text-xs bg-krish-ochre/15 border border-krish-ochre/30 rounded-full px-2.5 py-0.5 shadow-sm"
                style={{ fontFamily: 'var(--font-mono)' }}
              >
                v1.0.0-mvp
              </motion.code>
            </div>
            <p className="text-gray-500 text-xs font-mono">Hackathon Demo · Team Krish · 2026</p>
          </div>
        </div>

        {/* Bottom bar */}
        <div className="mt-10 pt-6 border-t border-krish-clay/15 flex flex-col sm:flex-row items-center justify-between gap-3">
          <p className="text-gray-500 text-xs">
            Powered by Gemini · Groq · OpenWeather · Telegram Bot API
          </p>
          <p className="text-gray-500 text-xs font-medium flex items-center gap-1.5">
            Demo infra cost:
            <span className="text-krish-wheat font-bold font-mono bg-krish-ochre/10 border border-krish-ochre/20 rounded px-1.5 py-0.5">
              $0
            </span>
          </p>
        </div>
      </div>
    </footer>
  );
};