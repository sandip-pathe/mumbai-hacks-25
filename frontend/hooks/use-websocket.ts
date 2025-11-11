"use client";

import { useEffect, useRef, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000/ws";
const RECONNECT_DELAY = 3000; // 3 seconds

export function useWebSocket() {
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const queryClient = useQueryClient();
  const shouldReconnectRef = useRef(true);

  useEffect(() => {
    shouldReconnectRef.current = true;

    const connect = () => {
      // Don't reconnect if we've been told to stop
      if (!shouldReconnectRef.current) return;

      // Clean up any existing connection
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        return; // Already connected
      }

      try {
        const ws = new WebSocket(WS_URL);

        ws.onopen = () => {
          console.log("✅ WebSocket connected");
          setIsConnected(true);
          // Clear any reconnect timeout on successful connection
          if (reconnectTimeoutRef.current) {
            clearTimeout(reconnectTimeoutRef.current);
            reconnectTimeoutRef.current = null;
          }
        };

        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);

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
          console.log("❌ WebSocket disconnected");
          setIsConnected(false);
          wsRef.current = null;

          // Auto-reconnect after delay if we should still be connected
          if (shouldReconnectRef.current && !reconnectTimeoutRef.current) {
            reconnectTimeoutRef.current = setTimeout(() => {
              console.log("🔄 Attempting to reconnect WebSocket...");
              reconnectTimeoutRef.current = null;
              connect();
            }, RECONNECT_DELAY);
          }
        };

        ws.onerror = (error) => {
          console.error("WebSocket error:", error);
          // Error will trigger onclose, which will handle reconnection
        };

        wsRef.current = ws;
      } catch (error) {
        console.error("Failed to create WebSocket:", error);
        setIsConnected(false);
      }
    };

    // Initial connection
    connect();

    // Cleanup
    return () => {
      shouldReconnectRef.current = false;

      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
        reconnectTimeoutRef.current = null;
      }

      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
    };
  }, [queryClient]);

  return { isConnected };
}
