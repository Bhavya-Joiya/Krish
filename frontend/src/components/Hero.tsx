import React from 'react';
import { motion } from 'framer-motion';
import { StatusBadge } from './StatusBadge';
import { ChannelConnector } from './ChannelConnector';
import { CharStagger } from './TextAnimate';
import { Magnetic } from './Magnetic';
import type { ChannelData } from '../types';

export const SeedlingIcon: React.FC<{ className?: string }> = ({ className = 'w-4 h-4' }) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" className={className}>
    <path d="M12 22V12" />
    <path d="M12 12C12 7.5 8.5 4 4 4C4 8.5 7.5 12 12 12Z" fill="currentColor" fillOpacity="0.18" />
    <path d="M12 12C12 7.5 15.5 4 20 4C20 8.5 16.5 12 12 12Z" fill="currentColor" fillOpacity="0.18" />
    <path d="M12 14c1.5-1 3.5-1 5 0" />
    <path d="M12 16c-1.5-1-3.5-1-5 0" />
  </svg>
);

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
    <section id="hero-grass-trigger" className="relative overflow-hidden pt-16 pb-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 lg:gap-16 items-start">

          {/* ── LEFT: Hero copy ── */}
          <motion.div
            className="space-y-6"
            variants={containerVariants}
            initial="hidden"
            animate={splashDone ? 'show' : 'hidden'}
          >
            {/* Eyebrow — crisp and separated above heading */}
            <motion.div variants={itemVariants}>
              <Magnetic strength={0.2}>
                <div className="inline-flex items-center gap-2 glass rounded-full px-4 py-1.5 border border-krish-ochre/25 hover:border-krish-ochre/45 transition-colors cursor-default shadow-lg">
                  <motion.div
                    animate={{ rotate: [-6, 6, -6] }}
                    transition={{ duration: 4, repeat: Infinity, ease: 'easeInOut' }}
                  >
                    <SeedlingIcon className="w-4 h-4 text-krish-ochre" />
                  </motion.div>
                  <span className="text-xs font-semibold text-krish-wheat tracking-wide uppercase">
                    AI Crop Advisory
                  </span>
                  <span className="w-1.5 h-1.5 rounded-full bg-krish-ochre animate-ping ml-1" />
                </div>
              </Magnetic>
            </motion.div>

            {/* Main heading with localized dawn radial glow behind Krish only */}
            <div className="relative">
              {/* Visible dawn radial glow — localized behind Krish wordmark, not washing out eyebrow badge */}
              <div
                className="absolute -top-1 -left-4 w-96 h-36 pointer-events-none rounded-full blur-3xl z-0"
                style={{
                  background: 'radial-gradient(circle at 35% 60%, rgba(232, 185, 95, 0.30) 0%, rgba(200, 129, 26, 0.12) 45%, transparent 70%)',
                }}
              />

              <motion.h1
                variants={itemVariants}
                className="text-4xl sm:text-5xl font-bold text-white leading-[1.2] tracking-tight relative z-10"
                style={{ fontFamily: 'var(--font-heading)' }}
              >
                <span
                  className="font-display italic font-semibold text-krish-wheat block mb-3 text-5xl sm:text-6xl tracking-wide"
                  style={{ fontFamily: 'var(--font-display)' }}
                >
                  <CharStagger text="Krish" delay={0.15} />
                </span>
                <span className="text-white">Your Farm's </span>
                <span className="text-[#F3D382] font-extrabold drop-shadow-sm">AI Advisor</span>
                <br />
                <span className="text-white">Right in </span>
                <span className="relative inline-block text-[#F3D382] font-extrabold">
                  Chat
                  <span className="absolute -bottom-1 left-0 right-0 h-0.5 bg-krish-ochre rounded-full opacity-90 shadow-[0_0_8px_rgba(200,129,26,0.6)]" />
                </span>
              </motion.h1>
            </div>

            {/* Sub-copy */}
            <motion.div variants={itemVariants} className="space-y-2.5">
              <p className="text-gray-300 text-base leading-relaxed max-w-lg">
                Farmers send a photo, a voice note, or a text — and Krish replies with practical advice in seconds.
                No app download. No registration. Works in Hindi, Hinglish &amp; English.
              </p>
              <p className="text-gray-400 text-sm leading-relaxed max-w-lg">
                Powered by Gemini vision, Groq speech, live weather data, and real mandi prices — all inside a single chat.
              </p>
            </motion.div>

            {/* Status + version row */}
            <motion.div variants={itemVariants} className="flex flex-wrap items-center gap-3 pt-2">
              <Magnetic strength={0.15}>
                <div className="glass flex items-center gap-2 rounded-xl px-4 py-2 border border-krish-ochre/20 hover:border-krish-ochre/40 transition-colors">
                  <StatusBadge status="connected" label="All Systems Live" />
                </div>
              </Magnetic>
              <div className="glass flex items-center gap-2 rounded-xl px-4 py-2 border border-krish-soil/30">
                <span className="text-gray-400 text-xs font-mono">v1.0.0</span>
                <span className="text-gray-600">|</span>
                <span className="text-gray-400 text-xs">MVP Demo</span>
              </div>
            </motion.div>
          </motion.div>

          {/* ── RIGHT: Channel Connector ── */}
          <motion.div
            initial={{ opacity: 0, x: 28 }}
            animate={splashDone ? { opacity: 1, x: 0 } : { opacity: 0, x: 28 }}
            transition={{ duration: 0.75, delay: 0.35, ease: [0.22, 1, 0.36, 1] }}
            className="space-y-4"
          >
            <p className="text-xs font-bold text-krish-ochre/80 uppercase tracking-widest flex items-center gap-2"
               style={{ fontFamily: 'var(--font-heading)' }}>
              <span>Connect &amp; Try Now</span>
              <span className="w-1.5 h-1.5 rounded-full bg-krish-wheat animate-pulse" />
            </p>
            <ChannelConnector channels={channels} />
          </motion.div>
        </div>
      </div>
    </section>
  );
};