import React, { useEffect, useRef } from 'react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { usePrefersReducedMotion } from '../hooks/usePrefersReducedMotion';

gsap.registerPlugin(ScrollTrigger);

interface ScrubSectionProps {
  children: React.ReactNode;
  className?: string;
}

export const ScrubSection: React.FC<ScrubSectionProps> = ({ children, className }) => {
  const ref = useRef<HTMLDivElement>(null);
  const reduced = usePrefersReducedMotion();

  useEffect(() => {
    const el = ref.current;
    if (!el || reduced) return;

    gsap.set(el, { opacity: 0.28, y: 36, filter: 'blur(8px)' });

    const st = ScrollTrigger.create({
      trigger: el,
      start: 'top 92%',
      end: 'top 48%',
      scrub: 0.85,
      onUpdate: (self) => {
        const p = self.progress;
        gsap.set(el, {
          opacity: 0.28 + p * 0.72,
          y: (1 - p) * 36,
          filter: `blur(${(1 - p) * 8}px)`,
        });
      },
    });

    return () => {
      st.kill();
      gsap.set(el, { clearProps: 'opacity,transform,filter' });
    };
  }, [reduced]);

  return (
    <div ref={ref} className={className}>
      {children}
    </div>
  );
};
