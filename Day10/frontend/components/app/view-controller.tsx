'use client';

import { useRef } from 'react';
import { AnimatePresence, motion } from 'motion/react';
import { useRoomContext } from '@livekit/components-react';
import { useSession } from '@/components/app/session-provider';
import { SessionView } from '@/components/app/session-view';
import { WelcomeView } from '@/components/app/welcome-view';

const MotionWelcomeView = motion.create(WelcomeView);
const MotionSessionView = motion.create(SessionView);

// Subtle upgraded transition set (fade + slight scale)
const VIEW_MOTION_PROPS = {
  variants: {
    visible: {
      opacity: 1,
      scale: 1,
      transition: {
        duration: 0.45,
        ease: 'easeOut',
      },
    },
    hidden: {
      opacity: 0,
      scale: 0.98,
      transition: {
        duration: 0.35,
        ease: 'easeIn',
      },
    },
  },
  initial: 'hidden',
  animate: 'visible',
  exit: 'hidden',
};

export function ViewController() {
  const room = useRoomContext();
  const isSessionActiveRef = useRef(false);
  const { appConfig, isSessionActive, startSession } = useSession();

  // Ensure up-to-date value inside animation handler
  isSessionActiveRef.current = isSessionActive;

  // Disconnect LiveKit room after fade-out animation completes
  const handleAnimationComplete = () => {
    if (!isSessionActiveRef.current && room.state !== 'disconnected') {
      room.disconnect();
    }
  };

  return (
    <AnimatePresence mode="wait">

      {/* ------------------------------
          Welcome Screen
      ------------------------------ */}
      {!isSessionActive && (
        <MotionWelcomeView
          key="welcome"
          {...VIEW_MOTION_PROPS}
          startButtonText={appConfig.startButtonText}
          onStartCall={startSession}
          className="relative"
        />
      )}

      {/* ------------------------------
          Active Session Screen
      ------------------------------ */}
      {isSessionActive && (
        <MotionSessionView
          key="session-view"
          {...VIEW_MOTION_PROPS}
          appConfig={appConfig}
          onAnimationComplete={handleAnimationComplete}
          className="relative"
        />
      )}
    </AnimatePresence>
  );
}
