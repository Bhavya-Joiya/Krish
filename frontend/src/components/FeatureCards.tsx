import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Camera, Mic, CloudRain, Play, Pause, ShieldAlert, Sparkles, TrendingUp, ChevronDown } from 'lucide-react';
import { TiltCard } from './TiltCard';

interface FeatureCardItem {
  id: string;
  icon: string;
  title: string;
  description: string;
  tag: 'Live' | 'Roadmap';
}

const iconMap: Record<string, React.ReactNode> = {
  camera:      <Camera    className="w-5 h-5" />,
  mic:         <Mic       className="w-5 h-5" />,
  'cloud-rain':<CloudRain className="w-5 h-5" />,
};

/* ─── WhatsApp-style chat bubble mockups with micro-animations ────────────── */
const ChatBubbleMock: React.FC<{ id: string }> = ({ id }) => {
  const [isPlaying, setIsPlaying] = useState(false);

  if (id === 'photo') {
    return (
      <div className="mt-4 space-y-3">
        {/* User prompt with Leaf Scan & Laser Beam */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 10 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          className="flex justify-end"
        >
          <div className="bg-[#2C1A0F]/85 border border-krish-clay/35 rounded-2xl rounded-tr-sm p-2.5 max-w-[85%] shadow-md relative overflow-hidden">
            <div className="w-48 h-28 rounded-lg overflow-hidden bg-krish-soil/60 flex flex-col items-center justify-center relative border border-krish-clay/20 group">
              <Camera className="w-8 h-8 text-krish-wheat/40 mb-1 group-hover:scale-110 transition-transform" />
              <span className="text-[10px] font-mono text-krish-wheat/70 uppercase tracking-widest">leaf_scan_01.jpg</span>
              
              {/* Laser scanning line animation */}
              <motion.div
                animate={{ y: [-50, 60, -50] }}
                transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }}
                className="absolute inset-x-0 h-0.5 bg-gradient-to-r from-transparent via-krish-wheat to-transparent shadow-[0_0_8px_#E8C56A]"
              />
            </div>
            <p className="text-[9px] text-krish-wheat/45 text-right mt-1.5 font-mono flex items-center justify-end gap-1">
              9:41 AM <span className="text-[#4ADE80]">✓✓</span>
            </p>
          </div>
        </motion.div>

        {/* AI response with Confidence Gauge */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 10 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.15 }}
          className="flex justify-start"
        >
          <div className="bg-[#1C281D]/90 border border-krish-neem/40 rounded-2xl rounded-tl-sm px-4 py-3.5 max-w-[90%] shadow-lg">
            <div className="flex items-center gap-2 mb-2 flex-wrap">
              <div className="w-5 h-5 rounded-full bg-krish-neem flex items-center justify-center text-krish-wheat text-[10px] font-bold">K</div>
              <span className="text-xs font-semibold text-krish-wheat">Krish AI</span>
              <span className="text-[9px] bg-red-900/40 text-red-300 rounded-full px-2 py-0.5 font-semibold border border-red-500/20 uppercase tracking-wider flex items-center gap-1">
                <span className="w-1 h-1 rounded-full bg-red-400 animate-ping" /> Early Blight
              </span>
            </div>

            {/* Confidence bar */}
            <div className="mb-2 bg-black/30 rounded-md p-1.5 border border-white/5">
              <div className="flex justify-between text-[10px] text-krish-wheat mb-1 font-mono">
                <span>Confidence</span>
                <span className="font-bold text-[#4ADE80]">98.4%</span>
              </div>
              <div className="w-full bg-krish-soil/50 h-1.5 rounded-full overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  whileInView={{ width: '98.4%' }}
                  viewport={{ once: true }}
                  transition={{ duration: 1.2, delay: 0.3, ease: 'easeOut' }}
                  className="bg-gradient-to-r from-krish-ochre to-[#4ADE80] h-full rounded-full"
                />
              </div>
            </div>

            <p className="text-[11px] text-gray-300 leading-relaxed font-sans">
              <strong className="text-krish-wheat">Diagnosis:</strong> Alternaria solani<br />
              <strong className="text-krish-wheat">Action Plan:</strong> Apply Mancozeb 75WP @ 2g/L. Spray in late afternoon.
            </p>
            <p className="text-[9px] text-krish-wheat/35 mt-2.5 text-right font-mono">9:41 AM ✓✓</p>
          </div>
        </motion.div>
      </div>
    );
  }

  if (id === 'voice') {
    return (
      <div className="mt-4 space-y-3">
        {/* User prompt with Live Equalizer */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 10 }}
          whileInView={{ opacity: 1, scale: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.4 }}
          className="flex justify-end"
        >
          <div className="bg-[#2C1A0F]/85 border border-krish-clay/35 rounded-2xl rounded-tr-sm px-4 py-3 max-w-[85%] shadow-md">
            <div className="flex items-center gap-2.5">
              <Mic className="w-4 h-4 text-krish-ochre animate-pulse" />
              <div className="flex items-center gap-1 h-6">
                {[3,7,12,6,14,9,5,11,7,10,4,8,6,12].map((h, i) => (
                  <motion.div
                    key={i}
                    animate={{ height: [`${Math.max(3, h * 0.4)}px`, `${h}px`, `${Math.max(3, h * 0.6)}px`] }}
                    transition={{ duration: 0.8 + (i % 4) * 0.2, repeat: Infinity, ease: 'easeInOut' }}
                    className="w-0.5 bg-krish-wheat/70 rounded-full"
                  />
                ))}
              </div>
              <span className="text-[10px] text-krish-wheat/60 font-mono">0:08</span>
            </div>
            <p className="text-[9px] text-krish-wheat/40 mt-1 text-right font-mono flex items-center justify-end gap-1">
              9:43 AM <span className="text-[#4ADE80]">✓✓</span>
            </p>
          </div>
        </motion.div>

        {/* AI voice reply */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 10 }}
          whileInView={{ opacity: 1, scale: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.4, delay: 0.15 }}
          className="flex justify-start"
        >
          <div className="bg-[#1C281D]/90 border border-krish-neem/40 rounded-2xl rounded-tl-sm px-4 py-3.5 max-w-[90%] shadow-lg">
            <div className="flex items-center gap-2 mb-1.5 flex-wrap">
              <div className="w-5 h-5 rounded-full bg-krish-neem flex items-center justify-center text-krish-wheat text-[10px] font-bold">K</div>
              <span className="text-xs font-semibold text-krish-wheat">Krish AI</span>
              <span className="text-[9px] text-krish-wheat/50 italic bg-krish-neem/20 px-2 py-0.5 rounded-full border border-krish-neem/30">Hindi Voice STT</span>
            </div>

            <div className="flex items-center gap-2.5 mb-2.5 bg-black/25 rounded-lg p-2 border border-white/5">
              <button
                onClick={() => setIsPlaying(!isPlaying)}
                className="w-6 h-6 rounded-full bg-krish-neem flex items-center justify-center text-krish-wheat text-[10px] hover:bg-krish-neem/80 transition-colors cursor-pointer shadow"
              >
                {isPlaying ? <Pause className="w-2.5 h-2.5 fill-current" /> : <Play className="w-2.5 h-2.5 fill-current" />}
              </button>
              <div className="flex items-center gap-1 h-5 flex-1">
                {[4,9,6,13,5,10,8,12,4,9,7,11,4].map((h, i) => (
                  <motion.div
                    key={i}
                    animate={isPlaying ? { height: [`${h * 0.3}px`, `${h}px`, `${h * 0.4}px`] } : { height: `${h * 0.6}px` }}
                    transition={{ duration: 0.6 + (i % 3) * 0.2, repeat: Infinity, ease: 'easeInOut' }}
                    className={`w-0.5 rounded-full transition-colors ${isPlaying ? 'bg-krish-wheat' : 'bg-krish-wheat/40'}`}
                  />
                ))}
              </div>
              <span className="text-[10px] text-krish-wheat/60 font-mono">{isPlaying ? '0:05' : '0:12'}</span>
            </div>

            <p className="text-[11px] text-gray-300 italic font-sans leading-relaxed">
              "गेहूं की फसल में रतुआ (rust) के लक्षण हैं। प्रोपिकोनाजोल का छिड़काव तुरंत करें और 3 दिन सिंचाई रोकें।"
            </p>
            <p className="text-[9px] text-krish-wheat/35 mt-2 text-right font-mono">9:43 AM ✓✓</p>
          </div>
        </motion.div>
      </div>
    );
  }

  if (id === 'weather') {
    return (
      <div className="mt-4 space-y-3">
        {/* Proactive alert */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 10 }}
          whileInView={{ opacity: 1, scale: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.4 }}
          className="flex justify-start"
        >
          <div className="bg-[#1C281D]/90 border border-krish-neem/40 rounded-2xl rounded-tl-sm px-4 py-3.5 max-w-[90%] shadow-lg">
            <div className="flex items-center gap-2 mb-2 flex-wrap">
              <div className="w-5 h-5 rounded-full bg-krish-neem flex items-center justify-center text-krish-wheat text-[10px] font-bold">K</div>
              <span className="text-xs font-semibold text-krish-wheat">Krish AI</span>
              <span className="text-[9px] bg-krish-ochre/20 text-krish-wheat rounded-full px-2 py-0.5 font-semibold border border-krish-ochre/35 flex items-center gap-1">
                <ShieldAlert className="w-2.5 h-2.5 animate-bounce" /> Weather Alert
              </span>
            </div>
            <p className="text-[11px] text-gray-300 leading-relaxed font-sans">
              🌧 <strong>Rain expected in 24h</strong> (Nashik, 18–25mm).<br /><br />
              Fungicide spray scheduled today might wash off. <strong>Reschedule to tomorrow evening.</strong>
            </p>
            <div className="mt-3 flex gap-2">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="text-[10px] text-krish-wheat font-semibold bg-krish-ochre/25 rounded-md px-2.5 py-1 border border-krish-ochre/40 hover:bg-krish-ochre/40 transition-colors cursor-pointer"
              >
                Reschedule
              </motion.button>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="text-[10px] text-gray-400 bg-white/5 rounded-md px-2.5 py-1 border border-white/10 hover:bg-white/10 transition-colors cursor-pointer"
              >
                Dismiss
              </motion.button>
            </div>
            <p className="text-[9px] text-krish-wheat/35 mt-2.5 text-right font-mono">6:00 AM ✓✓</p>
          </div>
        </motion.div>

        {/* Mandi update */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 10 }}
          whileInView={{ opacity: 1, scale: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.4, delay: 0.15 }}
          className="flex justify-start"
        >
          <div className="bg-[#1C281D]/90 border border-krish-neem/40 rounded-2xl rounded-tl-sm px-4 py-3.5 max-w-[90%] shadow-lg">
            <div className="flex items-center gap-2 mb-2">
              <div className="w-5 h-5 rounded-full bg-krish-neem flex items-center justify-center text-krish-wheat text-[10px] font-bold">K</div>
              <span className="text-xs font-semibold text-krish-wheat">Krish AI</span>
              <span className="text-[9px] bg-krish-soil text-krish-wheat/80 rounded px-1.5 py-0.5 font-mono flex items-center gap-1">
                <TrendingUp className="w-2.5 h-2.5 text-[#4ADE80]" /> Mandi rates
              </span>
            </div>
            <p className="text-[11px] text-gray-300 font-sans leading-relaxed">
              📊 <strong>Latur Mandi today:</strong><br />
              Soybean: ₹4,820/q <span className="text-[#4ADE80] font-semibold">(+2.1%)</span><br />
              Cotton: ₹6,150/q <span className="text-red-400 font-semibold">(-0.8%)</span>
            </p>
            <p className="text-[9px] text-krish-wheat/35 mt-2 text-right font-mono">6:01 AM ✓✓</p>
          </div>
        </motion.div>
      </div>
    );
  }
  return null;
};

