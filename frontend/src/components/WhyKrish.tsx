import React from 'react';
import { motion } from 'framer-motion';
import { Download, Languages, Bell, Tractor } from 'lucide-react';
import { WordReveal } from './TextAnimate';
import { TiltCard } from './TiltCard';

const benefits = [
  {
    icon: <Download size={20} strokeWidth={1.8} />,
    title: 'Zero new app to install',
    desc: 'Works inside Telegram, WhatsApp, and Web Chat — no signup, no new app to learn.',
    iconBg: 'bg-krish-neem/20 border-krish-neem/30 text-krish-wheat',
  },
  {
    icon: <Languages size={20} strokeWidth={1.8} />,
    title: 'Speaks your language',
    desc: 'Voice and text replies in Hindi, Hinglish, and English — seamlessly.',
    iconBg: 'bg-krish-ochre/20 border-krish-ochre/30 text-krish-wheat',
  },
  {
    icon: <Bell size={20} strokeWidth={1.8} />,
    title: 'Reactive today, proactive tomorrow',
    desc: 'Warns before damage happens — rain alerts, frost advisories, spray-timing reminders.',
    iconBg: 'bg-krish-neem/20 border-krish-neem/30 text-krish-wheat',
  },
  {
    icon: <Tractor size={20} strokeWidth={1.8} />,
    title: 'Built for all farmers',
    desc: "Designed for low-literacy, low-connectivity users — not just tech-savvy ones.",
    iconBg: 'bg-krish-ochre/20 border-krish-ochre/30 text-krish-wheat',
  },
];

const containerVariants = {
  hidden: {},
  show: {
    transition: {
      staggerChildren: 0.12,
    },
  },
};

const cardVariants = {
  hidden: { opacity: 0, y: 28, scale: 0.96 },
  show: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: { duration: 0.65, ease: [0.22, 1, 0.36, 1] as const },
  },
};

export const WhyKrish: React.FC = () => {
  return (
    <section className="max-w-7xl mx-auto relative rounded-3xl border border-krish-clay/20 bg-[#140F0A]/95 overflow-hidden shadow-2xl">
      {/* Subtle soil stripes texture overlay */}
      <div className="absolute inset-0 soil-stripes pointer-events-none" />

      <div className="relative z-10 p-8 sm:p-10">
        {/* Heading */}
        <div className="mb-8">
          <motion.p
            initial={{ opacity: 0, x: -12 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5 }}
            className="text-xs font-bold text-krish-ochre/80 uppercase tracking-widest mb-2 flex items-center gap-2"
            style={{ fontFamily: 'var(--font-heading)' }}
          >
            <span>The Problem We Solve</span>
            <span className="h-px w-8 bg-krish-ochre/40 inline-block" />
          </motion.p>

          <h2
            className="text-2xl sm:text-3xl font-bold text-white flex items-center gap-2 flex-wrap"
            style={{ fontFamily: 'var(--font-display)', fontStyle: 'italic' }}
          >
            <WordReveal delay={0.1} duration={0.6}>
              Why
            </WordReveal>
            <span className="text-krish-wheat text-shimmer not-italic inline-block">
              <WordReveal delay={0.25} duration={0.6}>
                Krish?
              </WordReveal>
            </span>
          </h2>
        </div>

        {/* 2×2 grid with Tilt & Spotlight Cards */}
        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="show"
          viewport={{ once: true, amount: 0.15 }}
          className="grid grid-cols-1 sm:grid-cols-2 gap-4"
        >
          {benefits.map((b, i) => (
            <motion.div key={i} variants={cardVariants}>
              <TiltCard
                maxTilt={6}
                glow
                className="h-full rounded-2xl bg-krish-soil/25 border border-krish-clay/20 hover:border-krish-ochre/45 hover:bg-krish-ochre/10 transition-colors p-5 shadow-lg"
              >
                <div className="flex items-start gap-4">
                  <motion.div
                    whileHover={{ scale: 1.15, rotate: 6 }}
                    transition={{ type: 'spring', stiffness: 350, damping: 15 }}
                    className={`w-11 h-11 rounded-xl border flex items-center justify-center flex-shrink-0 shadow-md ${b.iconBg}`}
                  >
                    {b.icon}
                  </motion.div>
                  <div>
                    <p className="font-semibold text-white text-sm leading-snug group-hover:text-krish-wheat transition-colors"
                       style={{ fontFamily: 'var(--font-heading)' }}>
                      {b.title}
                    </p>
                    <p className="text-gray-400 text-xs mt-1.5 leading-relaxed">{b.desc}</p>
                  </div>
                </div>
              </TiltCard>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
};