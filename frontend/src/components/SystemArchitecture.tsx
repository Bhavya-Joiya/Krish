import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { LayoutGrid, ChevronDown, ArrowRight } from 'lucide-react';
import { TiltCard } from './TiltCard';

const Box: React.FC<{ label: string; sub?: string; accent?: boolean }> = ({ label, sub, accent }) => (
  <motion.div
    whileHover={{ scale: 1.05, y: -2 }}
    transition={{ type: 'spring', stiffness: 350, damping: 15 }}
    className={`rounded-xl px-4 py-3 text-center border shadow-md transition-colors cursor-default ${
      accent
        ? 'bg-krish-ochre/20 border-krish-ochre/40 text-krish-wheat hover:border-krish-ochre/60 hover:shadow-[0_0_16px_rgba(200,129,26,0.3)]'
        : 'bg-krish-soil/30 border-krish-clay/25 text-white hover:border-krish-clay/45'
    }`}
  >
    <p className="text-xs font-semibold leading-snug" style={{ fontFamily: 'var(--font-heading)' }}>{label}</p>
    {sub && <p className="text-[10px] mt-0.5 text-gray-400 font-mono">{sub}</p>}
  </motion.div>
);

const Arrow: React.FC<{ label?: string }> = ({ label }) => (
  <div className="flex flex-col items-center justify-center px-1 flex-shrink-0">
    {label && <span className="text-[9px] text-krish-wheat/60 mb-0.5 whitespace-nowrap font-mono">{label}</span>}
    <div className="flex items-center relative">
      <div className="h-px w-5 bg-krish-clay/50" />
      <ArrowRight size={12} className="text-krish-ochre -ml-1 animate-pulse" />
    </div>
  </div>
);

export const SystemArchitecture: React.FC = () => {
  const [open, setOpen] = useState(false);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, amount: 0.15 }}
      transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
    >
      <TiltCard
        maxTilt={3}
        glow
        className="glass rounded-2xl overflow-hidden border border-krish-clay/25 shadow-xl"
      >
        <button
          onClick={() => setOpen(!open)}
          className="w-full flex items-center justify-between px-6 py-5 hover:bg-white/5 transition-colors cursor-pointer"
        >
          <div className="flex items-center gap-3.5">
            <motion.div
              whileHover={{ rotate: 15 }}
              className="w-10 h-10 rounded-xl bg-krish-ochre/15 border border-krish-ochre/25 text-krish-wheat flex items-center justify-center flex-shrink-0 shadow"
            >
              <LayoutGrid size={20} strokeWidth={1.8} />
            </motion.div>
            <div className="text-left">
              <p className="font-semibold text-white text-sm" style={{ fontFamily: 'var(--font-heading)' }}>
                System Architecture
              </p>
              <p className="text-gray-400 text-xs">End-to-end multi-modal data flow diagram</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <span className="hidden sm:inline-flex text-[10px] font-bold text-krish-wheat bg-krish-ochre/15 border border-krish-ochre/30 rounded-full px-2.5 py-1 shadow">
              Demo infra cost: $0
            </span>
            <ChevronDown
              size={18}
              className={`text-krish-wheat/70 transition-transform duration-300 ${open ? 'rotate-180' : ''}`}
            />
          </div>
        </button>

        <motion.div
          initial={false}
          animate={open ? { height: 'auto', opacity: 1 } : { height: 0, opacity: 0 }}
          transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
          className="overflow-hidden"
        >
          <div className="px-6 pb-6 border-t border-krish-clay/20">
            <div className="mt-5 space-y-6">
              {/* Main flow */}
              <div className="flex items-center gap-2">
                <div className="h-px flex-1 bg-krish-clay/30" />
                <span className="text-[10px] text-krish-wheat/70 font-semibold uppercase tracking-wider font-mono">Main Request Flow</span>
                <div className="h-px flex-1 bg-krish-clay/30" />
              </div>
              <div className="overflow-x-auto pb-2">
                <div className="flex items-center gap-1.5 min-w-max p-2">
                  <Box label="Farmer" sub="Telegram / WhatsApp / Photo" />
                  <Arrow />
                  <Box label="Channel Webhooks" sub="Telegram + Green-API" />
                  <Arrow />
                  <Box label="FastAPI Backend" sub="Python / Uvicorn" accent />
                  <Arrow />
                  <div className="flex flex-col gap-2">
                    <Box label="Vision Model" sub="Gemini Vision" />
                    <Box label="Speech STT/TTS" sub="Groq Whisper / edge-tts" />
                  </div>
                  <Arrow />
                  <Box label="SQLite" sub="Logs + advisories" />
                  <Arrow label="reply" />
                  <Box label="Farmer" sub="receives advice" />
                </div>
              </div>

              {/* Proactive loop */}
              <div className="flex items-center gap-2">
                <div className="h-px flex-1 bg-krish-clay/30" />
                <span className="text-[10px] text-krish-wheat/70 font-semibold uppercase tracking-wider font-mono">Proactive Advisory Loop</span>
                <div className="h-px flex-1 bg-krish-clay/30" />
              </div>
              <div className="overflow-x-auto pb-2">
                <div className="flex items-center gap-1.5 min-w-max p-2">
                  <Box label="Scheduler" sub="APScheduler / Cron" />
                  <Arrow />
                  <Box label="Weather API" sub="OpenWeather" />
                  <Arrow />
                  <Box label="FastAPI Backend" sub="Alert Engine" accent />
                  <Arrow label="push" />
                  <Box label="Telegram Alert" sub="Unprompted notification" />
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      </TiltCard>
    </motion.div>
  );
};