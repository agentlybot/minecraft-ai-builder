"use client";

import { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/Button";
import { ChatBubble } from "@/components/chat/ChatBubble";
import { SteveAvatar } from "@/components/ui/SteveAvatar";

interface Message {
  id: string;
  content: string;
  sender: "steve" | "user";
  timestamp: Date;
  steveMood?: "happy" | "thinking" | "building" | "waving";
  showFeedback?: boolean;
  buildDescription?: string;
}

interface FeedbackCardProps {
  buildDescription: string;
  onSubmit: (rating: number, comment: string) => void;
  onDismiss: () => void;
}

function FeedbackCard({ buildDescription, onSubmit, onDismiss }: FeedbackCardProps) {
  const [rating, setRating] = useState<number | null>(null);
  const [comment, setComment] = useState("");
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = () => {
    if (rating !== null) {
      onSubmit(rating, comment);
      setSubmitted(true);
    }
  };

  if (submitted) {
    return (
      <div className="bg-craft-grass/20 border-2 border-craft-grass rounded-lg p-4 mt-2">
        <p className="text-craft-grass-light text-center font-semibold">
          Thanks for your feedback! It helps Steve get better! 💚
        </p>
      </div>
    );
  }

  return (
    <div className="bg-craft-dark border-2 border-craft-stone rounded-lg p-4 mt-2 space-y-3">
      <p className="text-craft-cream font-semibold text-sm">How did this build turn out?</p>

      {/* Star Rating */}
      <div className="flex gap-2 justify-center">
        {[1, 2, 3, 4, 5].map((star) => (
          <button
            key={star}
            onClick={() => setRating(star)}
            className={`text-2xl transition-transform hover:scale-110 ${
              rating !== null && star <= rating
                ? "text-craft-gold"
                : "text-craft-stone-dark hover:text-craft-gold/50"
            }`}
          >
            ★
          </button>
        ))}
      </div>

      {/* Rating Labels */}
      {rating !== null && (
        <p className="text-center text-sm text-craft-stone-light">
          {rating === 1 && "Needs work 😕"}
          {rating === 2 && "Could be better"}
          {rating === 3 && "It's okay 👍"}
          {rating === 4 && "Pretty good!"}
          {rating === 5 && "Amazing! 🎉"}
        </p>
      )}

      {/* Optional Comment */}
      <textarea
        value={comment}
        onChange={(e) => setComment(e.target.value)}
        placeholder="Any details? (e.g., 'roof was flat', 'needs more windows')"
        className="w-full p-2 bg-craft-dark-lighter border border-craft-stone-dark rounded text-sm text-craft-cream placeholder-craft-stone resize-none"
        rows={2}
      />

      {/* Submit/Skip Buttons */}
      <div className="flex gap-2">
        <Button
          variant="primary"
          size="sm"
          onClick={handleSubmit}
          disabled={rating === null}
          className="flex-1"
        >
          Submit
        </Button>
        <Button
          variant="secondary"
          size="sm"
          onClick={onDismiss}
          className="flex-1"
        >
          Skip
        </Button>
      </div>
    </div>
  );
}

const STEVE_GREETINGS = [
  "Hey there, Architect! What amazing thing shall we build today? 🏰",
  "Hello, friend! I've got my pickaxe ready. What's the plan? ⛏️",
  "Welcome back! Ready to create something awesome together? ✨",
];

const STEVE_BUILDING_MESSAGES = [
  "On it! Let me grab my tools... 🔨",
  "Great idea! This is going to look awesome!",
  "Ooh, I love building those! Give me a moment...",
];

const STEVE_COMPLETE_MESSAGES = [
  "Ta-da! Your build is ready! Go check it out! 🎉",
  "All done! I hope you like it! ✨",
  "Finished! That was fun to build! 🏗️",
];

export function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isBuilding, setIsBuilding] = useState(false);
  const [buildProgress, setBuildProgress] = useState(0);
  const [isHydrated, setIsHydrated] = useState(false);
  const [pendingFeedback, setPendingFeedback] = useState<{id: string; description: string} | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  // Initialize welcome message after hydration to avoid mismatch
  useEffect(() => {
    if (!isHydrated) {
      setIsHydrated(true);
      setMessages([
        {
          id: "welcome",
          content: STEVE_GREETINGS[Math.floor(Math.random() * STEVE_GREETINGS.length)],
          sender: "steve",
          timestamp: new Date(),
          steveMood: "waving",
        },
      ]);
    }
  }, [isHydrated]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isBuilding) return;

    const buildDescription = input;
    const userMessage: Message = {
      id: Date.now().toString(),
      content: input,
      sender: "user",
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsBuilding(true);
    setBuildProgress(0);

    // Add Steve's "building" response
    const buildingMessage: Message = {
      id: (Date.now() + 1).toString(),
      content: STEVE_BUILDING_MESSAGES[Math.floor(Math.random() * STEVE_BUILDING_MESSAGES.length)],
      sender: "steve",
      timestamp: new Date(),
      steveMood: "building",
    };
    setMessages((prev) => [...prev, buildingMessage]);

    // Animate progress while building
    const progressInterval = setInterval(() => {
      setBuildProgress((prev) => {
        if (prev >= 90) return 90; // Cap at 90% until complete
        return prev + Math.random() * 10 + 3;
      });
    }, 500);

    try {
      // Call the build API
      const response = await fetch("/api/build", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ description: buildDescription }),
      });

      clearInterval(progressInterval);
      setBuildProgress(100);

      if (response.ok) {
        const result = await response.json();
        const messageId = (Date.now() + 2).toString();
        const completeMessage: Message = {
          id: messageId,
          content: STEVE_COMPLETE_MESSAGES[Math.floor(Math.random() * STEVE_COMPLETE_MESSAGES.length)] +
            `\n\n📊 Blocks placed: ${result.blocks_placed}\n⏱️ Time: ${result.execution_time.toFixed(1)} seconds`,
          sender: "steve",
          timestamp: new Date(),
          steveMood: "happy",
          showFeedback: true,
          buildDescription: buildDescription,
        };
        setMessages((prev) => [...prev, completeMessage]);
        setPendingFeedback({ id: messageId, description: buildDescription });
      } else {
        const error = await response.json();
        const errorMessage: Message = {
          id: (Date.now() + 2).toString(),
          content: `Oops! Something went wrong... 😅\n\n${error.error || "Could not connect to the Minecraft server. Make sure the server is running!"}`,
          sender: "steve",
          timestamp: new Date(),
          steveMood: "thinking",
        };
        setMessages((prev) => [...prev, errorMessage]);
      }
    } catch (error) {
      clearInterval(progressInterval);
      setBuildProgress(0);
      const errorMessage: Message = {
        id: (Date.now() + 2).toString(),
        content: "Hmm, I can't reach the build server right now. Make sure the Python API is running! 🔧",
        sender: "steve",
        timestamp: new Date(),
        steveMood: "thinking",
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsBuilding(false);
      setBuildProgress(0);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleFeedbackSubmit = async (rating: number, comment: string) => {
    if (!pendingFeedback) return;

    // Store feedback (later: send to API/database)
    const feedback = {
      buildDescription: pendingFeedback.description,
      rating,
      comment,
      timestamp: new Date().toISOString(),
    };

    // For now, log to console and store in localStorage
    console.log("Build Feedback:", feedback);

    // Store in localStorage for later analysis
    const existingFeedback = JSON.parse(localStorage.getItem("buildFeedback") || "[]");
    existingFeedback.push(feedback);
    localStorage.setItem("buildFeedback", JSON.stringify(existingFeedback));

    // Add Steve's response to feedback
    const responseMessages = {
      1: "I'm sorry it didn't turn out well. I'll try harder next time! 😔",
      2: "Thanks for letting me know. I'll work on improving! 💪",
      3: "Good to know! I'll keep practicing. 👍",
      4: "Yay! Glad you liked it! 😊",
      5: "Woohoo! That makes me so happy! 🎉",
    };

    const feedbackResponse: Message = {
      id: Date.now().toString(),
      content: responseMessages[rating as keyof typeof responseMessages],
      sender: "steve",
      timestamp: new Date(),
      steveMood: rating >= 4 ? "happy" : "thinking",
    };

    setMessages((prev) => [...prev, feedbackResponse]);
    setPendingFeedback(null);

    // Update the message to hide feedback card
    setMessages((prev) =>
      prev.map((msg) =>
        msg.id === pendingFeedback.id ? { ...msg, showFeedback: false } : msg
      )
    );
  };

  const handleFeedbackDismiss = () => {
    if (pendingFeedback) {
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === pendingFeedback.id ? { ...msg, showFeedback: false } : msg
        )
      );
      setPendingFeedback(null);
    }
  };

  return (
    <div className="flex flex-col h-full max-h-[80vh] bg-craft-dark-lighter rounded-pixel-lg border-2 border-craft-stone-dark overflow-hidden">
      {/* Header */}
      <div className="flex items-center gap-4 p-4 border-b-2 border-craft-stone-dark bg-craft-dark">
        <SteveAvatar size="md" mood={isBuilding ? "building" : "happy"} isAnimated={isBuilding} />
        <div>
          <h2 className="text-xl font-bold text-craft-cream">Steve the Builder</h2>
          <p className="text-craft-stone-light text-sm">
            {isBuilding ? "Building your creation..." : "Ready to build!"}
          </p>
        </div>
        <div className="ml-auto flex items-center gap-2">
          <span className={isBuilding ? "status-connecting" : "status-online"} />
          <span className="text-sm text-craft-stone-light">
            {isBuilding ? "Building" : "Online"}
          </span>
        </div>
      </div>

      {/* Build Progress */}
      {isBuilding && (
        <div className="px-4 py-2 bg-craft-dark/50">
          <div className="flex items-center gap-3">
            <span className="text-sm text-craft-grass-light">Building...</span>
            <div className="flex-1 progress-bar">
              <div
                className="progress-bar-fill"
                style={{ width: `${Math.min(buildProgress, 100)}%` }}
              />
            </div>
            <span className="text-sm text-craft-stone-light">
              {Math.round(Math.min(buildProgress, 100))}%
            </span>
          </div>
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 scrollbar-hide">
        {messages.map((message) => (
          <div key={message.id}>
            <ChatBubble
              message={message.content}
              sender={message.sender}
              timestamp={message.timestamp}
              steveMood={message.steveMood}
            />
            {message.showFeedback && message.buildDescription && (
              <FeedbackCard
                buildDescription={message.buildDescription}
                onSubmit={handleFeedbackSubmit}
                onDismiss={handleFeedbackDismiss}
              />
            )}
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t-2 border-craft-stone-dark bg-craft-dark">
        <div className="flex gap-3">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Tell Steve what to build..."
            className="input-pixel flex-1"
            disabled={isBuilding}
          />
          <Button
            variant="gold"
            size="lg"
            onClick={handleSend}
            disabled={!input.trim() || isBuilding}
            isLoading={isBuilding}
          >
            {isBuilding ? "Building..." : "🔨 Build!"}
          </Button>
        </div>
        <p className="text-sm text-craft-stone-light mt-2 text-center">
          Press Enter to send • Be descriptive for best results!
        </p>
      </div>
    </div>
  );
}
