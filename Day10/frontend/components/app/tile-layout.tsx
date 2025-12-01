'use client';

import React, { useEffect, useMemo, useRef } from 'react';
import { Track } from 'livekit-client';
import { AnimatePresence, motion } from 'motion/react';
import {
  type TrackReference,
  VideoTrack,
  useLocalParticipant,
  useTracks,
  useVoiceAssistant,
} from '@livekit/components-react';
import { cn } from '@/lib/utils';

const MotionContainer = motion.create('div');

const ANIMATION_TRANSITION = {
  type: 'spring',
  stiffness: 800,
  damping: 50,
  mass: 1,
};

const classNames = {
  grid: [
    'h-full w-full',
    'grid gap-x-4 place-content-center',
    'grid-cols-[1fr_1fr] grid-rows-[60px_1fr_60px]',
  ],
  agentChatOpenWithSecondTile: ['col-start-1 row-start-1', 'self-center justify-self-end'],
  agentChatOpenWithoutSecondTile: ['col-start-1 row-start-1', 'col-span-2', 'place-content-center'],
  agentChatClosed: ['col-start-1 row-start-1', 'col-span-2 row-span-3', 'place-content-center'],
  secondTileChatOpen: ['col-start-2 row-start-1', 'self-center justify-self-start'],
  secondTileChatClosed: ['col-start-2 row-start-3', 'place-content-end'],
};

export function useLocalTrackRef(source: Track.Source) {
  const { localParticipant } = useLocalParticipant();
  const publication = localParticipant.getTrackPublication(source);
  const trackRef = useMemo<TrackReference | undefined>(
    () => (publication ? { source, participant: localParticipant, publication } : undefined),
    [source, publication, localParticipant]
  );
  return trackRef;
}

/* ============================================================
   CUSTOM WAVEFORM / ECG VISUALIZER (kept 100% intact)
   Only color and glow styling modified.
   ============================================================ */
const ECGVisualizer = ({
  trackRef,
  className,
}: {
  trackRef?: TrackReference;
  className?: string;
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || !trackRef?.publication?.track) return;

    const track = trackRef.publication.track;
    if (!track.mediaStreamTrack) return;

    const stream = new MediaStream([track.mediaStreamTrack]);
    const AudioContextClass = window.AudioContext || (window as any).webkitAudioContext;
    const audioContext = new AudioContextClass();
    const analyser = audioContext.createAnalyser();
    const source = audioContext.createMediaStreamSource(stream);

    analyser.fftSize = 2048;
    source.connect(analyser);

    const bufferLength = analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);
    let animationId: number;

    const draw = () => {
      animationId = requestAnimationFrame(draw);
      analyser.getByteTimeDomainData(dataArray);

      const ctx = canvas.getContext('2d');
      if (!ctx) return;

      const width = canvas.width;
      const height = canvas.height;

      ctx.clearRect(0, 0, width, height);

      ctx.lineWidth = 2;
      ctx.strokeStyle = '#ff69e0';             // neon pink
      ctx.shadowBlur = 8;
      ctx.shadowColor = '#ff69e0';             // glow

      ctx.beginPath();

      const sliceWidth = width / bufferLength;
      let x = 0;

      for (let i = 0; i < bufferLength; i++) {
        const v = dataArray[i] / 128.0;
        const y = (v * height) / 2;

        i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
        x += sliceWidth;
      }

      ctx.lineTo(canvas.width, canvas.height / 2);
      ctx.stroke();
    };

    draw();

    return () => {
      cancelAnimationFrame(animationId);
      source.disconnect();
      analyser.disconnect();
      audioContext.close();
    };
  }, [trackRef]);

  return <canvas ref={canvasRef} className={className} width={300} height={150} />;
};

interface TileLayoutProps {
  chatOpen: boolean;
}

