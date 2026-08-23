import React from 'react';
import { motion } from 'framer-motion';
import { Download, Languages, Bell, Tractor } from 'lucide-react';

const benefits = [
  {
    icon: <Download size={20} strokeWidth={1.8} />,
    title: 'Zero new app to install',
    desc: 'Works inside Telegram (and Web Chat backup) — no signup, no new app to learn.',
    iconBg: 'bg-emerald-500/12 text-emerald-400',
    floatPhase: 0,
  },
  {
    icon: <Languages size={20} strokeWidth={1.8} />,
    title: 'Speaks your language',
    desc: 'Voice and text replies in Hindi, Hinglish, and English — seamlessly.',
    iconBg: 'bg-amber-400/12 text-amber-400',
    floatPhase: 1,
  },
  {
    icon: <Bell size={20} strokeWidth={1.8} />,
    title: 'Reactive today, proactive tomorrow',
    desc: 'Warns before damage happens — rain alerts, frost advisories, spray-timing reminders.',
    iconBg: 'bg-emerald-500/12 text-emerald-400',
    floatPhase: 2,
  },
  {
    icon: <Tractor size={20} strokeWidth={1.8} />,
    title: 'Built for all farmers',
    desc: "Designed for low-literacy, low-connectivity users — not just tech-savvy ones.",
    iconBg: 'bg-amber-400/12 text-amber-400',
    floatPhase: 3,
  },
];

// Subtle floating keyframes for y — each card starts at a different phase
const floatY = [
  [0, -5, 0, 5, 0],
  [0, 4, 0, -4, 0],
  [0, -4, 0, 4, 0],
  [0, 5, 0, -5, 0],
];

const cardVariants = {
  hidden: { opacity: 0, y: 24 },
  show: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: { duration: 0.6, delay: i * 0.1, ease: [0.22, 1, 0.36, 1] as const },
  }),
};

export const WhyKrish: React.FC = () => {
  return (
    <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div className="glass rounded-3xl p-8 sm:p-10 glow-em">
        {/* Heading */}
        <motion.div
          className="mb-8"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.3 }}
          transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
        >
          <p className="text-xs font-bold text-emerald-400/50 uppercase tracking-widest mb-2">
            The Problem We Solve
          </p>
          <h2
            className="text-2xl sm:text-3xl font-bold text-white"
            style={{ fontFamily: 'Sora, sans-serif' }}
          >
            Why{' '}
            <span className="grad-text">Krish?</span>
          </h2>
        </motion.div>

        {/* 2×2 grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {benefits.map((b, i) => (
            <motion.div
              key={i}
              custom={i}
              variants={cardVariants}
              initial="hidden"
              whileInView="show"
              viewport={{ once: true, amount: 0.2 }}
              // Continuous floating orbit
              animate={{ y: floatY[i] }}
              transition={
                // Need to keep the whileInView transition separate
                // Framer Motion merges — we use the animate transition for orbit
                { y: { duration: 7 + i * 1.2, repeat: Infinity, ease: 'easeInOut', delay: i * 1.5 } }
              }
              whileHover={{ y: 0, scale: 1.02, transition: { duration: 0.3 } }}
              className="flex items-start gap-4 p-4 rounded-2xl bg-white/4 border border-white/8 hover:border-emerald-500/25 hover:bg-emerald-500/5 transition-colors cursor-default"
              style={{
                boxShadow: '0 2px 16px rgba(0,0,0,0.3)',
              }}
            >
              {/* Icon */}
              <div className={`w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 ${b.iconBg}`}>
                {b.icon}
              </div>
              {/* Text */}
              <div>
                <p
                  className="font-semibold text-white text-sm leading-snug"
                  style={{ fontFamily: 'Sora, sans-serif' }}
                >
                  {b.title}
                </p>
                <p className="text-gray-400 text-xs mt-1 leading-relaxed">{b.desc}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};
