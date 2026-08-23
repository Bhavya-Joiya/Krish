import React from 'react';

export const Footer: React.FC = () => {
  return (
    <footer className="relative mt-20 border-t border-white/6">
      {/* Subtle gradient */}
      <div className="absolute inset-0 bg-gradient-to-b from-transparent to-black/40 pointer-events-none" />

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="flex flex-col md:flex-row items-center justify-between gap-8">
          {/* Logo */}
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center">
              <span className="text-2xl">🌱</span>
            </div>
            <div>
              <p className="text-white font-bold text-lg" style={{ fontFamily: 'Sora, sans-serif' }}>Krish</p>
              <p className="text-gray-400 text-xs">AI-Powered Crop Advisory Bot</p>
            </div>
          </div>

          {/* Center */}
          <div className="text-center">
            <p className="text-gray-400 text-sm">
              Built for{' '}
              <span className="grad-text font-semibold">Indian farmers</span>
              {' '}— Telegram · Web Chat · SMS (soon)
            </p>
            <p className="text-gray-500 text-xs mt-1">Hindi · Hinglish · English support</p>
          </div>

          {/* Version */}
          <div className="flex flex-col items-center md:items-end gap-1">
            <div className="flex items-center gap-2">
              <span className="text-[10px] text-gray-500 uppercase tracking-widest">Version</span>
              <code
                className="text-emerald-400 text-xs bg-emerald-400/8 border border-emerald-400/20 rounded px-2 py-0.5"
                style={{ fontFamily: 'JetBrains Mono, monospace' }}
              >
                v1.0.0-mvp
              </code>
            </div>
            <p className="text-gray-500 text-xs">Hackathon Demo · Team Krish · 2026</p>
          </div>
        </div>

        {/* Bottom bar */}
        <div className="mt-10 pt-6 border-t border-white/6 flex flex-col sm:flex-row items-center justify-between gap-3">
          <p className="text-gray-500 text-xs">
            Powered by Gemini · Groq · OpenWeather · Telegram Bot API
          </p>
          <p className="text-gray-500 text-xs">
            Demo infra cost:{' '}
            <span className="text-emerald-400 font-bold" style={{ fontFamily: 'JetBrains Mono, monospace' }}>
              $0
            </span>
          </p>
        </div>
      </div>
    </footer>
  );
};
