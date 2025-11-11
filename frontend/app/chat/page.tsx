"use client";

import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { MainLayout } from "@/components/layout/main-layout";
import { ChatInterface } from "@/components/chat/chat-interface";
import { sendChatMessage, ChatMessage } from "@/lib/api";

export default function ChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: "assistant",
      content:
        "Hi! I'm your compliance assistant. Ask me anything about RBI regulations, policy requirements, or recent circulars.",
      confidence: 100,
    },
  ]);

  const mutation = useMutation({
    mutationFn: sendChatMessage,
    onSuccess: (data) => {
      setMessages((prev) => [...prev, data]);
    },
  });

  const handleSendMessage = (query: string) => {
    // Add user message immediately
    setMessages((prev) => [...prev, { role: "user", content: query }]);

    // Send to API
    mutation.mutate(query);
  };

  return (
    <MainLayout>
      <div className="max-w-5xl mx-auto h-[calc(100vh-12rem)]">
        <div className="mb-6">
          <h1 className="text-4xl font-heading font-extrabold text-text-dark mb-2">
            Compliance Assistant
          </h1>
          <p className="text-gray-600">
            RAG-powered AI trained on RBI circulars and your policies
          </p>
        </div>

        <ChatInterface
          messages={messages}
          onSendMessage={handleSendMessage}
          isLoading={mutation.isPending}
        />
      </div>
    </MainLayout>
  );
}
