import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { ChevronDown } from 'lucide-react';

interface FeatureCardItem {
  id: string;
  icon: string;
  title: string;
  description: string;
  tag: 'Live' | 'Roadmap';
}

/* ─── WhatsApp chat bubble mockups (dark-tinted) ─────────────────────────── */
const ChatBubbleMock: React.FC<{ id: string }> = ({ id }) => {
  if (id === 'photo') {
    return (
      <div className="mt-4 space-y-3">
        <div className="flex justify-end">
          <div className="bg-white/8 rounded-2xl rounded-tr-sm px-3 py-2 max-w-[75%]">
            <div className="w-44 h-28 rounded-lg overflow-hidden bg-gradient-to-br from-emerald-900/50 to-emerald-700/30 flex items-center justify-center relative">
              <span className="text-4xl relative z-10">🍃</span>
              <div className="absolute bottom-1 right-1 bg-black/50 text-[9px] text-gray-300 rounded px-1">leaf_photo.jpg</div>
            </div>
            <p className="text-[10px] text-gray-600 text-right mt-1">9:41 AM ✓✓</p>
          </div>
        </div>
        <div className="flex justify-start">
          <div className="bg-emerald-900/40 border border-emerald-500/15 rounded-2xl rounded-tl-sm px-4 py-3 max-w-[80%]">
            <div className="flex items-center gap-2 mb-2 flex-wrap">
              <span className="text-xs font-bold text-emerald-400">🤖 Krish AI</span>
              <span className="text-[10px] bg-red-500/15 text-red-400 rounded-full px-1.5 py-0.5 font-semibold border border-red-500/20">Early Blight Detected</span>
            </div>
            <p className="text-[12px] text-gray-300 leading-relaxed">
              <strong className="text-white">Diagnosis:</strong> Alternaria solani (Early Blight)<br />
              <strong className="text-white">Severity:</strong> Moderate (Stage 2/4)<br />
              <strong className="text-white">Treatment:</strong> Apply Mancozeb 75WP @ 2g/L. Remove infected leaves. Spray in evening.
            </p>
            <p className="text-[10px] text-gray-600 mt-2 text-right">9:41 AM ✓✓</p>
          </div>
        </div>
      </div>
    );
  }
  if (id === 'voice') {
    return (
      <div className="mt-4 space-y-3">
        <div className="flex justify-end">
          <div className="bg-white/8 rounded-2xl rounded-tr-sm px-4 py-3 max-w-[75%]">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-full bg-white/8 flex items-center justify-center text-sm flex-shrink-0">🎤</div>
              <div className="flex items-center gap-0.5 h-8">
                {[3,6,9,5,12,8,4,10,6,7,3,9,5,11,4,8].map((h, i) => (
                  <div key={i} className="w-0.5 bg-gray-500 rounded-full" style={{ height: `${h}px` }} />
                ))}
              </div>
              <span className="text-xs text-gray-500">0:08</span>
            </div>
            <p className="text-[10px] text-gray-600 mt-1 text-right">9:43 AM ✓✓</p>
          </div>
        </div>
        <div className="flex justify-start">
          <div className="bg-emerald-900/40 border border-emerald-500/15 rounded-2xl rounded-tl-sm px-4 py-3 max-w-[85%]">
            <div className="flex items-center gap-2 mb-1.5 flex-wrap">
              <span className="text-xs font-bold text-emerald-400">🤖 Krish AI</span>
              <span className="text-[10px] text-gray-500 italic">Translated from Hinglish</span>
            </div>
            <div className="flex items-center gap-2 mb-2">
              <div className="w-7 h-7 rounded-full bg-emerald-600 flex items-center justify-center text-white text-xs flex-shrink-0">▶</div>
              <div className="flex items-center gap-0.5 h-7">
                {[4,8,6,12,5,9,7,11,4,8,6,10,5,9,3].map((h, i) => (
                  <div key={i} className="w-0.5 bg-emerald-500/60 rounded-full" style={{ height: `${h}px` }} />
                ))}
              </div>
              <span className="text-xs text-gray-500">0:12</span>
            </div>
            <p className="text-[11px] text-gray-400 italic">"Your wheat field shows signs of rust. Apply propiconazole immediately and reduce irrigation for 3 days."</p>
            <p className="text-[10px] text-gray-600 mt-1 text-right">9:43 AM ✓✓</p>
          </div>
        </div>
      </div>
    );
  }
  if (id === 'weather') {
    return (
      <div className="mt-4 space-y-3">
        <div className="flex justify-start">
          <div className="bg-emerald-900/40 border border-emerald-500/15 rounded-2xl rounded-tl-sm px-4 py-3 max-w-[85%]">
            <div className="flex items-center gap-2 mb-2 flex-wrap">
              <span className="text-xs font-bold text-emerald-400">🤖 Krish AI</span>
              <span className="text-[10px] bg-amber-400/15 text-amber-400 rounded-full px-1.5 py-0.5 font-semibold border border-amber-400/20">⚠ Weather Alert</span>
            </div>
            <p className="text-[12px] text-gray-300 leading-relaxed">
              🌧 <strong className="text-white">Rain expected in 24h</strong> (Nashik district, 18–25mm).<br /><br />
              Your scheduled fungicide spray may wash off. <strong className="text-white">Reschedule to tomorrow evening or apply a sticker adjuvant today.</strong>
            </p>
            <div className="mt-2 flex gap-2">
              <button className="text-[11px] text-emerald-400 font-semibold bg-emerald-500/10 rounded-lg px-2 py-1 border border-emerald-500/20">✓ Reschedule</button>
              <button className="text-[11px] text-gray-500 bg-white/5 rounded-lg px-2 py-1 border border-white/10">Dismiss</button>
            </div>
            <p className="text-[10px] text-gray-600 mt-2 text-right">6:00 AM ✓✓</p>
          </div>
        </div>
        <div className="flex justify-start">
          <div className="bg-emerald-900/40 border border-emerald-500/15 rounded-2xl rounded-tl-sm px-4 py-3 max-w-[85%]">
            <p className="text-[12px] text-gray-300">
              📊 <strong className="text-white">Latur Mandi today:</strong><br />
              Soybean: ₹4,820/q (+2.1%) &nbsp;|&nbsp; Cotton: ₹6,150/q (-0.8%)
            </p>
            <p className="text-[10px] text-gray-600 mt-1 text-right">6:01 AM ✓✓</p>
          </div>
        </div>
      </div>
    );
  }
  return null;
};

