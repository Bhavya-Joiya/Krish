import React from 'react';
import { motion } from 'framer-motion';
import { StatusBadge } from './StatusBadge';
import { ChannelConnector } from './ChannelConnector';
import type { ChannelData } from '../types';

// Stagger container + item variants
const containerVariants = {
  hidden: {},
  show: { transition: { staggerChildren: 0.12 } },
};

const itemVariants = {
  hidden: { opacity: 0, y: 28 },
  show:   { opacity: 1, y: 0, transition: { duration: 0.65, ease: [0.22, 1, 0.36, 1] as const } },
};

interface HeroProps {
  channels: ChannelData[];
  splashDone: boolean;
}

export const Hero: React.FC<HeroProps> = ({ channels, splashDone }) => {
  return (
    <section className="relative overflow-hidden pt-16 pb-12">
      {/* Subtle radial glow */}
      <div className="absolute top-0 left-1/4 w-96 h-96 bg-emerald-500/6 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute top-0 right-1/4 w-72 h-72 bg-amber-400/5 rounded-full blur-3xl pointer-events-none" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 lg:gap-16 items-start">

          {/* ── LEFT: Hero copy ── */}
          <motion.div
            className="space-y-6"
            variants={containerVariants}
            initial="hidden"
            animate={splashDone ? 'show' : 'hidden'}
          >
            {/* Eyebrow */}
            <motion.div variants={itemVariants}>
              <div className="inline-flex items-center gap-2 glass rounded-full px-4 py-1.5 border border-emerald-500/20">
                <span className="text-sm">🌱</span>
                <span className="text-xs font-semibold text-emerald-400 tracking-wide uppercase">
                  AI Crop Advisory
                </span>
              </div>
            </motion.div>

            {/* Main heading */}
            <motion.h1
              variants={itemVariants}
              className="text-4xl sm:text-5xl font-bold text-white leading-[1.1] tracking-tight"
              style={{ fontFamily: 'Sora, sans-serif' }}
            >
              Krish —{' '}
              <span className="grad-text">Your Farm's</span>
              <br />
              AI Advisor, Right in
              <br />
              <span className="relative inline-block">
                Chat
                <span className="absolute -bottom-1 left-0 right-0 h-0.5 bg-gradient-to-r from-emerald-400 to-amber-400 rounded-full opacity-70" />
              </span>
            </motion.h1>

            {/* Sub-copy */}
            <motion.div variants={itemVariants} className="space-y-2.5">
              <p className="text-gray-300 text-base leading-relaxed max-w-lg">
                Farmers send a photo, a voice note, or a text — and Krish replies with practical advice in seconds.
                No app download. No registration. Works in Hindi, Hinglish & English.
              </p>
              <p className="text-gray-300 text-sm leading-relaxed max-w-lg">
                Powered by Gemini vision, Groq speech, live weather data, and real mandi prices — all inside a single chat.
              </p>
            </motion.div>

            {/* Status + version row */}
            <motion.div variants={itemVariants} className="flex flex-wrap items-center gap-3 pt-2">
              <div className="glass flex items-center gap-2 rounded-xl px-4 py-2 border-emerald-500/15">
                <StatusBadge status="connected" label="All Systems Live" />
              </div>
              <div className="glass flex items-center gap-2 rounded-xl px-4 py-2">
                <span className="text-gray-500 text-xs font-mono">v1.0.0</span>
                <span className="text-gray-700">|</span>
                <span className="text-gray-500 text-xs">MVP Demo</span>
              </div>
            </motion.div>

            {/* Quick stats strip */}
            <motion.div
              variants={itemVariants}
              className="flex flex-wrap gap-8 pt-4 border-t border-white/8"
            >
              {[
                { val: '1.28M+', lbl: 'conversations' },
                { val: '12.4s',  lbl: 'avg response'  },
                { val: '99.6%',  lbl: 'uptime'        },
              ].map((s) => (
                <div key={s.lbl}>
                  <p
                    className="text-xl font-bold text-white"
                    style={{ fontFamily: 'JetBrains Mono, monospace' }}
                  >
                    {s.val}
                  </p>
                  <p className="text-xs text-gray-500 mt-0.5">{s.lbl}</p>
                </div>
              ))}
            </motion.div>
          </motion.div>

          {/* ── RIGHT: Channel Connector ── */}
          <motion.div
            initial={{ opacity: 0, x: 24 }}
            animate={splashDone ? { opacity: 1, x: 0 } : { opacity: 0, x: 24 }}
            transition={{ duration: 0.7, delay: 0.45, ease: [0.22, 1, 0.36, 1] }}
            className="space-y-4"
          >
            <p className="text-xs font-bold text-emerald-400/50 uppercase tracking-widest"
               style={{ fontFamily: 'Sora, sans-serif' }}>
              Connect &amp; Try Now
            </p>
            <ChannelConnector channels={channels} />
          </motion.div>
        </div>
      </div>
    </section>
  );
};
