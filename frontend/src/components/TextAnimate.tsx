import React from 'react';
import { motion } from 'framer-motion';
import { usePrefersReducedMotion } from '../hooks/usePrefersReducedMotion';

interface WordRevealProps {
  children: string;
  className?: string;
  delay?: number;
  stagger?: number;
  duration?: number;
  style?: React.CSSProperties;
}

/**
 * Splits text into words and animates them with a 3D mask reveal.
 */
export const WordReveal: React.FC<WordRevealProps> = ({
  children,
  className = '',
  delay = 0,
  stagger = 0.05,
  duration = 0.65,
  style,
}) => {
  const reduced = usePrefersReducedMotion();
  const words = children.split(' ');

  if (reduced) {
    return <span className={className} style={style}>{children}</span>;
  }

  const container = {
    hidden: {},
    visible: {
      transition: {
        staggerChildren: stagger,
        delayChildren: delay,
      },
    },
  };

  const wordVariant = {
    hidden: {
      opacity: 0,
      y: '105%',
      rotateX: -20,
      filter: 'blur(3px)',
    },
    visible: {
      opacity: 1,
      y: '0%',
      rotateX: 0,
      filter: 'blur(0px)',
      transition: {
        duration,
        ease: [0.22, 1, 0.36, 1] as const,
      },
    },
  };

  return (
    <motion.span
      className={`inline-block ${className}`}
      style={{ perspective: 600, ...style }}
      variants={container}
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true, amount: 0.2 }}
    >
      {words.map((word, i) => (
        <span key={i} className="inline-block overflow-hidden py-1 mr-[0.28em] last:mr-0 align-baseline">
          <motion.span
            className="inline-block origin-bottom"
            variants={wordVariant}
          >
            {word}
          </motion.span>
        </span>
      ))}
    </motion.span>
  );
};

interface CharStaggerProps {
  text: string;
  className?: string;
  delay?: number;
  style?: React.CSSProperties;
}

/**
 * Letter-by-letter spring animation for high-impact keywords.
 */
export const CharStagger: React.FC<CharStaggerProps> = ({
  text,
  className = '',
  delay = 0,
  style,
}) => {
  const reduced = usePrefersReducedMotion();

  if (reduced) {
    return <span className={className} style={style}>{text}</span>;
  }

  return (
    <motion.span
      className={`inline-flex ${className}`}
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true }}
      transition={{ staggerChildren: 0.04, delayChildren: delay }}
      style={style}
    >
      {Array.from(text).map((char, index) => (
        <motion.span
          key={index}
          variants={{
            hidden: { opacity: 0, y: 16, scale: 0.8 },
            visible: {
              opacity: 1,
              y: 0,
              scale: 1,
              transition: {
                type: 'spring',
                damping: 14,
                stiffness: 240,
              },
            },
          }}
          className="inline-block"
        >
          {char === ' ' ? '\u00A0' : char}
        </motion.span>
      ))}
    </motion.span>
  );
};