/* ─── Main ───────────────────────────────────────────────────────────────── */
export const FeatureCards: React.FC<{ cards: FeatureCardItem[] }> = ({ cards }) => {
  const [openId, setOpenId] = useState<string | null>(null);

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      {cards.map((card, i) => {
        const isOpen = openId === card.id;
        return (
          <motion.div
            key={card.id}
            initial={{ opacity: 0, y: 24 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, amount: 0.2 }}
            transition={{ duration: 0.55, delay: i * 0.1, ease: [0.22, 1, 0.36, 1] }}
            whileHover={{ y: -4, scale: 1.015, transition: { duration: 0.25 } }}
            className="glass rounded-2xl overflow-hidden cursor-default"
            style={{ boxShadow: '0 4px 24px rgba(0,0,0,0.4)' }}
          >
            {/* Header */}
            <button
              onClick={() => setOpenId(isOpen ? null : card.id)}
              className="w-full flex items-center gap-3 p-5 text-left cursor-pointer"
            >
              <div className="w-11 h-11 rounded-xl bg-emerald-500/10 flex items-center justify-center text-2xl flex-shrink-0">
                {card.icon}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-0.5 flex-wrap">
                  <span className="font-semibold text-white text-sm" style={{ fontFamily: 'Sora, sans-serif' }}>
                    {card.title}
                  </span>
                  <span className={`text-[10px] font-bold rounded-full px-2 py-0.5 ${
                    card.tag === 'Live'
                      ? 'bg-emerald-400/10 text-emerald-400 border border-emerald-400/25'
                      : 'bg-amber-400/10 text-amber-400 border border-amber-400/25'
                  }`}>
                    {card.tag === 'Live' ? '● Live' : '◌ Roadmap'}
                  </span>
                </div>
                <p className="text-gray-500 text-xs leading-snug">{card.description}</p>
              </div>
              <ChevronDown
                size={16}
                className={`text-gray-600 transition-transform duration-200 flex-shrink-0 ${isOpen ? 'rotate-180' : ''}`}
              />
            </button>

            {/* Expanded */}
            <div className={`transition-all duration-300 ease-in-out overflow-hidden ${isOpen ? 'max-h-[520px] opacity-100' : 'max-h-0 opacity-0'}`}>
              <div className="px-5 pb-5 border-t border-white/6">
                <div className="mt-3 bg-black/30 rounded-xl p-3 border border-white/8">
                  <div className="flex items-center gap-2 mb-3 pb-2 border-b border-white/8">
                    <div className="w-6 h-6 rounded-full bg-emerald-600 flex items-center justify-center text-white text-[10px] font-bold flex-shrink-0">K</div>
                    <span className="text-xs font-semibold text-gray-300">Krish Bot</span>
                    <span className="text-[10px] text-emerald-400 ml-auto">● online</span>
                  </div>
                  <ChatBubbleMock id={card.id} />
                </div>
              </div>
            </div>
          </motion.div>
        );
      })}
    </div>
  );
};
