import React, { useEffect, useState } from 'react';
import { motion, useMotionValue, useSpring } from 'framer-motion';
import { usePrefersReducedMotion } from '../hooks/usePrefersReducedMotion';

export const CustomCursor: React.FC = () => {
  const reduced = usePrefersReducedMotion();
  const [enabled, setEnabled] = useState(false);
  const [hovering, setHovering] = useState(false);

  // Dot — tight spring
  const mx = useMotionValue(-100);
  const my = useMotionValue(-100);
  const dotX = useSpring(mx, { stiffness: 520, damping: 30, mass: 0.28 });
  const dotY = useSpring(my, { stiffness: 520, damping: 30, mass: 0.28 });

  // Aura ring — sluggish spring (trails behind)
  const auraX = useSpring(mx, { stiffness: 120, damping: 22, mass: 0.6 });
  const auraY = useSpring(my, { stiffness: 120, damping: 22, mass: 0.6 });

  useEffect(() => {
    const fine = window.matchMedia('(pointer: fine)').matches;
    if (!fine || reduced) return;
    setEnabled(true);
    document.documentElement.classList.add('has-custom-cursor');

    const onMove = (e: MouseEvent) => {
      mx.set(e.clientX);
      my.set(e.clientY);
    };

    const onOver = (e: MouseEvent) => {
      const t = e.target as HTMLElement | null;
      const hit = t?.closest('a, button, [data-cursor="hover"], [role="button"]');
      setHovering(Boolean(hit));
    };

    window.addEventListener('mousemove', onMove, { passive: true });
    window.addEventListener('mouseover', onOver, { passive: true });

    return () => {
      document.documentElement.classList.remove('has-custom-cursor');
      window.removeEventListener('mousemove', onMove);
      window.removeEventListener('mouseover', onOver);
    };
  }, [mx, my, reduced]);

  if (!enabled) return null;

  return (
    <>
      {/* Trailing aura ring */}
      <motion.div
        className={`custom-cursor-aura${hovering ? ' custom-cursor-aura--hover' : ''}`}
        style={{ x: auraX, y: auraY }}
        aria-hidden="true"
      />
      {/* Tight dot */}
      <motion.div
        className={`custom-cursor${hovering ? ' custom-cursor--hover' : ''}`}
        style={{ x: dotX, y: dotY }}
        aria-hidden="true"
      />
    </>
  );
};
