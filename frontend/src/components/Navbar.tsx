import React from 'react';
import { StatusBadge } from './StatusBadge';

export const Navbar: React.FC = () => {
  return (
    <nav className="sticky top-0 z-50 bg-[#0B2545] border-b border-white/10 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo / Name */}
          <div className="flex items-center gap-3">
            <div className="flex items-center justify-center w-9 h-9 rounded-xl bg-green-500/20 border border-green-500/40">
              <span className="text-green-400 text-xl">🌱</span>
            </div>
            <div>
              <h1 className="text-white font-bold text-lg leading-none tracking-tight">Krish</h1>
              <p className="text-white/40 text-[10px] uppercase tracking-widest">AI Crop Advisory</p>
            </div>
          </div>

          {/* Right side */}
          <div className="flex items-center gap-4">
            <StatusBadge status="connected" label="All Systems Live" />
            <div className="hidden sm:flex items-center gap-2 bg-white/5 rounded-lg px-3 py-1.5 border border-white/10">
              <span className="text-white/60 text-xs">v1.0.0</span>
              <span className="text-white/20">|</span>
              <span className="text-white/60 text-xs">MVP Demo</span>
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
};
