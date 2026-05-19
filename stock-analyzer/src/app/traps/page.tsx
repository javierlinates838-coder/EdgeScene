"use client";

import { useState } from "react";
import {
  ShieldAlert, AlertTriangle, Radio, Eye, Clock,
  ChevronDown, ChevronUp, Search, Filter, Zap,
  Skull, RefreshCw, Bot, Crosshair, Flame, Ghost, TrendingDown,
} from "lucide-react";
import { trapExamples } from "@/lib/mock-data";
import { SeverityBadge } from "@/components/SignalBadge";
import { TrapIndicator } from "@/lib/types";

const trapIcons: Record<string, React.ReactNode> = {
  PUMP_DUMP: <Flame className="w-5 h-5 text-red-400" />,
  WASH_TRADE: <RefreshCw className="w-5 h-5 text-orange-400" />,
  SPOOFING: <Ghost className="w-5 h-5 text-purple-400" />,
  LAYERING: <Bot className="w-5 h-5 text-blue-400" />,
  FRONT_RUNNING: <Crosshair className="w-5 h-5 text-cyan-400" />,
  SHORT_SQUEEZE_TRAP: <Skull className="w-5 h-5 text-yellow-400" />,
  FOMO_TRAP: <Flame className="w-5 h-5 text-orange-400" />,
  DEAD_CAT_BOUNCE: <TrendingDown className="w-5 h-5 text-red-400" />,
};

const trapDescriptions: Record<string, string> = {
  PUMP_DUMP: "Coordinated buying to inflate price, followed by mass selling. Often promoted through social media, newsletters, or chat groups.",
  WASH_TRADE: "Trading with yourself or affiliated accounts to create artificial volume and the illusion of market interest.",
  SPOOFING: "Placing large orders with the intent to cancel before execution, manipulating other traders' perception of supply/demand.",
  LAYERING: "Placing multiple orders at different price levels to create a false impression of market depth.",
  FRONT_RUNNING: "Trading based on advance knowledge of pending orders or non-public information.",
  SHORT_SQUEEZE_TRAP: "Manufactured short squeeze where insiders profit from the volatility while retail traders get trapped at the top.",
  FOMO_TRAP: "Social media-driven buying frenzy that creates unsustainable price levels, trapping late buyers.",
  DEAD_CAT_BOUNCE: "Brief recovery in a declining stock that fools buyers into thinking a reversal has occurred.",
};

