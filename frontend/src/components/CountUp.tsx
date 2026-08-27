import React, { useEffect, useRef, useState } from 'react';
import { usePrefersReducedMotion } from '../hooks/usePrefersReducedMotion';

function parseStat(raw: string) {
  const match = raw.match(/^([0-9][0-9,]*(?:\.[0-9]+)?)(.*)$/);
  if (!match) return { target: 0, suffix: raw, decimals: 0, commas: false };
  const numStr = match[1];
  const suffix = match[2];
  const commas = numStr.includes(',');
  const decimals = (numStr.split('.')[1] || '').length;
  const target = parseFloat(numStr.replace(/,/g, ''));
  return { target, suffix, decimals, commas };
}

function formatStat(n: number, decimals: number, commas: boolean, suffix: string) {
  const fixed = n.toFixed(decimals);
  if (!commas) return `${fixed}${suffix}`;
  const [intPart, frac] = fixed.split('.');
  const withCommas = intPart.replace(/\B(?=(\d{3})+(?!\d))/g, ',');
  return `${frac !== undefined ? `${withCommas}.${frac}` : withCommas}${suffix}`;
}

interface CountUpProps {
  value: string;
  active?: boolean;
  duration?: number;
  className?: string;
  style?: React.CSSProperties;
}

export const CountUp: React.FC<CountUpProps> = ({
  value,
  active = true,
  duration = 1.6,
  className,
  style,
}) => {
  const reduced = usePrefersReducedMotion();
  const { target, suffix, decimals, commas } = parseStat(value);
  const [display, setDisplay] = useState(() =>
    reduced || !active ? value : formatStat(0, decimals, commas, suffix),
  );
  const started = useRef(false);

  useEffect(() => {
    if (!active || started.current || reduced) {
      setDisplay(value);
      return;
    }
    started.current = true;
    const start = performance.now();
    const ms = duration * 1000;
    let raf = 0;

    const tick = (now: number) => {
      const t = Math.min(1, (now - start) / ms);
      const eased = 1 - Math.pow(1 - t, 3);
      setDisplay(formatStat(target * eased, decimals, commas, suffix));
      if (t < 1) raf = requestAnimationFrame(tick);
      else setDisplay(value);
    };

    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [active, commas, decimals, duration, reduced, suffix, target, value]);

  return (
    <span className={className} style={style}>
      {display}
    </span>
  );
};
