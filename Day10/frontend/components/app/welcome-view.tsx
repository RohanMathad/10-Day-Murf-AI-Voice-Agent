'use client';

import React, { useState } from 'react';
import { Button } from '@/components/livekit/button';

// Purple equalizer logo
function WelcomeImage() {
  return (
    <svg
      width="64"
      height="64"
      viewBox="0 0 64 64"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className="text-purple-300 mb-6 size-20 drop-shadow-[0_0_18px_rgba(168,85,247,0.7)]"
    >
      <path
        d="M15 24V40C15 40.7957 14.6839 41.5587 14.1213 42.1213C13.5587 42.6839 12.7956 43 12 43C11.2044 43 10.4413 42.6839 9.87868 42.1213C9.31607 41.5587 9 40.7957 9 40V24C9 23.2044 9.31607 22.4413 9.87868 21.8787C10.4413 21.3161 11.2044 21 12 21C12.7956 21 13.5587 21.3161 14.1213 21.8787C14.6839 22.4413 15 23.2044 15 24ZM22 5C21.2044 5 20.4413 5.31607 19.8787 5.87868C19.3161 6.44129 19 7.20435 19 8V56C19 56.7957 19.3161 57.5587 19.8787 58.1213C20.4413 58.6839 21.2044 59 22 59C22.7956 59 23.5587 58.6839 24.1213 58.1213C24.6839 57.5587 25 56.7957 25 56V8C25 7.20435 24.6839 6.44129 24.1213 5.87868C23.5587 5.31607 22.7956 5 22 5ZM32 13C31.2044 13 30.4413 13.3161 29.8787 13.8787C29.3161 14.4413 29 15.2044 29 16V48C29 48.7957 29.3161 49.5587 29.8787 50.1213C30.4413 50.6839 31.2044 51 32 51C32.7956 51 33.5587 50.6839 34.1213 50.1213C34.6839 49.5587 35 48.7957 35 48V16C35 15.2044 34.6839 14.4413 34.1213 13.8787C33.5587 13.3161 32.7956 13 32 13ZM42 21C41.2043 21 40.4413 21.3161 39.8787 21.8787C39.3161 22.4413 39 23.2044 39 24V40C39 40.7957 39.3161 41.5587 39.8787 42.1213C40.4413 42.6839 41.2043 43 42 43C42.7957 43 43.5587 42.6839 44.1213 42.1213C44.6839 41.5587 45 40.7957 45 40V24C45 23.2044 44.6839 22.4413 44.1213 21.8787C43.5587 21.3161 42.7957 21 42 21ZM52 17C51.2043 17 50.4413 17.3161 49.8787 17.8787C49.3161 18.4413 49 19.2044 49 20V44C49 44.7957 49.3161 45.5587 49.8787 46.1213C50.4413 46.6839 51.2043 47 52 47C52.7957 47 53.5587 46.6839 54.1213 46.1213C54.6839 45.5587 55 44.7957 55 44V20C55 19.2044 54.6839 18.4413 54.1213 17.8787C53.5587 17.3161 52.7957 17 52 17Z"
        fill="currentColor"
      />
    </svg>
  );
}

// Corner TV Icon
function RetroTvIcon({ className }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.5"
      className={className}
    >
      <rect x="2" y="7" width="20" height="15" rx="2" ry="2" />
      <polyline points="17 2 12 7 7 2" />
    </svg>
  );
}

export const WelcomeView = React.forwardRef<HTMLDivElement, any>(
  ({ onStartCall }, ref) => {
    const [name, setName] = useState('');
    const [started, setStarted] = useState(false);

    function handleStart() {
      if (!name.trim()) return;

      localStorage.setItem('player_name', name.trim());
      setStarted(true);
      onStartCall?.(name.trim());
    }

    return (
      <div ref={ref} className="min-h-screen w-full flex items-center justify-between px-20 text-white">

        {/* LEFT SIDE TITLE */}
        <div className="flex flex-col gap-4 max-w-xl m-10 ">
          <h1 className="text-7xl font-extrabold bg-gradient-to-r from-pink-500 to-purple-400 bg-clip-text text-transparent drop-shadow-[0_0_18px_rgba(236,72,153,0.5)]">
            Improv Battle
          </h1>

          <p className="text-lg text-white/70">
            Step onto the stage. Bring your character alive.  
            <br />
            The host is waiting.
          </p>
        </div>

        {/* RIGHT SIDE CARD */}
        {!started ? (
          <section className="relative flex flex-col items-center text-center p-10 
            bg-[#0d0d16] rounded-3xl overflow-hidden
            shadow-[0_0_70px_rgba(168,85,247,0.45)]
            border border-white/10 w-full max-w-sm mr-50">

            <RetroTvIcon className="absolute top-4 right-4 w-8 h-8 text-purple-400 opacity-80" />

            <WelcomeImage />

            <h2 className="text-2xl font-bold text-white mb-2">Enter the Arena</h2>
            <p className="text-white/70 mb-6">Enter your name to begin the improv.</p>

            {/* INPUT */}
            <label className="block text-xs font-bold uppercase tracking-wider mb-2 text-left text-white/60 w-full ml-1">
              Your Stage Name
            </label>

            <div className="flex w-full items-stretch gap-2">
              <input
                value={name}
                onChange={(e) => setName(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleStart()}
                placeholder="Type name..."
                className="flex-1 rounded-xl border-none px-4 py-3 
                bg-[#11111c] text-white placeholder:text-white/30 font-semibold
                shadow-inner focus:outline-none focus:ring-2 focus:ring-purple-500/50"
              />

              <Button
                onClick={handleStart}
                className="px-6 rounded-xl font-bold
                bg-gradient-to-r from-pink-400 to-purple-500 
                text-black shadow-lg hover:scale-105 transition"
              >
                →
              </Button>
            </div>

            <div className="mt-4 text-[10px] text-white/40">Press Enter to Begin</div>
          </section>
        ) : (
          <div className="text-2xl font-bold animate-pulse">🔥 Preparing the stage…</div>
        )}
      </div>
    );
  }
);

WelcomeView.displayName = 'WelcomeView';
