'use client';

import React, { useEffect, useRef, useState } from 'react';
import { motion } from 'motion/react';
import { useLocalParticipant } from '@livekit/components-react';
import { ParticipantEvent, type LocalParticipant } from 'livekit-client';
import type { AppConfig } from '@/app-config';
import { ChatTranscript } from '@/components/app/chat-transcript';
import { PreConnectMessage } from '@/components/app/preconnect-message';
import { TileLayout } from '@/components/app/tile-layout';
import {
  AgentControlBar,
  type ControlBarControls,
} from '@/components/livekit/agent-control-bar/agent-control-bar';
import { useChatMessages } from '@/hooks/useChatMessages';
import { useConnectionTimeout } from '@/hooks/useConnectionTimout';
import { useDebugMode } from '@/hooks/useDebug';
import { cn } from '@/lib/utils';
import { ScrollArea } from '../livekit/scroll-area/scroll-area';

const MotionBottom = motion.create('div');

const IN_DEVELOPMENT = process.env.NODE_ENV !== 'production';
const BOTTOM_VIEW_MOTION_PROPS = {
  variants: {
    visible: {
      opacity: 1,
      translateY: '0%',
    },
    hidden: {
      opacity: 0,
      translateY: '100%',
    },
  },
  initial: 'hidden',
  animate: 'visible',
  exit: 'hidden',
  transition: {
    duration: 0.3,
    delay: 0.5,
    ease: 'easeOut',
  },
};

function Fade({ top = false, bottom = false, className }: any) {
  return (
    <div
      className={cn(
        'pointer-events-none h-4',
        top && 'bg-gradient-to-b from-black/10 to-transparent',
        bottom && 'bg-gradient-to-t from-black/10 to-transparent',
        className
      )}
    />
  );
}

/* -------------------------------------------
   FIXED PLAYER BADGE
   Always uses name typed in Welcome screen.
-------------------------------------------- */
function PlayerBadge({ participant }: { participant?: LocalParticipant }) {
  const [displayName, setDisplayName] = useState("Player");

  useEffect(() => {
    // direct stage name from welcome screen
    const savedName = typeof window !== 'undefined'
      ? localStorage.getItem("player_name")
      : null;

    if (savedName && savedName.trim() !== "") {
      setDisplayName(savedName.trim());
      return;
    }

    // fallback to participant name if exists
    const updateName = () => {
      const finalName =
        participant?.name && participant.name !== 'user' && participant.name !== 'identity'
          ? participant.name
          : "Player";
      setDisplayName(finalName);
    };

    updateName();

    if (!participant) return;

    participant.on(ParticipantEvent.NameChanged, updateName);
    participant.on(ParticipantEvent.MetadataChanged, updateName);

    return () => {
      participant?.off(ParticipantEvent.NameChanged, updateName);
      participant?.off(ParticipantEvent.MetadataChanged, updateName);
    };
  }, [participant]);

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: 0.5 }}
      className="absolute top-4 left-4 z-40 flex items-center gap-3 rounded-2xl 
      bg-white/10 p-2 pr-5 backdrop-blur-2xl border border-white/20 shadow-lg ring-1 ring-white/10"
    >
      <div className="flex h-10 w-10 items-center justify-center rounded-full 
      bg-gradient-to-br from-pink-400 to-violet-500 text-black shadow-lg">
        <svg xmlns="http://www.w3.org/2000/svg" fill="currentColor" className="size-6" viewBox="0 0 24 24">
          <path fillRule="evenodd" d="M7.5 6a4.5 4.5 0 1 1 9 0..." clipRule="evenodd" />
        </svg>
      </div>

      <div className="flex flex-col">
        <span className="text-[10px] uppercase font-bold text-white/60 tracking-wider">
          Contestant
        </span>
        <span className="text-sm font-extrabold text-white tracking-wide">
          {displayName}
        </span>
      </div>
    </motion.div>
  );
}

/* -------------------------------------------
   MAIN SESSION VIEW
-------------------------------------------- */

interface SessionViewProps {
  appConfig: AppConfig;
}

export const SessionView = ({
  appConfig,
  ...props
}: React.ComponentProps<'section'> & SessionViewProps) => {
  useConnectionTimeout(200_000);
  useDebugMode({ enabled: IN_DEVELOPMENT });

  const { localParticipant } = useLocalParticipant();
  const messages = useChatMessages();
  const [chatOpen, setChatOpen] = useState(false);
  const scrollAreaRef = useRef<HTMLDivElement>(null);

  const controls: ControlBarControls = {
    leave: true,
    microphone: true,
    chat: appConfig.supportsChatInput,
    camera: appConfig.supportsVideoInput,
    screenShare: appConfig.supportsVideoInput,
  };

  useEffect(() => {
    const lastMessage = messages.at(-1);
    const lastLocal = lastMessage?.from?.isLocal === true;
    if (scrollAreaRef.current && lastLocal) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight;
    }
  }, [messages]);

  return (
    <section
      className="relative z-10 h-full w-full overflow-hidden"
      {...props}
    >
      {/* Player Name Badge */}
      <PlayerBadge participant={localParticipant} />

      {/* Chat panel */}
      <div
        className={cn(
          'fixed inset-0 grid grid-cols-1 grid-rows-1',
          !chatOpen && 'pointer-events-none'
        )}
      >
        <Fade top className="absolute inset-x-4 top-0 h-40" />
        <ScrollArea
          ref={scrollAreaRef}
          className="px-4 pt-40 pb-[150px] md:px-6 md:pb-[180px]"
        >
          <ChatTranscript
            hidden={!chatOpen}
            messages={messages}
            className="ml-auto mr-0 md:mr-12 max-w-lg space-y-3 transition-opacity duration-300 ease-out"
          />
        </ScrollArea>
      </div>

      {/* Agent Visual */}
      <TileLayout chatOpen={chatOpen} />

      {/* Bottom Controls */}
      <MotionBottom
        {...BOTTOM_VIEW_MOTION_PROPS}
        className="fixed inset-x-3 bottom-0 z-50 md:inset-x-12"
      >
        {appConfig.isPreConnectBufferEnabled && (
          <PreConnectMessage messages={messages} className="pb-4" />
        )}

        <div className="relative ml-auto mr-0 md:mr-4 max-w-lg pb-3 md:pb-12">
          <Fade bottom className="absolute inset-x-0 top-0 h-4 -translate-y-full" />
          <AgentControlBar controls={controls} onChatOpenChange={setChatOpen} />
        </div>
      </MotionBottom>
    </section>
  );
};
