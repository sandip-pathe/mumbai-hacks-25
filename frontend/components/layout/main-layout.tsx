"use client";

import { useWebSocket } from "@/hooks/use-websocket";
import { useUIStore } from "@/store/ui-store";
import { Header } from "./header";
import { Sidebar } from "./sidebar";

export function MainLayout({ children }: { children: React.ReactNode }) {
  const { isConnected } = useWebSocket();
  const sidebarOpen = useUIStore((state) => state.sidebarOpen);

  return (
    <div className="flex h-screen bg-background-light">
      {/* Sidebar */}
      <Sidebar />

      {/* Main Content */}
      <div
        className={`flex-1 flex flex-col transition-all duration-300 ${
          sidebarOpen ? "ml-64" : "ml-20"
        }`}
      >
        {/* Header */}
        <Header isConnected={isConnected} />

        {/* Page Content */}
        <main className="flex-1 overflow-y-auto p-8">{children}</main>
      </div>
    </div>
  );
}
