"use client";

import Link from "next/link";
import { useState } from "react";
import { ChatInterface } from "@/components/chat/ChatInterface";
import { SteveAvatar } from "@/components/ui/SteveAvatar";

export default function DashboardPage() {
  const [selectedServer, setSelectedServer] = useState("my-server");

  // Mock data - will come from Supabase
  const user = {
    name: "Young Architect",
    buildsRemaining: 4,
    tier: "free" as const,
  };

  const servers = [
    { id: "my-server", name: "My Creative World", status: "online" as const },
    { id: "friend-server", name: "Friend's Server", status: "offline" as const },
  ];

  return (
    <div className="min-h-screen bg-craft-dark bg-pixel-grid">
      {/* Header */}
      <header className="border-b border-craft-stone-dark bg-craft-dark-lighter">
        <div className="section-container py-4">
          <div className="flex items-center justify-between">
            {/* Logo */}
            <Link href="/dashboard" className="flex items-center gap-3">
              <span className="text-2xl">🏗️</span>
              <span className="font-display text-lg text-craft-gold">
                Craft Architect
              </span>
            </Link>

            {/* Builds Remaining */}
            <div className="flex items-center gap-6">
              <div className="flex items-center gap-2">
                <span className="text-craft-stone-light">Builds left:</span>
                <span className="text-xl font-bold text-craft-gold">
                  {user.buildsRemaining}
                </span>
                {user.tier === "free" && (
                  <Link
                    href="/pricing"
                    className="text-sm text-craft-grass-light hover:underline"
                  >
                    Get more
                  </Link>
                )}
              </div>

              {/* User Menu */}
              <div className="flex items-center gap-3">
                <span className={`badge-${user.tier}`}>
                  {user.tier.charAt(0).toUpperCase() + user.tier.slice(1)}
                </span>
                <div className="w-10 h-10 rounded-full bg-craft-water flex items-center justify-center text-white font-bold">
                  {user.name.charAt(0)}
                </div>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="flex">
        {/* Sidebar */}
        <aside className="w-64 min-h-[calc(100vh-73px)] border-r border-craft-stone-dark bg-craft-dark-lighter p-4">
          <nav className="space-y-2">
            <Link href="/dashboard" className="nav-link-active">
              <span className="text-xl">🔨</span>
              Build
            </Link>
            <Link href="/dashboard/servers" className="nav-link">
              <span className="text-xl">🖥️</span>
              Servers
            </Link>
            <Link href="/dashboard/history" className="nav-link">
              <span className="text-xl">📜</span>
              History
            </Link>
            <Link href="/dashboard/settings" className="nav-link">
              <span className="text-xl">⚙️</span>
              Settings
            </Link>
          </nav>

          {/* Server Selector */}
          <div className="mt-8">
            <h3 className="text-sm font-semibold text-craft-stone-light mb-3 px-4">
              Active Server
            </h3>
            <select
              value={selectedServer}
              onChange={(e) => setSelectedServer(e.target.value)}
              className="input-pixel text-base"
            >
              {servers.map((server) => (
                <option key={server.id} value={server.id}>
                  {server.status === "online" ? "🟢" : "🔴"} {server.name}
                </option>
              ))}
            </select>
            <Link
              href="/dashboard/servers"
              className="text-sm text-craft-grass-light hover:underline block mt-2 px-4"
            >
              + Add server
            </Link>
          </div>

          {/* Quick Tips */}
          <div className="mt-8 card-pixel">
            <div className="flex items-start gap-3">
              <SteveAvatar size="sm" mood="happy" />
              <div>
                <h4 className="font-bold text-craft-cream text-sm">Pro Tips!</h4>
                <ul className="text-xs text-craft-stone-light mt-1 space-y-1">
                  <li>• &quot;cozy oak cottage with a garden&quot;</li>
                  <li>• &quot;medieval castle with moat and drawbridge&quot;</li>
                  <li>• &quot;village market with stalls and fountain&quot;</li>
                  <li>• &quot;farm with windmill and animal pens&quot;</li>
                  <li>• &quot;wizard tower with dome and spire&quot;</li>
                </ul>
              </div>
            </div>
          </div>
        </aside>

        {/* Main Content */}
        <main className="flex-1 p-6">
          <div className="max-w-4xl mx-auto">
            <h1 className="text-2xl font-bold text-craft-cream mb-6">
              What shall we build today?
            </h1>
            <ChatInterface />
          </div>
        </main>
      </div>
    </div>
  );
}
