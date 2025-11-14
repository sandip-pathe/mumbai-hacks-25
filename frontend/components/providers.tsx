"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { createContext, useContext, useEffect, useRef, useState } from "react";

// WebSocket Context
interface WebSocketContextType {
  isConnected: boolean;
  send: (data: any) => void;
}

const WebSocketContext = createContext<WebSocketContextType>({
  isConnected: false,
  send: () => {},
});

export const useWebSocketContext = () => useContext(WebSocketContext);

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000/ws";
const RECONNECT_DELAY = 3000;
const MAX_RECONNECT_ATTEMPTS = 5;

function WebSocketProvider({
  children,
  queryClient,
}: {
  children: React.ReactNode;
  queryClient: QueryClient;
}) {
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const isMountedRef = useRef(true);

  const connect = () => {
    // Don't connect if unmounted or already connected/connecting
    if (!isMountedRef.current) return;
    if (
      wsRef.current?.readyState === WebSocket.OPEN ||
      wsRef.current?.readyState === WebSocket.CONNECTING
    ) {
      return;
    }

    // Stop reconnecting after max attempts
    if (reconnectAttemptsRef.current >= MAX_RECONNECT_ATTEMPTS) {
      console.error("❌ Max WebSocket reconnect attempts reached");
      return;
    }

    try {
      const ws = new WebSocket(WS_URL);

      ws.onopen = () => {
        if (!isMountedRef.current) {
          ws.close();
          return;
        }
        console.log("✅ WebSocket connected");
        setIsConnected(true);
        reconnectAttemptsRef.current = 0; // Reset on successful connection

        if (reconnectTimeoutRef.current) {
          clearTimeout(reconnectTimeoutRef.current);
          reconnectTimeoutRef.current = null;
        }
      };

      ws.onmessage = (event) => {
        if (!isMountedRef.current) return;

        try {
          const data = JSON.parse(event.data);

          // Respond to server pings
          if (data.type === "ping") {
            ws.send("pong");
            return;
          }

          // Handle connection confirmation
          if (data.type === "connected") {
            console.log("📡 WebSocket handshake complete:", data.message);
            return;
          }

          // Invalidate queries based on message type
          if (data.type === "score_updated") {
            queryClient.invalidateQueries({ queryKey: ["compliance-score"] });
          }
          if (data.type === "alert_created") {
            queryClient.invalidateQueries({ queryKey: ["alerts"] });
          }
        } catch (error) {
          console.error("Error parsing WebSocket message:", error);
        }
      };
      ws.onclose = () => {
        if (!isMountedRef.current) return;

        console.log("❌ WebSocket disconnected");
        setIsConnected(false);
        wsRef.current = null;

        // Auto-reconnect with exponential backoff
        if (!reconnectTimeoutRef.current) {
          reconnectAttemptsRef.current++;
          const delay =
            RECONNECT_DELAY * Math.pow(1.5, reconnectAttemptsRef.current - 1);

          reconnectTimeoutRef.current = setTimeout(() => {
            reconnectTimeoutRef.current = null;
            connect();
          }, Math.min(delay, 30000)); // Max 30 seconds
        }
      };

      ws.onerror = (error) => {
        console.error("WebSocket error:", error);
      };

      wsRef.current = ws;
    } catch (error) {
      console.error("Failed to create WebSocket:", error);
      setIsConnected(false);
    }
  };

  const send = (data: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(data));
    }
  };

  useEffect(() => {
    isMountedRef.current = true;
    connect();

    return () => {
      isMountedRef.current = false;

      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
        reconnectTimeoutRef.current = null;
      }

      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
    };
  }, []);

  return (
    <WebSocketContext.Provider value={{ isConnected, send }}>
      {children}
    </WebSocketContext.Provider>
  );
}

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 60 * 1000, // 1 minute
            refetchOnWindowFocus: false,
          },
        },
      })
  );

  return (
    <QueryClientProvider client={queryClient}>
      <WebSocketProvider queryClient={queryClient}>
        {children}
      </WebSocketProvider>
    </QueryClientProvider>
  );
}
