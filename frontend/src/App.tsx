import React, { useEffect, useState } from 'react';
import './index.css';
import { motion } from 'framer-motion';
import { SplashScreen } from './components/SplashScreen';
import { Hero } from './components/Hero';
import { WhyKrish } from './components/WhyKrish';
import { StatStrip } from './components/StatStrip';
import { FeatureCards } from './components/FeatureCards';
import { SystemArchitecture } from './components/SystemArchitecture';

import { Footer } from './components/Footer';
import { GrassScene } from './components/GrassScene';
import type { StatCardData, ChannelData } from './types';
import { apiUrl, resolveHref } from './api';

const STATS: StatCardData[] = [
  { label: 'Total Conversations Handled', value: '1,284,912', icon: 'camera' },
  { label: 'Active Users This Week', value: '12,480', icon: 'users', trend: '+8% this week' },
  { label: 'Avg. Diagnosis Response Time', value: '12.4 sec', icon: 'clock' },
  { label: 'Uptime', value: '99.6%', icon: 'signal', badge: 'All systems operational' },
];

const FEATURES = [
  { id: 'photo', icon: '📸', title: 'Photo Diagnosis', description: 'Snap a leaf — get instant AI-powered crop disease detection.', tag: 'Live' as const },
  { id: 'voice', icon: '🎙', title: 'Voice Query', description: 'Speak in Hindi or Hinglish — bot replies in your language.', tag: 'Live' as const },
  { id: 'weather', icon: '🌧', title: 'Weather & Mandi Alerts', description: 'Proactive rain, frost, and market price alerts for your district.', tag: 'Live' as const },
];

/** Shown until /api/channels responds (or if backend is down). */
const FALLBACK_CHANNELS: ChannelData[] = [
  {
    id: 'telegram',
    name: 'Telegram Bot',
    icon: 'telegram',
    status: 'offline',
    meta1: 'Photo · voice · text · weather · mandi',
    meta2: 'Start the API to resolve your bot link',
    href: null,
    actionLabel: 'Bot offline',
    disabled: true,
    note: 'Backend not reachable. Run uvicorn on port 8000, then refresh.',
  },
  {
    id: 'fallback',
    name: 'Fallback Web Chat',
    icon: 'fallback',
    status: 'connected',
    meta1: 'Text + image URL + location — same AI pipeline',
    meta2: 'Voice available via Telegram only',
    href: resolveHref('/chat'),
    actionLabel: 'Open Web Chat',
    disabled: false,
    note: 'Opens the FastAPI /chat backup (same origin, or Render when on Vercel).',
  },
  {
    id: 'sms',
    name: 'SMS',
    icon: 'sms',
    status: 'pending',
    meta1: 'Text-only advisory — not wired yet',
    meta2: 'Coming soon',
    href: null,
    actionLabel: 'Coming soon',
    disabled: true,
    note: 'SMS channel is planned but not built for this demo.',
  },
];

const SectionLabel: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <motion.p
    className="text-xs font-bold text-emerald-400/65 uppercase tracking-widest mb-3"
    style={{ fontFamily: 'Sora, sans-serif' }}
    initial={{ opacity: 0, y: 12 }}
    whileInView={{ opacity: 1, y: 0 }}
    viewport={{ once: true, amount: 0.5 }}
    transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
  >
    {children}
  </motion.p>
);

function App() {
  const [splashDone, setSplashDone] = useState<boolean>(() => {
    try {
      return sessionStorage.getItem('krish_splash_done') === '1';
    } catch {
      return false;
    }
  });
  const [channels, setChannels] = useState<ChannelData[]>(FALLBACK_CHANNELS);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const res = await fetch(apiUrl('/api/channels'));
        if (!res.ok) return;
        const data = await res.json();
        if (cancelled || !Array.isArray(data.channels)) return;
        const next = (data.channels as ChannelData[]).map((ch) => ({
          ...ch,
          href: resolveHref(ch.href) ?? ch.href,
        }));
        setChannels(next);
      } catch {
        // keep FALLBACK_CHANNELS
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const handleSplashDone = () => {
    try {
      sessionStorage.setItem('krish_splash_done', '1');
    } catch {}
    setSplashDone(true);
  };

  return (
    <div className="relative min-h-screen bg-[#0A0E0A] text-gray-300 overflow-x-hidden">
      <GrassScene />

      <div
        className="fixed inset-0 z-[1] pointer-events-none"
        style={{
          background:
            'linear-gradient(to bottom, rgba(0,0,0,0.22) 0%, rgba(0,0,0,0.32) 45%, rgba(0,0,0,0.50) 100%)',
        }}
      />

      <div className="relative z-10">
        {!splashDone && <SplashScreen onDone={handleSplashDone} />}

        <Hero channels={channels} splashDone={splashDone} />

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="h-px bg-white/6" />
        </div>

        <main className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 space-y-16">
          <div>
            <SectionLabel>The Problem We Solve</SectionLabel>
            <WhyKrish />
          </div>

          <div>
            <SectionLabel>System Metrics</SectionLabel>
            <StatStrip cards={STATS} />
          </div>

          <div>
            <SectionLabel>Feature Demos</SectionLabel>
            <FeatureCards cards={FEATURES} />
          </div>

          <div>
            <SectionLabel>System Architecture</SectionLabel>
            <SystemArchitecture />
          </div>
        </main>

        <Footer />
      </div>
    </div>
  );
}

export default App;
