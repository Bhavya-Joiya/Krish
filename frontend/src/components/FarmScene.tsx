import React from 'react';
import { motion, useScroll, useTransform, useReducedMotion } from 'framer-motion';

// ─── Firefly positions — deterministic (no Math.random in render) ───────────
const FIREFLIES = [
  { id: 0, left: '8%',  bottom: '32%', delay: '0s',   dur: '4.2s', size: 4 },
  { id: 1, left: '22%', bottom: '44%', delay: '1.4s', dur: '5.1s', size: 3 },
  { id: 2, left: '38%', bottom: '37%', delay: '0.7s', dur: '3.8s', size: 5 },
  { id: 3, left: '55%', bottom: '50%', delay: '2.1s', dur: '4.5s', size: 3 },
  { id: 4, left: '70%', bottom: '34%', delay: '0.3s', dur: '5.8s', size: 4 },
  { id: 5, left: '84%', bottom: '40%', delay: '1.8s', dur: '3.5s', size: 3 },
  { id: 6, left: '14%', bottom: '60%', delay: '3.0s', dur: '6.2s', size: 3 },
  { id: 7, left: '47%', bottom: '57%', delay: '2.5s', dur: '4.0s', size: 4 },
  { id: 8, left: '72%', bottom: '64%', delay: '1.1s', dur: '5.5s', size: 3 },
  { id: 9, left: '30%', bottom: '53%', delay: '4.0s', dur: '4.8s', size: 3 },
];

// ─── Farmer SVG silhouette ───────────────────────────────────────────────────
// Gender-neutral figure, wide-brim hat, hoe in mid-work pose.
// Uses path-based anatomy so the bob animation reads as natural motion.
const FarmerSVG: React.FC = () => (
  <svg
    viewBox="0 0 70 115"
    width="70"
    height="115"
    xmlns="http://www.w3.org/2000/svg"
    aria-hidden="true"
  >
    {/* Wide-brim sun hat — brim first so crown layers on top */}
    <ellipse cx="35" cy="20" rx="27" ry="7"   fill="#0F2419" />
    <path d="M16,20 Q35,5 54,20 Z"             fill="#0F2419" />
    {/* Head */}
    <circle cx="35" cy="30" r="11"             fill="#0F2419" />
    {/* Neck */}
    <rect   x="30" y="39" width="10" height="7" rx="2" fill="#0F2419" />
    {/* Torso — loose fabric silhouette */}
    <path d="M14,46 C20,42 50,42 56,46 L52,80 C46,84 24,84 18,80 Z" fill="#0F2419" />
    {/* Left leg (back — stepping back) */}
    <path d="M24,80 C22,93 19,104 16,112"
          stroke="#0F2419" strokeWidth="8" strokeLinecap="round" fill="none"/>
    {/* Right leg (forward — mid-stride) */}
    <path d="M44,80 C48,92 52,103 55,110"
          stroke="#0F2419" strokeWidth="8" strokeLinecap="round" fill="none"/>
    {/* Left arm (lower guide hand on hoe) */}
    <path d="M18,52 C11,63 8,72 7,80"
          stroke="#0F2419" strokeWidth="6" strokeLinecap="round" fill="none"/>
    {/* Right arm (raised, gripping hoe handle) */}
    <path d="M52,48 C59,38 63,28 65,18"
          stroke="#0F2419" strokeWidth="6" strokeLinecap="round" fill="none"/>
    {/* Hoe handle — long diagonal */}
    <line x1="65" y1="16" x2="48" y2="92"
          stroke="#0F2419" strokeWidth="3.5" strokeLinecap="round"/>
    {/* Hoe blade */}
    <path d="M41,90 Q48,97 57,92"
          stroke="#0F2419" strokeWidth="6" strokeLinecap="round" fill="none"/>
    {/* Subtle green highlight for painterly depth */}
    <circle cx="35" cy="30" r="11" fill="#1C4228" opacity="0.22"/>
  </svg>
);

// ─── Star positions (static, sparse) ────────────────────────────────────────
const STARS: [number, number, number][] = [
  [120,75,0.9],[310,52,1.1],[510,38,0.8],[760,28,1.0],[990,48,0.9],[1210,43,1.2],
  [175,118,0.7],[425,98,1.0],[665,82,0.85],[905,108,0.9],[1320,115,1.1],
  [62,158,0.8],[255,143,1.0],[558,128,0.9],[825,153,0.8],[1055,138,1.1],
];

