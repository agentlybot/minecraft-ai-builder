"use client";

import { cn } from "@/lib/utils";
import { SteveAvatar } from "@/components/ui/SteveAvatar";

interface ChatBubbleProps {
  message: string;
  sender: "steve" | "user";
  timestamp?: Date;
  isTyping?: boolean;
  steveMood?: "happy" | "thinking" | "building" | "waving";
}

export function ChatBubble({
  message,
  sender,
  timestamp,
  isTyping = false,
  steveMood = "happy"
}: ChatBubbleProps) {
  const isSteve = sender === "steve";

  return (
    <div
      className={cn(
        "flex gap-3 items-end",
        isSteve ? "flex-row" : "flex-row-reverse"
      )}
    >
      {/* Avatar */}
      {isSteve && (
        <SteveAvatar
          size="sm"
          mood={isTyping ? "thinking" : steveMood}
          isAnimated={isTyping}
        />
      )}

      {/* Bubble */}
      <div
        className={cn(
          isSteve ? "chat-bubble-steve" : "chat-bubble-user",
          isTyping && "animate-pulse"
        )}
      >
        {isTyping ? (
          <div className="flex gap-2 items-center">
            <span className="text-sm">Steve is thinking</span>
            <span className="flex gap-1">
              <span className="w-2 h-2 bg-white/60 rounded-full animate-typing" style={{ animationDelay: "0ms" }} />
              <span className="w-2 h-2 bg-white/60 rounded-full animate-typing" style={{ animationDelay: "150ms" }} />
              <span className="w-2 h-2 bg-white/60 rounded-full animate-typing" style={{ animationDelay: "300ms" }} />
            </span>
          </div>
        ) : (
          <p className="whitespace-pre-wrap">{message}</p>
        )}
      </div>

      {/* User avatar placeholder */}
      {!isSteve && (
        <div className="w-10 h-10 rounded-full bg-craft-water-light flex items-center justify-center text-lg font-bold text-white">
          A
        </div>
      )}
    </div>
  );
}