function TrapCard({ trap, expanded, onToggle }: { trap: TrapIndicator; expanded: boolean; onToggle: () => void }) {
  const severityColors: Record<string, string> = {
    CRITICAL: "border-red-500/30 bg-red-500/5",
    HIGH: "border-orange-500/20 bg-orange-500/5",
    MEDIUM: "border-yellow-500/20 bg-yellow-500/5",
    LOW: "border-green-500/20 bg-green-500/5",
  };

  return (
    <div className={`glass-card border ${severityColors[trap.severity]} transition-all`}>
      <button onClick={onToggle} className="w-full p-5 text-left">
        <div className="flex items-start gap-4">
          <div className="w-10 h-10 rounded-lg bg-white/5 flex items-center justify-center shrink-0">
            {trapIcons[trap.type] || <AlertTriangle className="w-5 h-5 text-yellow-400" />}
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-3 mb-1">
              <h3 className="text-sm font-bold text-white">{trap.type.replace(/_/g, " ")}</h3>
              <SeverityBadge severity={trap.severity} />
              {trap.severity === "CRITICAL" && (
                <span className="flex items-center gap-1 text-[10px] font-bold text-red-400 animate-pulse">
                  <Radio className="w-3 h-3" /> ACTIVE
                </span>
              )}
            </div>
            <p className="text-xs text-slate-400 leading-relaxed line-clamp-2">{trap.description}</p>
          </div>
          <div className="flex items-center gap-3 shrink-0">
            <span className="text-[10px] text-slate-600 flex items-center gap-1">
              <Clock className="w-3 h-3" />
              {new Date(trap.detectedAt).toLocaleTimeString("en-US", { hour: "numeric", minute: "2-digit" })}
            </span>
            {expanded ? <ChevronUp className="w-4 h-4 text-slate-500" /> : <ChevronDown className="w-4 h-4 text-slate-500" />}
          </div>
        </div>
      </button>

      {expanded && (
        <div className="px-5 pb-5 pt-0 space-y-4 border-t border-[#1e2d3d] mt-0 pt-4">
          <div>
            <h4 className="text-[10px] text-slate-500 font-semibold uppercase tracking-wider mb-2">How This Trap Works</h4>
            <p className="text-xs text-slate-400 leading-relaxed">
              {trapDescriptions[trap.type] || "Analysis in progress..."}
            </p>
          </div>
          <div>
            <h4 className="text-[10px] text-slate-500 font-semibold uppercase tracking-wider mb-2">Evidence Detected</h4>
            <div className="grid grid-cols-2 gap-2">
              {trap.evidence.map((e, i) => (
                <div key={i} className="flex items-start gap-2 p-2 rounded-lg bg-white/5">
                  <span className={`mt-0.5 w-1.5 h-1.5 rounded-full shrink-0 ${
                    trap.severity === "CRITICAL" ? "bg-red-400" :
                    trap.severity === "HIGH" ? "bg-orange-400" : "bg-yellow-400"
                  }`} />
                  <span className="text-[11px] text-slate-400">{e}</span>
                </div>
              ))}
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className="flex-1 p-3 rounded-lg bg-blue-500/5 border border-blue-500/10">
              <p className="text-[10px] text-blue-400 font-semibold mb-1">🛡️ Protection Advice</p>
              <p className="text-[11px] text-slate-400">
                {trap.severity === "CRITICAL"
                  ? "Avoid this stock entirely. Wait for the manipulation to resolve before considering any position."
                  : trap.severity === "HIGH"
                  ? "Exercise extreme caution. Only enter with strict stop-losses and reduced position size."
                  : "Monitor closely. Consider waiting for confirmation of genuine price action before acting."}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default function TrapsPage() {
  const [expandedIndex, setExpandedIndex] = useState<number | null>(0);
  const [filterSeverity, setFilterSeverity] = useState("ALL");
  const [searchQuery, setSearchQuery] = useState("");

  const filtered = trapExamples.filter((t) => {
    if (filterSeverity !== "ALL" && t.severity !== filterSeverity) return false;
    if (searchQuery && !t.type.toLowerCase().includes(searchQuery.toLowerCase()) && !t.description.toLowerCase().includes(searchQuery.toLowerCase())) return false;
    return true;
  });

  const severityCounts = {
    CRITICAL: trapExamples.filter((t) => t.severity === "CRITICAL").length,
    HIGH: trapExamples.filter((t) => t.severity === "HIGH").length,
    MEDIUM: trapExamples.filter((t) => t.severity === "MEDIUM").length,
    LOW: trapExamples.filter((t) => t.severity === "LOW").length,
  };

  return (
    <div className="space-y-6 fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-3">
            <ShieldAlert className="w-7 h-7 text-red-400" />
            Bot &amp; Trap Detector
          </h1>
          <p className="text-sm text-slate-500 mt-1">AI-powered detection of market manipulation, bots, and trading traps</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium bg-red-500/10 text-red-400 rounded-lg border border-red-500/20 animate-pulse">
            <Radio className="w-3.5 h-3.5" />
            Live Monitoring
          </span>
        </div>
      </div>

      {/* Severity Overview */}
      <div className="grid grid-cols-4 gap-4">
        {(["CRITICAL", "HIGH", "MEDIUM", "LOW"] as const).map((sev) => {
          const colors: Record<string, { bg: string; text: string; accent: string }> = {
            CRITICAL: { bg: "bg-red-500/5", text: "text-red-400", accent: "border-red-500/20" },
            HIGH: { bg: "bg-orange-500/5", text: "text-orange-400", accent: "border-orange-500/20" },
            MEDIUM: { bg: "bg-yellow-500/5", text: "text-yellow-400", accent: "border-yellow-500/20" },
            LOW: { bg: "bg-green-500/5", text: "text-green-400", accent: "border-green-500/20" },
          };
          const c = colors[sev];
          return (
            <button
              key={sev}
              onClick={() => setFilterSeverity(filterSeverity === sev ? "ALL" : sev)}
              className={`glass-card p-4 text-left transition-all ${
                filterSeverity === sev ? `${c.bg} border ${c.accent}` : ""
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <span className={`text-xs font-bold ${c.text}`}>{sev}</span>
                {sev === "CRITICAL" && severityCounts.CRITICAL > 0 && (
                  <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
                )}
              </div>
              <p className="text-2xl font-bold text-white">{severityCounts[sev]}</p>
              <p className="text-[10px] text-slate-500 mt-0.5">alerts detected</p>
            </button>
          );
        })}
      </div>

      {/* Filters */}
      <div className="flex items-center gap-3">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
          <input
            type="text" value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search traps..."
            className="w-full pl-10 pr-4 py-2 bg-[#0d1321] border border-[#1e2d3d] rounded-lg text-sm text-slate-300 placeholder:text-slate-600 focus:outline-none focus:border-blue-500/50"
          />
        </div>
        <div className="flex gap-1">
          {["ALL", "CRITICAL", "HIGH", "MEDIUM", "LOW"].map((sev) => (
            <button
              key={sev}
              onClick={() => setFilterSeverity(sev)}
              className={`px-3 py-1.5 text-xs font-medium rounded-lg transition-colors ${
                filterSeverity === sev
                  ? "bg-blue-500/20 text-blue-400 border border-blue-500/30"
                  : "text-slate-500 hover:text-slate-300 hover:bg-white/5 border border-transparent"
              }`}
            >
              {sev}
            </button>
          ))}
        </div>
      </div>

      {/* Trap Cards */}
      <div className="space-y-3">
        {filtered.map((trap, i) => (
          <TrapCard
            key={i}
            trap={trap}
            expanded={expandedIndex === i}
            onToggle={() => setExpandedIndex(expandedIndex === i ? null : i)}
          />
        ))}
        {filtered.length === 0 && (
          <div className="glass-card p-12 text-center">
            <ShieldAlert className="w-12 h-12 text-slate-600 mx-auto mb-3" />
            <p className="text-sm text-slate-500">No traps matching your filter criteria.</p>
          </div>
        )}
      </div>

      {/* Education Section */}
      <div className="glass-card p-5">
        <div className="flex items-center gap-2 mb-4">
          <Zap className="w-5 h-5 text-yellow-400" />
          <h3 className="text-sm font-bold text-white">How AI Trap Detection Works</h3>
        </div>
        <div className="grid grid-cols-3 gap-4">
          <div className="p-4 rounded-lg bg-white/5">
            <div className="w-8 h-8 rounded-lg bg-blue-500/10 flex items-center justify-center mb-3">
              <Eye className="w-4 h-4 text-blue-400" />
            </div>
            <h4 className="text-sm font-semibold text-white mb-1">Pattern Recognition</h4>
            <p className="text-xs text-slate-500 leading-relaxed">
              Our AI analyzes millions of trades in real-time, identifying patterns that match known manipulation techniques like spoofing, layering, and wash trading.
            </p>
          </div>
          <div className="p-4 rounded-lg bg-white/5">
            <div className="w-8 h-8 rounded-lg bg-purple-500/10 flex items-center justify-center mb-3">
              <Bot className="w-4 h-4 text-purple-400" />
            </div>
            <h4 className="text-sm font-semibold text-white mb-1">Bot Detection</h4>
            <p className="text-xs text-slate-500 leading-relaxed">
              Machine learning models detect automated trading bots by analyzing order timing, size patterns, and execution speed that exceed human capability.
            </p>
          </div>
          <div className="p-4 rounded-lg bg-white/5">
            <div className="w-8 h-8 rounded-lg bg-emerald-500/10 flex items-center justify-center mb-3">
              <ShieldAlert className="w-4 h-4 text-emerald-400" />
            </div>
            <h4 className="text-sm font-semibold text-white mb-1">Smart Protection</h4>
            <p className="text-xs text-slate-500 leading-relaxed">
              Get real-time alerts when traps are detected. Our system provides actionable advice on how to avoid falling victim to each type of manipulation.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
