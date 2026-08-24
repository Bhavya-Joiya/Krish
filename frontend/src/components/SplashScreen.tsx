import React, { useEffect, useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { SeedlingIcon } from './Hero';

interface SplashScreenProps {
  onDone: () => void;
  /** When true the splash begins its exit animation (driven by GrassScene's first frame). */
  sceneReady?: boolean;
}

export const SplashScreen: React.FC<SplashScreenProps> = ({ onDone, sceneReady }) => {
  const [visible, setVisible] = useState(true);

  // Exit triggered by real scene readiness (not a fixed timer)
  useEffect(() => {
    if (!sceneReady) return;
    setVisible(false);
    // Allow the exit animation to complete before calling onDone
    const doneTimer = setTimeout(() => onDone(), 750);
    return () => clearTimeout(doneTimer);
  }, [sceneReady, onDone]);

  const handleSkip = () => {
    setVisible(false);
    setTimeout(() => onDone(), 700);
  };

  return (
    <AnimatePresence>
      {visible && (
        <motion.div
          key="splash"
          className="splash-overlay digital-dawn-bg"
          initial={{ opacity: 1 }}
          exit={{ opacity: 0, filter: 'blur(8px)', scale: 1.02 }}
          transition={{ duration: 0.75, ease: 'easeInOut' }}
          onClick={handleSkip}
        >
          {/* Ambient golden glow bloom — mirrors the Hero dawn glow behind the wordmark */}
          <div
            className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-64 pointer-events-none rounded-full blur-3xl"
            style={{
              background:
                'radial-gradient(circle at 50% 50%, rgba(232,185,95,0.28) 0%, rgba(200,129,26,0.10) 50%, transparent 70%)',
            }}
          />

          {/* Main content */}
          <motion.div
            initial={{ opacity: 0, scale: 0.86, filter: 'blur(8px)' }}
            animate={{ opacity: 1, scale: 1, filter: 'blur(0px)' }}
            transition={{ duration: 0.75, ease: [0.22, 1, 0.36, 1] }}
            className="flex flex-col items-center gap-5 select-none relative z-10"
          >
            {/* Hero-style "AI CROP ADVISORY" pill badge */}
            <div className="inline-flex items-center gap-2 glass rounded-full px-4 py-1.5 border border-krish-ochre/25 shadow-lg">
              <motion.div
                animate={{ rotate: [-6, 6, -6] }}
                transition={{ duration: 4, repeat: Infinity, ease: 'easeInOut' }}
              >
                <SeedlingIcon className="w-4 h-4 text-krish-ochre" />
              </motion.div>
              <span
                className="text-xs font-semibold text-krish-wheat tracking-[0.2em] uppercase"
                style={{ fontFamily: 'var(--font-heading)' }}
              >
                AI Crop Advisory
              </span>
              <span className="w-1.5 h-1.5 rounded-full bg-krish-ochre animate-ping ml-1" />
            </div>

            {/* "Krish" wordmark — exact match to Hero typography */}
            <h1
              className="text-7xl sm:text-8xl font-semibold italic text-krish-wheat leading-none tracking-wide"
              style={{ fontFamily: 'var(--font-display, "Libre Baskerville", Georgia, serif)' }}
            >
              Krish
            </h1>

            {/* Tagline */}
            <p className="text-gray-400 text-sm tracking-widest font-light mt-1">
              Your Farm's AI Advisor
            </p>
          </motion.div>

          {/* Skip hint */}
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.9, duration: 0.4 }}
            className="absolute bottom-8 text-white/20 text-xs tracking-widest"
          >
            tap to skip
          </motion.p>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

