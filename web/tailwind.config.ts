import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Minecraft-inspired palette
        craft: {
          // Primary greens (grass/creeper inspired)
          grass: "#5D8C3E",
          "grass-light": "#7CB342",
          "grass-dark": "#3E5C29",

          // Earth tones (dirt/wood)
          dirt: "#8B5A2B",
          "dirt-light": "#A0522D",
          "dirt-dark": "#5C3D1E",
          wood: "#BA8C63",
          "wood-light": "#D4A574",

          // Stone/UI backgrounds
          stone: "#7F7F7F",
          "stone-light": "#A0A0A0",
          "stone-dark": "#4A4A4A",
          cobble: "#6B6B6B",

          // Sky/water accents
          sky: "#87CEEB",
          "sky-dark": "#5BA3C6",
          water: "#3F76E4",
          "water-light": "#6B9FFF",

          // UI colors
          gold: "#FFD700",
          "gold-dark": "#DAA520",
          redstone: "#FF3B3B",
          "redstone-dark": "#CC0000",
          diamond: "#4AEDD9",
          emerald: "#17DD62",

          // Backgrounds
          dark: "#1a1a2e",
          "dark-lighter": "#252542",
          cream: "#F5F5DC",
        },
      },
      fontFamily: {
        // Pixel-friendly but readable fonts
        display: ["'Press Start 2P'", "monospace"],
        body: ["'Nunito'", "system-ui", "sans-serif"],
        mono: ["'JetBrains Mono'", "monospace"],
      },
      fontSize: {
        // Kid-friendly minimum sizes
        "kid-sm": ["1rem", { lineHeight: "1.5" }],
        "kid-base": ["1.125rem", { lineHeight: "1.6" }],
        "kid-lg": ["1.25rem", { lineHeight: "1.5" }],
        "kid-xl": ["1.5rem", { lineHeight: "1.4" }],
        "kid-2xl": ["2rem", { lineHeight: "1.3" }],
        "kid-3xl": ["2.5rem", { lineHeight: "1.2" }],
      },
      spacing: {
        // Touch-friendly spacing
        "touch": "44px",
        "touch-lg": "56px",
      },
      borderRadius: {
        "pixel": "4px",
        "pixel-lg": "8px",
        "bubble": "20px",
      },
      boxShadow: {
        "pixel": "4px 4px 0px 0px rgba(0,0,0,0.3)",
        "pixel-lg": "6px 6px 0px 0px rgba(0,0,0,0.3)",
        "pixel-inset": "inset 2px 2px 0px 0px rgba(255,255,255,0.2), inset -2px -2px 0px 0px rgba(0,0,0,0.2)",
        "glow-gold": "0 0 20px rgba(255, 215, 0, 0.4)",
        "glow-diamond": "0 0 20px rgba(74, 237, 217, 0.4)",
        "glow-emerald": "0 0 20px rgba(23, 221, 98, 0.4)",
      },
      animation: {
        "bounce-slow": "bounce 2s infinite",
        "pulse-glow": "pulse-glow 2s ease-in-out infinite",
        "float": "float 3s ease-in-out infinite",
        "pixel-shake": "pixel-shake 0.5s ease-in-out",
        "slide-up": "slide-up 0.3s ease-out",
        "fade-in": "fade-in 0.3s ease-out",
        "typing": "typing 1.5s ease-in-out infinite",
      },
      keyframes: {
        "pulse-glow": {
          "0%, 100%": { boxShadow: "0 0 20px rgba(255, 215, 0, 0.4)" },
          "50%": { boxShadow: "0 0 40px rgba(255, 215, 0, 0.6)" },
        },
        "float": {
          "0%, 100%": { transform: "translateY(0px)" },
          "50%": { transform: "translateY(-10px)" },
        },
        "pixel-shake": {
          "0%, 100%": { transform: "translateX(0)" },
          "25%": { transform: "translateX(-4px)" },
          "75%": { transform: "translateX(4px)" },
        },
        "slide-up": {
          "0%": { transform: "translateY(20px)", opacity: "0" },
          "100%": { transform: "translateY(0)", opacity: "1" },
        },
        "fade-in": {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        "typing": {
          "0%": { opacity: "0.3" },
          "50%": { opacity: "1" },
          "100%": { opacity: "0.3" },
        },
      },
    },
  },
  plugins: [],
};

export default config;
