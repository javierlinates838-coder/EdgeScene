"use client";

import { clsx } from "clsx";

const signalConfig: Record<string, { color: string; bg: string; border: string; glow: string }> = {
  STRONG_BUY: { color: "text-emerald-300", bg: "bg-emerald-500/10", border: "border-emerald-500/30", glow: "shadow-emerald-500/20" },
  BUY: { color: "text-green-400", bg: "bg-green-500/10", border: "border-green-500/30", glow: "shadow-green-500/10" },
  HOLD: { color: "text-yellow-400", bg: "bg-yellow-500/10", border: "border-yellow-500/30", glow: "shadow-yellow-500/10" },
  SELL: { color: "text-orange-400", bg: "bg-orange-500/10", border: "border-orange-500/30", glow: "shadow-orange-500/10" },
  STRONG_SELL: { color: "text-red-400", bg: "bg-red-500/10", border: "border-red-500/30", glow: "shadow-red-500/20" },
};

const severityConfig: Record<string, { color: string; bg: string }> = {
  LOW: { color: "text-green-400", bg: "bg-green-500/10" },
  MEDIUM: { color: "text-yellow-400", bg: "bg-yellow-500/10" },
  HIGH: { color: "text-orange-400", bg: "bg-orange-500/10" },
  CRITICAL: { color: "text-red-400", bg: "bg-red-500/10" },
};

export function SignalBadge({ signal, size = "md" }: { signal: string; size?: "sm" | "md" | "lg" }) {
  const config = signalConfig[signal] || signalConfig.HOLD;
  return (
    <span
      className={clsx(
        "inline-flex items-center font-bold rounded-md border shadow-sm",
        config.color, config.bg, config.border, config.glow,
        size === "sm" && "px-2 py-0.5 text-[10px]",
        size === "md" && "px-3 py-1 text-xs",
        size === "lg" && "px-4 py-1.5 text-sm"
      )}
    >
      {signal.replace("_", " ")}
    </span>
  );
}

export function SeverityBadge({ severity }: { severity: string }) {
  const config = severityConfig[severity] || severityConfig.MEDIUM;
  return (
    <span className={clsx("inline-flex items-center px-2 py-0.5 text-[10px] font-bold rounded-md", config.color, config.bg)}>
      {severity}
    </span>
  );
}

export function ScoreMeter({ score, label }: { score: number; label?: string }) {
  const color = score >= 80 ? "#10b981" : score >= 60 ? "#f59e0b" : score >= 40 ? "#f97316" : "#ef4444";

  return (
    <div className="flex flex-col items-center gap-1">
      <div className="relative w-16 h-16">
        <svg className="w-full h-full -rotate-90" viewBox="0 0 36 36">
          <circle cx="18" cy="18" r="15.5" fill="none" stroke="#1e2d3d" strokeWidth="3" />
          <circle
            cx="18" cy="18" r="15.5" fill="none" stroke={color} strokeWidth="3"
            strokeDasharray={`${score * 0.975} 97.5`}
            strokeLinecap="round"
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-sm font-bold" style={{ color }}>{score}</span>
        </div>
      </div>
      {label && <span className="text-[10px] text-slate-500 font-medium">{label}</span>}
    </div>
  );
}
