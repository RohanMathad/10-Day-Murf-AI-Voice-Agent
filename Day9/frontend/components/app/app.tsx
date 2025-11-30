'use client';

import { RoomAudioRenderer, StartAudio } from '@livekit/components-react';
import type { AppConfig } from '@/app-config';
import { SessionProvider } from '@/components/app/session-provider';
import { ViewController } from '@/components/app/view-controller';
import { Toaster } from '@/components/livekit/toaster';

interface AppProps {
  appConfig: AppConfig;
}

export function App({ appConfig }: AppProps) {
  return (
    <SessionProvider appConfig={appConfig}>

      <div className="pointer-events-none fixed inset-0 overflow-hidden -z-10">
        <div className="absolute top-20 left-24 w-72 h-72 bg-primary/10 blur-3xl rounded-full animate-float-slow"></div>

        <div className="absolute bottom-28 right-16 w-96 h-96 bg-accent/10 blur-2xl rounded-full animate-float-slower"></div>

        <div className="absolute inset-0 m-auto w-80 h-80 bg-primary/5 blur-[120px] rounded-full animate-pulse"></div>
      </div>

      <main className="grid h-svh grid-cols-1 place-content-center relative z-10">
        <ViewController />
      </main>

      <StartAudio label="Start Audio" />
      <RoomAudioRenderer />
      <Toaster />
    </SessionProvider>
  );
}
