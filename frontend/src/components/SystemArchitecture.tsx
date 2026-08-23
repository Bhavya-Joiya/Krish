import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { LayoutGrid, ChevronDown, ArrowRight } from 'lucide-react';

const Box: React.FC<{ label: string; sub?: string; accent?: boolean }> = ({ label, sub, accent }) => (
  <div className={`rounded-xl px-4 py-3 text-center border ${
    accent
      ? 'bg-emerald-500/15 border-emerald-500/30 text-emerald-300'
      : 'bg-white/6 border-white/10 text-white'
  }`}>
    <p className="text-xs font-semibold leading-snug" style={{ fontFamily: 'Sora, sans-serif' }}>{label}</p>
    {sub && <p className="text-[10px] mt-0.5 text-gray-500">{sub}</p>}
  </div>
);

const Arrow: React.FC<{ label?: string }> = ({ label }) => (
  <div className="flex flex-col items-center justify-center px-1 flex-shrink-0">
    {label && <span className="text-[9px] text-gray-600 mb-0.5 whitespace-nowrap">{label}</span>}
    <div className="flex items-center">
      <div className="h-px w-5 bg-gray-700" />
      <ArrowRight size={12} className="text-gray-600 -ml-1" />
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
      className="glass rounded-2xl overflow-hidden"
    >
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between px-6 py-4 hover:bg-white/3 transition-colors cursor-pointer"
      >
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-emerald-500/10 text-emerald-400 flex items-center justify-center flex-shrink-0">
            <LayoutGrid size={20} strokeWidth={1.8} />
          </div>
          <div className="text-left">
            <p className="font-semibold text-white text-sm" style={{ fontFamily: 'Sora, sans-serif' }}>
              System Architecture
            </p>
            <p className="text-gray-500 text-xs">End-to-end data flow diagram</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <span className="hidden sm:inline-flex text-[10px] font-bold text-emerald-400 bg-emerald-400/8 border border-emerald-400/20 rounded-full px-2.5 py-1">
            Demo infra cost: $0
          </span>
          <ChevronDown
            size={16}
            className={`text-gray-600 transition-transform duration-200 ${open ? 'rotate-180' : ''}`}
          />
        </div>
      </button>

      <div className={`transition-all duration-400 ease-in-out overflow-hidden ${open ? 'max-h-[600px] opacity-100' : 'max-h-0 opacity-0'}`}>
        <div className="px-6 pb-6 border-t border-white/6">
          <div className="mt-5 space-y-6">
            {/* Main flow */}
            <div className="flex items-center gap-2">
              <div className="h-px flex-1 bg-white/6" />
              <span className="text-[10px] text-gray-600 font-semibold uppercase tracking-wider">Main Request Flow</span>
              <div className="h-px flex-1 bg-white/6" />
            </div>
            <div className="overflow-x-auto pb-2">
              <div className="flex items-center gap-1 min-w-max">
                <Box label="👨‍🌾 Farmer" sub="Telegram / Voice / Photo" />
                <Arrow />
                <Box label="Telegram Bot API" sub="Webhook" />
                <Arrow />
                <Box label="FastAPI Backend" sub="Python / Uvicorn" accent />
                <Arrow />
                <div className="flex flex-col gap-2">
                  <Box label="🧠 Vision Model" sub="Gemini / Groq" />
                  <Box label="🎙 Speech STT/TTS" sub="Groq Whisper / edge-tts" />
                </div>
                <Arrow />
                <Box label="SQLite" sub="Logs + advisories" />
                <Arrow label="reply" />
                <Box label="👨‍🌾 Farmer" sub="receives advice" />
              </div>
            </div>

            {/* Proactive loop */}
            <div className="flex items-center gap-2">
              <div className="h-px flex-1 bg-white/6" />
              <span className="text-[10px] text-gray-600 font-semibold uppercase tracking-wider">Proactive Loop</span>
              <div className="h-px flex-1 bg-white/6" />
            </div>
            <div className="overflow-x-auto pb-2">
              <div className="flex items-center gap-1 min-w-max">
                <Box label="⏰ Scheduler" sub="Cron / APScheduler" />
                <Arrow />
                <Box label="Weather API" sub="OpenWeather" />
                <Arrow />
                <Box label="FastAPI Backend" sub="Alert engine" accent />
                <Arrow label="push" />
                <Box label="📲 Telegram Alert" sub="Unprompted notification" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
};
