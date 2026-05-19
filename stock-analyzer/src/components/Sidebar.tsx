"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Search,
  ScanLine,
  ShieldAlert,
  BookOpen,
  Settings,
  Zap,
  TrendingUp,
} from "lucide-react";
import { clsx } from "clsx";

const navItems = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard },
  { href: "/analyze", label: "Analyze Stock", icon: Search },
  { href: "/screener", label: "Stock Screener", icon: ScanLine },
  { href: "/traps", label: "Trap Detector", icon: ShieldAlert },
  { href: "/research", label: "AI Research", icon: BookOpen },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="fixed top-0 left-0 h-screen w-[240px] bg-[#0d1321] border-r border-[#1e2d3d] flex flex-col z-50">
      <div className="p-5 border-b border-[#1e2d3d]">
        <Link href="/" className="flex items-center gap-3 group">
          <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center shadow-lg shadow-blue-500/20">
            <TrendingUp className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-white tracking-tight">StockLens</h1>
            <p className="text-[10px] text-slate-500 font-medium tracking-widest uppercase">AI Analysis</p>
          </div>
        </Link>
      </div>

      <nav className="flex-1 py-4 px-3 space-y-1">
        {navItems.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={clsx(
                "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200",
                isActive
                  ? "bg-blue-500/10 text-blue-400 border border-blue-500/20"
                  : "text-slate-400 hover:text-slate-200 hover:bg-white/5 border border-transparent"
              )}
            >
              <item.icon className={clsx("w-[18px] h-[18px]", isActive && "text-blue-400")} />
              {item.label}
              {item.label === "Trap Detector" && (
                <span className="ml-auto w-2 h-2 rounded-full bg-red-500 animate-pulse" />
              )}
            </Link>
          );
        })}
      </nav>

      <div className="p-3 mx-3 mb-3 rounded-lg bg-gradient-to-br from-blue-500/10 to-purple-500/10 border border-blue-500/20">
        <div className="flex items-center gap-2 mb-2">
          <Zap className="w-4 h-4 text-yellow-400" />
          <span className="text-xs font-semibold text-slate-300">AI Status</span>
        </div>
        <p className="text-[11px] text-slate-500 leading-relaxed">
          Connect your API key in settings for live AI-powered analysis.
        </p>
        <Link
          href="/research"
          className="mt-2 block text-center text-xs font-medium text-blue-400 hover:text-blue-300 transition-colors"
        >
          Configure →
        </Link>
      </div>

      <div className="p-3 border-t border-[#1e2d3d]">
        <Link
          href="/research"
          className="flex items-center gap-3 px-3 py-2 rounded-lg text-sm text-slate-500 hover:text-slate-300 hover:bg-white/5 transition-colors"
        >
          <Settings className="w-4 h-4" />
          Settings
        </Link>
      </div>
    </aside>
  );
}
