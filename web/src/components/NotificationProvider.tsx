import React, { createContext, useContext, useState, useCallback, useRef } from 'react';
import { CheckCircle2, AlertTriangle, XCircle, Info, Loader2, X } from 'lucide-react';

export type NotificationType = 'success' | 'error' | 'info' | 'warning' | 'loading';

export interface NotificationItem {
  id: string;
  type: NotificationType;
  title?: string;
  message: string;
  duration?: number;
}

interface NotificationContextType {
  notifications: NotificationItem[];
  notify: {
    success: (message: string, title?: string, duration?: number) => string;
    error: (message: string, title?: string, duration?: number) => string;
    info: (message: string, title?: string, duration?: number) => string;
    warning: (message: string, title?: string, duration?: number) => string;
    loading: (message: string, title?: string) => string;
    dismiss: (id: string) => void;
  };
}

const NotificationContext = createContext<NotificationContextType | undefined>(undefined);

export const NotificationProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const timersRef = useRef<Map<string, { timeoutId: number; remaining: number; started: number }>>(new Map());

  const dismiss = useCallback((id: string) => {
    const timer = timersRef.current.get(id);
    if (timer) {
      window.clearTimeout(timer.timeoutId);
      timersRef.current.delete(id);
    }
    setNotifications((prev) => prev.filter((n) => n.id !== id));
  }, []);

  const addNotification = useCallback(
    (type: NotificationType, message: string, title?: string, customDuration?: number): string => {
      const id = `notif-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`;
      const duration = customDuration ?? (type === 'error' ? 6500 : type === 'loading' ? 0 : 4500);

      const newItem: NotificationItem = { id, type, title, message, duration };

      setNotifications((prev) => [newItem, ...prev.slice(0, 4)]); // Stack up to 5 max

      if (duration > 0) {
        const timeoutId = window.setTimeout(() => dismiss(id), duration);
        timersRef.current.set(id, {
          timeoutId,
          remaining: duration,
          started: Date.now(),
        });
      }

      return id;
    },
    [dismiss]
  );

  const notify = {
    success: (msg: string, title?: string, dur?: number) => addNotification('success', msg, title, dur),
    error: (msg: string, title?: string, dur?: number) => addNotification('error', msg, title, dur),
    info: (msg: string, title?: string, dur?: number) => addNotification('info', msg, title, dur),
    warning: (msg: string, title?: string, dur?: number) => addNotification('warning', msg, title, dur),
    loading: (msg: string, title?: string) => addNotification('loading', msg, title, 0),
    dismiss,
  };

  const handleMouseEnter = (id: string) => {
    const timer = timersRef.current.get(id);
    if (timer) {
      window.clearTimeout(timer.timeoutId);
      const elapsed = Date.now() - timer.started;
      timer.remaining = Math.max(1000, timer.remaining - elapsed);
    }
  };

  const handleMouseLeave = (id: string) => {
    const timer = timersRef.current.get(id);
    if (timer) {
      timer.started = Date.now();
      timer.timeoutId = window.setTimeout(() => dismiss(id), timer.remaining);
    }
  };

  return (
    <NotificationContext.Provider value={{ notifications, notify }}>
      {children}

      {/* Floating Notification Stack (Top-Right) */}
      <div
        role="region"
        aria-label="Notifications"
        aria-live="polite"
        className="fixed top-5 right-5 z-50 flex flex-col gap-2.5 max-w-sm w-full pointer-events-none"
      >
        {notifications.map((item) => {
          const isSuccess = item.type === 'success';
          const isError = item.type === 'error';
          const isWarning = item.type === 'warning';
          const isLoading = item.type === 'loading';

          const accentColor = isSuccess
            ? 'text-emerald-300 border-emerald-500/30 shadow-[0_4px_24px_rgba(16,185,129,0.12)]'
            : isError
            ? 'text-rose-300 border-rose-500/35 shadow-[0_4px_24px_rgba(244,63,94,0.14)]'
            : isWarning
            ? 'text-amber-300 border-amber-500/30 shadow-[0_4px_24px_rgba(245,158,11,0.12)]'
            : isLoading
            ? 'text-[#C4B5FD] border-[#8B5CF6]/35 shadow-[0_4px_24px_rgba(139,92,246,0.15)]'
            : 'text-[#DDD6FE] border-white/15 shadow-[0_4px_24px_rgba(187,168,241,0.12)]';

          const icon = isSuccess ? (
            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
          ) : isError ? (
            <XCircle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
          ) : isWarning ? (
            <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
          ) : isLoading ? (
            <Loader2 className="w-4 h-4 text-[#C4B5FD] shrink-0 mt-0.5 animate-spin" />
          ) : (
            <Info className="w-4 h-4 text-[#C4B5FD] shrink-0 mt-0.5" />
          );

          return (
            <div
              key={item.id}
              onMouseEnter={() => handleMouseEnter(item.id)}
              onMouseLeave={() => handleMouseLeave(item.id)}
              className={`pointer-events-auto p-4 rounded-2xl bg-[#0d091a]/90 backdrop-blur-xl border ${accentColor} transition-all duration-200 transform translate-y-0 opacity-100 flex items-start gap-3 shadow-2xl animate-fade-in`}
              style={{
                background: 'linear-gradient(135deg, rgba(20, 14, 38, 0.92) 0%, rgba(10, 7, 20, 0.96) 100%)',
              }}
            >
              {icon}
              <div className="flex-1 min-w-0 pr-1">
                {item.title && (
                  <h4 className="text-xs font-display font-semibold tracking-wide text-[#F1EDF8] mb-0.5">
                    {item.title}
                  </h4>
                )}
                <p className="text-[12px] font-sans font-light text-[#D8D2E6] leading-relaxed break-words">
                  {item.message}
                </p>
              </div>
              <button
                onClick={() => dismiss(item.id)}
                className="p-1 rounded-lg text-[#9892AB] hover:text-[#F1EDF8] hover:bg-white/6 transition cursor-pointer shrink-0"
                aria-label="Dismiss notification"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            </div>
          );
        })}
      </div>
    </NotificationContext.Provider>
  );
};

export function useNotifications() {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotifications must be used within a NotificationProvider');
  }
  return context.notify;
}

