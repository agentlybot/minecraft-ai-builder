"use client";

import { cn } from "@/lib/utils";

interface SteveAvatarProps {
  size?: "sm" | "md" | "lg" | "xl";
  isAnimated?: boolean;
  mood?: "happy" | "thinking" | "building" | "waving";
  className?: string;
}

export function SteveAvatar({
  size = "md",
  isAnimated = false,
  mood = "happy",
  className
}: SteveAvatarProps) {
  const sizes = {
    sm: "w-12 h-12",
    md: "w-20 h-20",
    lg: "w-32 h-32",
    xl: "w-48 h-48",
  };

  // SVG-based Steve face for consistent rendering
  return (
    <div
      className={cn(
        "relative",
        sizes[size],
        isAnimated && "animate-float",
        className
      )}
    >
      {/* Steve's face - pixel art style */}
      <svg
        viewBox="0 0 64 64"
        className="w-full h-full"
        style={{ imageRendering: "pixelated" }}
      >
        {/* Face background (skin) */}
        <rect x="8" y="8" width="48" height="48" fill="#c79a6b" />

        {/* Hair */}
        <rect x="8" y="8" width="48" height="12" fill="#3b2815" />
        <rect x="8" y="8" width="8" height="24" fill="#3b2815" />
        <rect x="48" y="8" width="8" height="24" fill="#3b2815" />

        {/* Eyes */}
        <rect x="16" y="24" width="8" height="8" fill="#ffffff" />
        <rect x="40" y="24" width="8" height="8" fill="#ffffff" />
        <rect x="18" y="26" width="4" height="4" fill="#614126" />
        <rect x="42" y="26" width="4" height="4" fill="#614126" />

        {/* Nose */}
        <rect x="28" y="32" width="8" height="4" fill="#a07553" />

        {/* Mouth - changes based on mood */}
        {mood === "happy" && (
          <>
            <rect x="24" y="40" width="16" height="4" fill="#6b4423" />
            <rect x="20" y="40" width="4" height="4" fill="#a07553" />
            <rect x="40" y="40" width="4" height="4" fill="#a07553" />
          </>
        )}
        {mood === "thinking" && (
          <rect x="24" y="42" width="16" height="2" fill="#6b4423" />
        )}
        {mood === "building" && (
          <>
            <rect x="22" y="40" width="20" height="6" fill="#6b4423" />
            <rect x="26" y="42" width="12" height="2" fill="#ffffff" />
          </>
        )}
        {mood === "waving" && (
          <>
            <rect x="24" y="38" width="16" height="6" fill="#6b4423" />
            <rect x="28" y="40" width="8" height="2" fill="#a07553" />
          </>
        )}

        {/* Beard shadow */}
        <rect x="16" y="48" width="32" height="8" fill="#3b2815" opacity="0.3" />
      </svg>

      {/* Speech indicator when thinking */}
      {mood === "thinking" && (
        <div className="absolute -top-2 -right-2 flex gap-1">
          <span className="w-2 h-2 bg-craft-grass rounded-full animate-typing" style={{ animationDelay: "0ms" }} />
          <span className="w-2 h-2 bg-craft-grass rounded-full animate-typing" style={{ animationDelay: "200ms" }} />
          <span className="w-2 h-2 bg-craft-grass rounded-full animate-typing" style={{ animationDelay: "400ms" }} />
        </div>
      )}

      {/* Pickaxe when building */}
      {mood === "building" && (
        <div className="absolute -bottom-2 -right-4 text-3xl animate-bounce">
          ⛏️
        </div>
      )}
    </div>
  );
}
