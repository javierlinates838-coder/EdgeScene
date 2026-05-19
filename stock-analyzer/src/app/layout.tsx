import type { Metadata } from "next";
import "./globals.css";
import Sidebar from "@/components/Sidebar";
import StockSearch from "@/components/StockSearch";
import { Bell } from "lucide-react";

export const metadata: Metadata = {
  title: "StockLens — AI-Powered Stock Analysis",
  description: "AI-powered stock analysis, trap detection, and research platform. Make smarter investment decisions with machine learning.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="antialiased">
        <Sidebar />
        <div className="ml-[240px] min-h-screen">
          <header className="sticky top-0 z-40 bg-[#0a0e17]/80 backdrop-blur-xl border-b border-[#1e2d3d]">
            <div className="flex items-center justify-between px-6 py-3">
              <StockSearch />
              <div className="flex items-center gap-4">
                <button className="relative p-2 rounded-lg hover:bg-white/5 transition-colors">
                  <Bell className="w-5 h-5 text-slate-400" />
                  <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-blue-500 rounded-full" />
                </button>
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-xs font-bold text-white">
                    U
                  </div>
                </div>
              </div>
            </div>
          </header>
          <main className="p-6">{children}</main>
        </div>
      </body>
    </html>
  );
}