export function TileLayout({ chatOpen }: TileLayoutProps) {
  const {
    state: agentState,
    audioTrack: agentAudioTrack,
    videoTrack: agentVideoTrack,
  } = useVoiceAssistant();

  const [screenShareTrack] = useTracks([Track.Source.ScreenShare]);
  const cameraTrack: TrackReference | undefined = useLocalTrackRef(Track.Source.Camera);

  const isCameraEnabled = cameraTrack && !cameraTrack.publication.isMuted;
  const isScreenShareEnabled = screenShareTrack && !screenShareTrack.publication.isMuted;

  const hasSecondTile = isCameraEnabled || isScreenShareEnabled;

  const animationDelay = chatOpen ? 0 : 0.15;
  const isAvatar = agentVideoTrack !== undefined;

  const w = agentVideoTrack?.publication.dimensions?.width ?? 0;
  const h = agentVideoTrack?.publication.dimensions?.height ?? 0;

  return (
    <div className="pointer-events-none fixed inset-x-0 top-8 bottom-32 z-50 md:top-12 md:bottom-40">
      <div className="relative mx-auto h-full max-w-4xl px-4 md:px-0">
        <div className={cn(classNames.grid)}>

          {/* =====================================================
              AGENT TILE  –  Audio waveform or Avatar
              ===================================================== */}
          <div
            className={cn([
              'grid transition-all duration-500 ease-spring',
              !chatOpen && classNames.agentChatClosed,
              chatOpen && hasSecondTile && classNames.agentChatOpenWithSecondTile,
              chatOpen && !hasSecondTile && classNames.agentChatOpenWithoutSecondTile,
            ])}
          >

            <AnimatePresence mode="popLayout">
              {!isAvatar && (
                <MotionContainer
                  key="agent-audio"
                  layoutId="agent"
                  initial={{ opacity: 0, scale: 0.8, filter: 'blur(12px)' }}
                  animate={{ opacity: 1, scale: chatOpen ? 1 : 1.15, filter: 'blur(0px)' }}
                  transition={{ ...ANIMATION_TRANSITION, delay: animationDelay }}
                  className={cn(
                    'relative overflow-hidden',
                    'bg-black/90 backdrop-blur-xl',
                    'border border-pink-500/30',
                    'shadow-[0_0_25px_-4px_rgba(255,105,224,0.4)]',
                    chatOpen
                      ? 'h-[60px] w-[60px] rounded-xl'
                      : 'h-[120px] w-[120px] rounded-2xl'
                  )}
                >
                  <div
                    className="absolute inset-0 z-0 opacity-15"
                    style={{
                      backgroundImage:
                        'linear-gradient(rgba(255,105,224,0.35) 1px, transparent 1px), linear-gradient(90deg, rgba(255,105,224,0.35) 1px, transparent 1px)',
                      backgroundSize: '12px 12px',
                    }}
                  />

                  <ECGVisualizer trackRef={agentAudioTrack} className="relative z-10 h-full w-full" />
                </MotionContainer>
              )}

              {isAvatar && (
                <MotionContainer
                  key="agent-video"
                  layoutId="avatar"
                  initial={{ scale: 1, opacity: 1 }}
                  animate={{
                    borderRadius: chatOpen ? 12 : 16,
                  }}
                  transition={{ ...ANIMATION_TRANSITION, delay: animationDelay }}
                  className={cn(
                    'relative overflow-hidden bg-black',
                    'border border-pink-400/30 shadow-[0_0_25px_-4px_rgba(255,105,224,0.3)]',
                    chatOpen
                      ? 'h-[60px] w-[60px]'
                      : 'h-auto w-full max-w-[400px] aspect-video rounded-2xl'
                  )}
                >
                  <VideoTrack
                    trackRef={agentVideoTrack}
                    width={w}
                    height={h}
                    className="h-full w-full object-cover opacity-90"
                  />
                </MotionContainer>
              )}
            </AnimatePresence>
          </div>

          {/* =====================================================
              SECOND TILE (camera or screen share)
              ===================================================== */}
          <div
            className={cn([
              'grid transition-all duration-500',
              chatOpen && classNames.secondTileChatOpen,
              !chatOpen && classNames.secondTileChatClosed,
            ])}
          >
            <AnimatePresence>
              {(cameraTrack && isCameraEnabled) ||
              (screenShareTrack && isScreenShareEnabled) ? (
                <MotionContainer
                  key="camera"
                  layout="position"
                  layoutId="camera"
                  initial={{ opacity: 0, scale: 0.85, y: 16 }}
                  animate={{ opacity: 1, scale: 1, y: 0 }}
                  exit={{ opacity: 0, scale: 0.8, y: 20 }}
                  transition={{ ...ANIMATION_TRANSITION, delay: animationDelay }}
                  className={cn(
                    'relative overflow-hidden',
                    'bg-black/80 border border-white/20',
                    'shadow-[0_0_25px_-4px_rgba(255,255,255,0.2)]',
                    'h-[60px] w-[60px] rounded-xl'
                  )}
                >
                  <VideoTrack
                    trackRef={cameraTrack || screenShareTrack}
                    width={(cameraTrack || screenShareTrack)?.publication.dimensions?.width ?? 0}
                    height={(cameraTrack || screenShareTrack)?.publication.dimensions?.height ?? 0}
                    className="h-full w-full object-cover grayscale-[0.05]"
                  />

                  {/* Status Dot */}
                  <div className="absolute bottom-2 right-2 h-2 w-2 rounded-full bg-pink-500 shadow-[0_0_6px_rgba(255,105,224,0.9)]" />
                </MotionContainer>
              ) : null}
            </AnimatePresence>
          </div>
        </div>
      </div>
    </div>
  );
}
