"use client";

import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Bell, Wifi, WifiOff } from "lucide-react";

interface HeaderProps {
  isConnected: boolean;
}

export function Header({ isConnected }: HeaderProps) {
  return (
    <header className="h-16 border-b border-gray-200 bg-white px-8 flex items-center justify-between">
      <div className="flex items-center gap-4">
        <h1 className="text-2xl font-heading font-bold text-text-dark">
          Compliance Dashboard
        </h1>
      </div>

      <div className="flex items-center gap-4">
        {/* WebSocket Status */}
        <Badge
          variant={isConnected ? "default" : "destructive"}
          className="gap-2"
        >
          {isConnected ? <Wifi size={14} /> : <WifiOff size={14} />}
          {isConnected ? "Live" : "Offline"}
        </Badge>

        {/* Notifications */}
        <button className="relative p-2 hover:bg-gray-100 rounded-lg">
          <Bell size={20} className="text-gray-600" />
          <span className="absolute top-1 right-1 w-2 h-2 bg-critical rounded-full" />
        </button>

        {/* User Avatar */}
        <Avatar>
          <AvatarFallback className="bg-accent text-white">CO</AvatarFallback>
        </Avatar>
        <div className="text-sm">
          <p className="font-medium text-text-dark">Compliance Officer</p>
          <p className="text-gray-500 text-xs">compliance@fintech.com</p>
        </div>
      </div>
    </header>
  );
}
