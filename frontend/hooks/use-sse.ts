"use client";

import { useEffect, useRef, useState, useCallback } from "react";

export interface SSEEvent {
  type: string;
  data: Record<string, unknown>;
  timestamp?: string;
}

interface UseSSEOptions {
  url: string;
  token?: string;
  enabled?: boolean;
  onEvent?: (event: SSEEvent) => void;
  onError?: (error: Event) => void;
}

export function useSSE({ url, token, enabled = true, onEvent, onError }: UseSSEOptions) {
  const [connected, setConnected] = useState(false);
  const [events, setEvents] = useState<SSEEvent[]>([]);
  const [error, setError] = useState<string | null>(null);
  const eventSourceRef = useRef<EventSource | null>(null);

  const connect = useCallback(() => {
    if (!enabled || !url) return;

    try {
      const headers: Record<string, string> = {};
      if (token) {
        headers["Authorization"] = `Bearer ${token}`;
      }

      // EventSource doesn't support custom headers, use query param for auth
      const authParam = token ? `?token=${encodeURIComponent(token)}` : "";
      const eventSource = new EventSource(`${url}${authParam}`);
      eventSourceRef.current = eventSource;

      eventSource.onopen = () => {
        setConnected(true);
        setError(null);
      };

      eventSource.onmessage = (event) => {
        try {
          const parsed: SSEEvent = JSON.parse(event.data);
          setEvents((prev) => [...prev, parsed]);
          onEvent?.(parsed);
        } catch {
          // Non-JSON message
        }
      };

      eventSource.onerror = () => {
        setConnected(false);
        setError("Connection lost. Reconnecting...");
        onError?.(new Event("error"));
        eventSource.close();
      };
    } catch (err) {
      setError("Failed to establish connection");
    }
  }, [url, token, enabled, onEvent, onError]);

  useEffect(() => {
    connect();
    return () => {
      eventSourceRef.current?.close();
    };
  }, [connect]);

  const disconnect = useCallback(() => {
    eventSourceRef.current?.close();
    setConnected(false);
  }, []);

  const clearEvents = useCallback(() => {
    setEvents([]);
  }, []);

  return { connected, events, error, disconnect, clearEvents };
}
