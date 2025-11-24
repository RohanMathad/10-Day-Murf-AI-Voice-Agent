import * as React from 'react';
import { cn } from '@/lib/utils';

export interface ChatEntryProps extends React.HTMLAttributes<HTMLLIElement> {
  locale: string;
  timestamp: number;
  message: string;
  messageOrigin: 'local' | 'remote';
  name?: string;
  hasBeenEdited?: boolean;
}

export const ChatEntry = ({
  name,
  locale,
  timestamp,
  message,
  messageOrigin,
  hasBeenEdited = false,
  className,
  ...props
}: ChatEntryProps) => {
  const time = new Date(timestamp);
  const title = time.toLocaleTimeString(locale, { timeStyle: 'full' });

  return (
    <li
      title={title}
      data-lk-message-origin={messageOrigin}
      className={cn('group flex w-full flex-col gap-1', className)}
      {...props}
    >
      {/* Header: name + timestamp */}
      <header
        className={cn(
          'flex items-center gap-2 text-xs text-muted-foreground',
          messageOrigin === 'local' ? 'flex-row-reverse text-right' : 'text-left'
        )}
      >
        {name && <strong className="text-foreground">{name}</strong>}
        <span className="font-mono opacity-0 transition-opacity duration-200 group-hover:opacity-100">
          {hasBeenEdited && '*'}
          {time.toLocaleTimeString(locale, { timeStyle: 'short' })}
        </span>
      </header>

      {/* Message bubble */}
      <span
        className={cn(
          'max-w-[75%] rounded-2xl px-4 py-2 text-sm shadow-sm leading-relaxed',
          messageOrigin === 'local'
            ? // User bubble: soft mint-teal
              'ml-auto bg-primary text-primary-foreground shadow-md'
            : // AI bubble: soft card panel
              'mr-auto bg-card text-foreground border border-border/30'
        )}
      >
        {message}
      </span>
    </li>
  );
};
