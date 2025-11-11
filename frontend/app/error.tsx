"use client";

import { useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { AlertTriangle } from "lucide-react";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error("Application error:", error);
  }, [error]);

  return (
    <div className="h-screen w-full flex items-center justify-center bg-background-light p-4">
      <Card className="max-w-md p-8 text-center">
        <div className="w-16 h-16 rounded-full bg-critical/10 flex items-center justify-center mx-auto mb-4">
          <AlertTriangle className="text-critical" size={32} />
        </div>
        <h2 className="text-2xl font-heading font-bold text-text-dark mb-2">
          Something went wrong
        </h2>
        <p className="text-gray-600 mb-6">
          {error.message || "An unexpected error occurred. Please try again."}
        </p>
        <Button onClick={reset} className="bg-gradient-accent">
          Try Again
        </Button>
      </Card>
    </div>
  );
}
