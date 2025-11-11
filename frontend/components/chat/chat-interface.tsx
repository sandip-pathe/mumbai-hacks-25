"use client";

import { useRef, useEffect } from "react";
import { Card } from "@/components/ui/card";
import { MessageBubble } from "./message-bubble";
import { ChatInput } from "./chat-input";
import { ChatMessage } from "@/lib/api";
import { Loader2 } from "lucide-react";

interface Props {
  messages: ChatMessage[];
  onSendMessage: (message: string) => void;
  isLoading: boolean;
}

export function ChatInterface({ messages, onSendMessage, isLoading }: Props) {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <Card className="flex flex-col h-full">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {messages.map((msg, idx) => (
          <MessageBubble key={idx} message={msg} />
        ))}

        {isLoading && (
          <div className="flex items-center gap-2 text-gray-500">
            <Loader2 className="animate-spin" size={16} />
            <span className="text-sm">Analyzing regulations...</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="border-t p-4">
        <ChatInput onSend={onSendMessage} disabled={isLoading} />
      </div>
    </Card>
  );
}
