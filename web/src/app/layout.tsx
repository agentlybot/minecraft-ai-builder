import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Craft Architect - AI-Powered Minecraft Builder",
  description: "Tell Steve what to build and watch it appear in your Minecraft world! AI-powered building for young architects.",
  keywords: ["minecraft", "builder", "AI", "kids", "gaming", "creative"],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="font-body antialiased">
        {children}
      </body>
    </html>
  );
}
