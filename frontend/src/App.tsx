import React, { useCallback, useEffect, useRef, useState } from 'react';
import './index.css';
import { motion } from 'framer-motion';
import { SplashScreen } from './components/SplashScreen';
import { Hero } from './components/Hero';
import { WhyKrish } from './components/WhyKrish';
import { FeatureCards } from './components/FeatureCards';
import { SystemArchitecture } from './components/SystemArchitecture';
import { CustomCursor } from './components/CustomCursor';
import { GrainOverlay } from './components/GrainOverlay';
import { Footer } from './components/Footer';
import { GrassScene } from './components/GrassScene';
import type { ChannelData } from './types';
import { apiUrl, resolveHref } from './api';

const FEATURES = [
  { id: 'photo', icon: 'camera', title: 'Photo Diagnosis', description: 'Snap a leaf — get instant AI-powered crop disease detection.', tag: 'Live' as const },
  { id: 'voice', icon: 'mic', title: 'Voice Query', description: 'Speak in Hindi or Hinglish — bot replies in your language.', tag: 'Live' as const },
  { id: 'weather', icon: 'cloud-rain', title: 'Weather & Mandi Alerts', description: 'Proactive rain, frost, and market price alerts for your district.', tag: 'Live' as const },
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
  <motion.div
    className="inline-flex items-center gap-2 mb-3"
    initial={{ opacity: 0, x: -14 }}
    whileInView={{ opacity: 1, x: 0 }}
    viewport={{ once: true, amount: 0.5 }}
    transition={{ duration: 0.55, ease: [0.22, 1, 0.36, 1] }}
  >
    <span className="w-1.5 h-1.5 rounded-full bg-krish-ochre animate-ping" />
    <p
      className="text-xs font-bold text-krish-ochre/85 uppercase tracking-widest"
      style={{ fontFamily: 'var(--font-heading)' }}
    >
      {children}
    </p>
  </motion.div>
);

function App() {
  const [splashDone, setSplashDone] = useState<boolean>(() => {
    try {
      return sessionStorage.getItem('krish_splash_done') === '1';
    } catch {
      return false;
    }
  });
  const [sceneReady, setSceneReady] = useState(false);
  /** Timestamp (ms) captured at first render — used to enforce the 800ms minimum floor. */
  const splashStartRef = useRef<number>(Date.now());
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

  /**
   * Called by GrassScene after its first GPU frame renders.
   * Respects an 800ms minimum display floor so fast loads don't flash.
   */
  const handleSceneReady = useCallback(() => {
    const elapsed = Date.now() - splashStartRef.current;
    const remaining = Math.max(0, 1500 - elapsed);
    setTimeout(() => setSceneReady(true), remaining);
  }, []);

  /**
   * Hard-fallback: force sceneReady=true after 5500ms in case WebGL fails
   * (shader compile error, context lost, etc.) so the splash always exits.
   */
  useEffect(() => {
    if (splashDone) return; // skip if splash already bypassed via sessionStorage
    const fallback = setTimeout(() => setSceneReady(true), 5500);
    return () => clearTimeout(fallback);
  }, [splashDone]);

  const handleSplashDone = () => {
    try {
      sessionStorage.setItem('krish_splash_done', '1');
    } catch {}
    setSplashDone(true);
  };

  return (
    <div className="relative min-h-screen bg-[#0A0E0A] text-gray-300 overflow-x-hidden selection:bg-krish-ochre/30 selection:text-krish-wheat">
      <CustomCursor />
      <GrainOverlay />

      {/* Dedicated Viewport-Pinned Digital Dawn Sky Background */}
      <div className="fixed inset-0 z-0 digital-dawn-bg pointer-events-none" />

      {/* Three.js 3D Grass Scene — passes onReady only while splash is active */}
      <GrassScene onReady={!splashDone ? handleSceneReady : undefined} />

      <div className="relative z-10">
        {!splashDone && <SplashScreen onDone={handleSplashDone} sceneReady={sceneReady} />}

        <Hero channels={channels} splashDone={splashDone} />

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ scaleX: 0 }}
            whileInView={{ scaleX: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 1, ease: [0.22, 1, 0.36, 1] }}
            className="h-px bg-gradient-to-r from-transparent via-krish-clay/40 to-transparent origin-center"
          />
        </div>

        <main className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 space-y-20">
          <motion.section
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, amount: 0.15 }}
            transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
          >
            <SectionLabel>The Problem We Solve</SectionLabel>
            <WhyKrish />
          </motion.section>

          <motion.section
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, amount: 0.15 }}
            transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
          >
            <SectionLabel>Feature Demos</SectionLabel>
            <FeatureCards cards={FEATURES} />
          </motion.section>

          <motion.section
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, amount: 0.15 }}
            transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
          >
            <SectionLabel>System Architecture</SectionLabel>
            <SystemArchitecture />
          </motion.section>
        </main>

        <Footer />
      </div>
    </div>
  );
}

export default App;