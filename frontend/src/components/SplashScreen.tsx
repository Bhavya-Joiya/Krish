import React, { useEffect, useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';

interface SplashScreenProps {
  onDone: () => void;
}

export const SplashScreen: React.FC<SplashScreenProps> = ({ onDone }) => {
  const [visible, setVisible] = useState(true);

  useEffect(() => {
    // text in ~0.8s, hold 0.8s, then fade out 0.8s → total ~2.4s
    const exitTimer = setTimeout(() => setVisible(false), 1800);
    const doneTimer = setTimeout(() => onDone(), 2700);  // after exit animation completes
    return () => { clearTimeout(exitTimer); clearTimeout(doneTimer); };
  }, [onDone]);

  const handleSkip = () => {
    setVisible(false);
    setTimeout(() => onDone(), 700);
  };

  return (
    <AnimatePresence>
      {visible && (
        <motion.div
          key="splash"
          className="splash-overlay"
          initial={{ opacity: 1 }}
          exit={{ opacity: 0, filter: 'blur(12px)', scale: 1.04 }}
          transition={{ duration: 0.75, ease: 'easeInOut' }}
          onClick={handleSkip}
        >
          {/* "Krish" text */}
          <motion.div
            initial={{ opacity: 0, scale: 0.86, filter: 'blur(8px)' }}
            animate={{ opacity: 1, scale: 1, filter: 'blur(0px)' }}
            transition={{ duration: 0.75, ease: [0.22, 1, 0.36, 1] }}
            className="flex flex-col items-center gap-4 select-none"
          >
            <div className="w-16 h-16 rounded-2xl border border-emerald-500/25 bg-emerald-500/8 flex items-center justify-center">
              <span className="text-4xl">🌱</span>
            </div>
            <h1
              className="text-7xl font-bold text-white tracking-tight"
              style={{ fontFamily: 'Sora, sans-serif' }}
            >
              Krish
            </h1>
            <p className="text-emerald-400/60 text-xs tracking-[0.25em] uppercase font-medium">
              AI Crop Advisory
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
