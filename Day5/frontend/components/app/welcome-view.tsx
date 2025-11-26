import { Button } from '@/components/livekit/button';

function LenskartLogo() {
  return (
    <svg
      width="160"
      height="80"
      viewBox="0 0 1200 600"
      xmlns="http://www.w3.org/2000/svg"
      className="mb-6"
    >
      <defs>
        <linearGradient id="lk_grad" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stopColor="#00B884" />
          <stop offset="100%" stopColor="#FFE247" />
        </linearGradient>
      </defs>
      <path
        fill="url(#lk_grad)"
        d="M598.4 234.2c-39.1 0-74.8 20.3-94.4 53.6-19.6-33.3-55.3-53.6-94.4-53.6-61 0-110.4 49.4-110.4 110.4s49.4 110.4 110.4 110.4c39.1 0 74.8-20.3 94.4-53.6 19.6 33.3 55.3 53.6 94.4 53.6 61 0 110.4-49.4 110.4-110.4s-49.4-110.4-110.4-110.4zm-188.8 176.1c-36.2 0-65.7-29.5-65.7-65.7s29.5-65.7 65.7-65.7 65.7 29.5 65.7 65.7-29.5 65.7-65.7 65.7zm188.8 0c-36.2 0-65.7-29.5-65.7-65.7s29.5-65.7 65.7-65.7 65.7 29.5 65.7 65.7-29.5 65.7-65.7 65.7z"
      />
    </svg>
  );
}

interface WelcomeViewProps {
  startButtonText: string;
  onStartCall: () => void;
}

export const WelcomeView = ({
  startButtonText,
  onStartCall,
  ref,
}: React.ComponentProps<'div'> & WelcomeViewProps) => {
  return (
    <div ref={ref}>
      <section className="bg-background flex flex-col items-center justify-center text-center py-20">
        {/* Lenskart Logo */}
        <LenskartLogo />

        <h1 className="text-foreground text-2xl font-semibold mb-2">
          Welcome to the Lenskart Voice Assistant
        </h1>

        <p className="text-muted-foreground max-w-prose leading-6 font-medium">
          Chat live with your AI-powered Lenskart sales assistant.
        </p>

        <Button
          variant="primary"
          size="lg"
          onClick={onStartCall}
          className="mt-8 w-64 font-mono bg-[#00B884] hover:bg-[#009E72] text-black"
        >
          {startButtonText}
        </Button>
      </section>

      <div className="fixed bottom-5 left-0 flex w-full items-center justify-center">
        <p className="text-muted-foreground text-xs md:text-sm">
          Need help setting up? Check the{' '}
          <a
            target="_blank"
            rel="noopener noreferrer"
            href="https://docs.livekit.io/agents/start/voice-ai/"
            className="underline"
          >
            Voice AI quickstart
          </a>.
        </p>
      </div>
    </div>
  );
};