/* ─── Horizontal Scroll-Snap Feature Cards with click-to-expand accordion ─── */
export const FeatureCards: React.FC<{ cards: FeatureCardItem[] }> = ({ cards }) => {
  // null = all collapsed; string = id of the currently open card
  const [openId, setOpenId] = useState<string | null>(null);

  return (
    <div className="w-full overflow-x-auto pb-4 scrollbar-thin snap-x snap-mandatory flex gap-6 lg:grid lg:grid-cols-3 lg:items-start">
      {cards.map((card, i) => {
        const hasIcon = iconMap[card.icon] ?? <Sparkles className="w-5 h-5" />;
        const isOpen = openId === card.id;
        return (
          <motion.div
            key={card.id}
            initial={{ opacity: 0, y: 28, scale: 0.95 }}
            whileInView={{ opacity: 1, y: 0, scale: 1 }}
            viewport={{ once: true, amount: 0.15 }}
            transition={{ duration: 0.65, delay: i * 0.1, ease: [0.22, 1, 0.36, 1] }}
            className="snap-center flex-shrink-0 w-[88vw] sm:w-[410px] lg:w-auto"
          >
            <TiltCard
              maxTilt={isOpen ? 0 : 5}
              glow
              className={`h-full bg-[#130E0A]/95 border-2 transition-colors rounded-3xl shadow-2xl flex flex-col ${
                isOpen
                  ? 'border-krish-ochre/55'
                  : 'border-krish-clay/35 hover:border-krish-ochre/40'
              }`}
            >
              {/* ── Clickable header (always visible) ── */}
              <button
                onClick={() => setOpenId(isOpen ? null : card.id)}
                className="w-full text-left p-5 cursor-pointer group"
                aria-expanded={isOpen}
              >
                <div className="flex items-start justify-between gap-3 mb-4">
                  <motion.div
                    whileHover={{ scale: 1.15, rotate: 6 }}
                    transition={{ type: 'spring', stiffness: 350, damping: 15 }}
                    className="w-10 h-10 rounded-xl bg-krish-ochre/15 border border-krish-ochre/25 text-krish-wheat flex items-center justify-center flex-shrink-0 shadow"
                  >
                    {hasIcon}
                  </motion.div>
                  <div className="flex items-center gap-2">
                    <span className={`text-[9px] font-bold rounded-full px-2.5 py-0.5 uppercase tracking-wider flex items-center gap-1 ${
                      card.tag === 'Live'
                        ? 'bg-krish-neem/25 text-krish-wheat border border-krish-neem/35'
                        : 'bg-krish-soil text-krish-wheat/60 border border-krish-clay/20'
                    }`}>
                      {card.tag === 'Live' ? (
                        <>
                          <span className="w-1.5 h-1.5 rounded-full bg-[#4ADE80] animate-pulse" />
                          Live
                        </>
                      ) : (
                        '◌ Roadmap'
                      )}
                    </span>
                    {/* Rotating chevron indicates open/closed */}
                    <motion.div
                      animate={{ rotate: isOpen ? 180 : 0 }}
                      transition={{ duration: 0.3, ease: [0.22, 1, 0.36, 1] }}
                      className="text-krish-wheat/40 group-hover:text-krish-wheat/70 transition-colors"
                    >
                      <ChevronDown className="w-4 h-4" />
                    </motion.div>
                  </div>
                </div>

                <h3
                  className="font-semibold text-white text-base leading-tight group-hover:text-krish-wheat transition-colors"
                  style={{ fontFamily: 'var(--font-heading)' }}
                >
                  {card.title}
                </h3>
                <p className="text-gray-400 text-xs mt-1.5 leading-relaxed">
                  {card.description}
                </p>

                {/* Collapsed hint */}
                {!isOpen && (
                  <p className="text-krish-ochre/50 text-[10px] mt-3 flex items-center gap-1 font-medium tracking-wide">
                    <ChevronDown className="w-3 h-3" /> Click to see demo
                  </p>
                )}
              </button>

              {/* ── Expandable chat sandbox ── */}
              <AnimatePresence initial={false}>
                {isOpen && (
                  <motion.div
                    key="sandbox"
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.45, ease: [0.22, 1, 0.36, 1] }}
                    className="overflow-hidden px-5 pb-5"
                  >
                    <div className="border-t border-krish-clay/25 pt-4">
                      <div className="bg-[#090705]/90 rounded-2xl p-3 border border-krish-clay/20 shadow-inner">
                        <div className="flex items-center gap-2 mb-2 pb-2 border-b border-krish-clay/15">
                          <div className="w-6 h-6 rounded-full bg-krish-soil border border-krish-clay/30 flex items-center justify-center text-krish-wheat text-[10px] font-bold">K</div>
                          <div className="leading-none">
                            <span className="text-[11px] font-semibold text-white block">Krish Bot</span>
                            <span className="text-[8px] text-krish-wheat/50 tracking-wider">interactive demo</span>
                          </div>
                          <span className="text-[9px] text-[#4ADE80] font-medium ml-auto flex items-center gap-1">
                            <span className="w-1.5 h-1.5 rounded-full bg-[#4ADE80] animate-ping" /> online
                          </span>
                        </div>
                        <ChatBubbleMock id={card.id} />
                      </div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </TiltCard>
          </motion.div>
        );
      })}
    </div>
  );
};