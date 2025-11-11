import { ChatMessage } from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { FileText } from "lucide-react";
import { cn } from "@/lib/utils";

interface Props {
  message: ChatMessage;
}

export function MessageBubble({ message }: Props) {
  const isUser = message.role === "user";

  return (
    <div className={cn("flex gap-3", isUser && "flex-row-reverse")}>
      {/* Avatar */}
      <div
        className={cn(
          "w-8 h-8 rounded-full flex items-center justify-center shrink-0",
          isUser ? "bg-accent text-white" : "bg-gray-200 text-gray-600"
        )}
      >
        {isUser ? "U" : "AI"}
      </div>

      {/* Message Content */}
      <div
        className={cn("flex-1 max-w-2xl", isUser && "flex flex-col items-end")}
      >
        <div
          className={cn(
            "rounded-2xl px-4 py-3",
            isUser ? "bg-accent text-white" : "bg-gray-100 text-text-dark"
          )}
        >
          <p className="text-sm leading-relaxed whitespace-pre-wrap">
            {message.content}
          </p>
        </div>

        {/* Assistant metadata */}
        {!isUser && message.confidence && (
          <div className="mt-2 flex items-center gap-2">
            <Badge variant="outline" className="text-xs">
              {message.confidence}% confident
            </Badge>
          </div>
        )}

        {/* Sources */}
        {!isUser && message.sources && message.sources.length > 0 && (
          <div className="mt-3 space-y-2">
            <p className="text-xs text-gray-500 font-medium">Sources:</p>
            {message.sources.map((source, idx) => (
              <div
                key={idx}
                className="flex items-center gap-2 text-xs text-gray-600 bg-white border rounded-lg p-2"
              >
                <FileText size={14} />
                <span className="flex-1">
                  {source.type === "circular" ? source.title : source.name}
                </span>
                {source.date && (
                  <span className="text-gray-400">{source.date}</span>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