// ─── Main component ──────────────────────────────────────────────────────────
export const FarmScene: React.FC = () => {
  const prefersReduced = useReducedMotion();

  // Full-page scroll progress (0 = top, 1 = bottom)
  const { scrollYProgress } = useScroll();

  // Farmer: left edge 4% → 80% as user scrolls top → bottom
  // 80% cap keeps the 70px-wide figure on-screen even at 375px viewport
  const farmerLeft = useTransform(scrollYProgress, [0, 1], ['4%', '80%']);

  // Horizon warmth: slightly brighter near hero, dims as user scrolls deeper
  const horizonOpacity = useTransform(scrollYProgress, [0, 1], [0.20, 0.07]);

  // Hills: very slight leftward drift for subtle parallax (background moves less)
  const hillsFarX  = useTransform(scrollYProgress, [0, 1], ['0%', '-2%']);
  const hillsNearX = useTransform(scrollYProgress, [0, 1], ['0%', '-4%']);

  return (
    <div
      className="fixed inset-0 z-0 overflow-hidden pointer-events-none select-none"
      aria-hidden="true"
    >
      {/* ── Sky + static scene SVG ──────────────────────────────────────── */}
      <svg
        viewBox="0 0 1440 810"
        preserveAspectRatio="xMidYMid slice"
        className="absolute inset-0 w-full h-full"
        xmlns="http://www.w3.org/2000/svg"
      >
        <defs>
          {/* Dark forest-charcoal sky */}
          <linearGradient id="skyBase" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%"   stopColor="#070C07" />
            <stop offset="40%"  stopColor="#0A1409" />
            <stop offset="70%"  stopColor="#0D1B12" />
            <stop offset="100%" stopColor="#152E1A" />
          </linearGradient>

          {/* Warm amber horizon glow */}
          <radialGradient id="horizonGlow" cx="50%" cy="82%" r="65%">
            <stop offset="0%"   stopColor="#F5B94D" stopOpacity="1" />
            <stop offset="38%"  stopColor="#E07A3A" stopOpacity="0.45"/>
            <stop offset="100%" stopColor="#0D1B12" stopOpacity="0" />
          </radialGradient>

          {/* Soft moonlight ambience top-left */}
          <radialGradient id="moonAmbience" cx="18%" cy="14%" r="32%">
            <stop offset="0%"   stopColor="#B8EFCE" stopOpacity="0.07"/>
            <stop offset="100%" stopColor="#0D1B12" stopOpacity="0" />
          </radialGradient>
        </defs>

        {/* Base sky fill */}
        <rect x="0" y="0" width="1440" height="810" fill="url(#skyBase)" />
        {/* Moon ambience */}
        <rect x="0" y="0" width="1440" height="810" fill="url(#moonAmbience)" />

        {/* Stars */}
        {STARS.map(([x, y, r], i) => (
          <circle key={i} cx={x} cy={y} r={r}
            fill="#C8EED8"
            opacity={0.12 + (i % 4) * 0.05}
          />
        ))}

        {/* Ground plane */}
        <rect x="0" y="718" width="1440" height="92" fill="#0E2416" />
        {/* Ground surface edge highlight */}
        <path
          d="M0,718 C480,708 960,713 1440,706 L1440,726 C960,734 480,728 0,734 Z"
          fill="#183520" opacity="0.65"
        />

        {/* Field rows — perspective ellipses converging to horizon */}
        {[
          { cy: 733, rx: 600, ry: 4,   op: 0.22 },
          { cy: 748, rx: 640, ry: 5,   op: 0.25 },
          { cy: 763, rx: 672, ry: 5.5, op: 0.28 },
          { cy: 779, rx: 700, ry: 6,   op: 0.30 },
          { cy: 795, rx: 720, ry: 6.5, op: 0.33 },
          { cy: 810, rx: 740, ry: 7,   op: 0.35 },
        ].map((r, i) => (
          <ellipse key={i} cx="720" cy={r.cy} rx={r.rx} ry={r.ry}
            fill="#1C4428" opacity={r.op}
          />
        ))}
      </svg>

      {/* ── Scroll-reactive horizon warmth (MotionValue opacity) ── */}
      <motion.div
        className="absolute inset-0"
        style={{
          background: 'radial-gradient(ellipse 90% 52% at 50% 88%, rgba(245,185,77,1) 0%, rgba(224,122,58,0.35) 35%, transparent 70%)',
          opacity: prefersReduced ? 0.13 : horizonOpacity,
        }}
      />

      {/* ── Far hills — very subtle, barely moves (mobile: hidden) ── */}
      <motion.div
        className="absolute inset-0 hidden sm:block"
        style={{ x: prefersReduced ? '0%' : hillsFarX }}
      >
        <svg viewBox="0 0 1440 810" preserveAspectRatio="xMidYMid slice"
             className="w-full h-full" xmlns="http://www.w3.org/2000/svg">
          <path
            d="M-80,575 C120,535 340,518 560,528 C740,536 940,522 1140,528 C1300,533 1410,542 1520,538 L1520,810 L-80,810 Z"
            fill="#0D2018" opacity="0.88"
          />
          {/* Subtle tree-line bumps */}
          {[180,340,520,700,880,1060,1220,1380].map((x, i) => (
            <ellipse key={i} cx={x} cy={525 - (i%3)*8} rx={28 + (i%4)*6} ry={18 + (i%3)*5}
              fill="#0C1E14" opacity="0.65"
            />
          ))}
        </svg>
      </motion.div>

      {/* ── Near hills ── */}
      <motion.div
        className="absolute inset-0"
        style={{ x: prefersReduced ? '0%' : hillsNearX }}
      >
        <svg viewBox="0 0 1440 810" preserveAspectRatio="xMidYMid slice"
             className="w-full h-full" xmlns="http://www.w3.org/2000/svg">
          <path
            d="M-80,652 C100,618 280,605 468,616 C628,625 790,618 950,630 C1090,640 1260,630 1520,638 L1520,810 L-80,810 Z"
            fill="#0F2A1A" opacity="0.94"
          />
          {/* Tree silhouette bumps on ridge */}
          {[220,420,600,780,960,1120,1300].map((x, i) => (
            <ellipse key={i} cx={x} cy={612 - (i%2)*10} rx={20 + (i%3)*8} ry={22 + (i%4)*6}
              fill="#0D2418" opacity="0.80"
            />
          ))}
        </svg>
      </motion.div>

      {/* ── Farmer silhouette — scroll-driven horizontal, time-based bob ── */}
      <motion.div
        className="absolute bottom-[11%] sm:bottom-[13%]"
        style={{ left: prefersReduced ? '40%' : farmerLeft }}
      >
        {/* Walking bob — y oscillation layered on top of scroll-driven x */}
        <motion.div
          className="origin-bottom"
          animate={prefersReduced ? undefined : {
            y:      [0, -4, -1, -4, 0],
            rotate: [-1, 0.4, -0.4, 0.8, -1],
          }}
          transition={{
            duration: 0.86,
            repeat:   Infinity,
            ease:     'easeInOut',
          }}
        >
          {/* Scale down on mobile so figure fits narrow viewport */}
          <div className="scale-[0.72] sm:scale-90 md:scale-100 origin-bottom-left">
            <FarmerSVG />
          </div>
        </motion.div>
      </motion.div>

      {/* ── Fireflies (desktop only, scroll-independent drift) ── */}
      {!prefersReduced && FIREFLIES.map((ff) => (
        <div
          key={ff.id}
          className="absolute rounded-full hidden md:block"
          style={{
            left:      ff.left,
            bottom:    ff.bottom,
            width:     `${ff.size}px`,
            height:    `${ff.size}px`,
            background:'#F5B94D',
            boxShadow: `0 0 ${ff.size * 3}px ${ff.size * 1.5}px rgba(245,185,77,0.38)`,
            animation: `fireflyFloat ${ff.dur} ${ff.delay} ease-in-out infinite`,
          }}
        />
      ))}

      {/* ── Global dark veil — keeps cards readable across entire page ── */}
      {/* Very subtle, just enough to ensure contrast on top of scene */}
      <div
        className="absolute inset-0"
        style={{
          background: 'linear-gradient(to bottom, rgba(0,0,0,0.08) 0%, rgba(0,0,0,0.18) 40%, rgba(0,0,0,0.28) 100%)',
        }}
      />
    </div>
  );
};
