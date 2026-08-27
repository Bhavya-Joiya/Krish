import React from 'react';
import { AnimatePresence, motion } from 'framer-motion';

interface PageCurtainProps {
  show: boolean;
}

/** Reusable curtain-wipe for future route changes; currently used after splash. */
export const PageCurtain: React.FC<PageCurtainProps> = ({ show }) => (
  <AnimatePresence>
    {show && (
      <motion.div
        key="curtain"
        className="page-curtain"
        initial={{ scaleY: 1 }}
        animate={{ scaleY: 1 }}
        exit={{ scaleY: 0 }}
        transition={{ duration: 0.85, ease: [0.76, 0, 0.24, 1] }}
        style={{ transformOrigin: 'top' }}
        aria-hidden="true"
      />
    )}
  </AnimatePresence>
);
