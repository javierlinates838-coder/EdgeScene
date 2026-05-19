"use client";

import { useState } from "react";
import Link from "next/link";
import {
  TrendingUp, TrendingDown, BarChart3, Shield, Brain,
  ArrowUpRight, ArrowDownRight, Activity, Zap, Eye, ChevronRight,
} from "lucide-react";
import {
  AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer,
  BarChart, Bar,
} from "recharts";
import { marketIndices, trendingStocks, generateChartData, trapExamples } from "@/lib/mock-data";
import { SignalBadge, ScoreMeter } from "@/components/SignalBadge";

const miniChartData = generateChartData(30);

function formatLargeNumber(n: number): string {
  if (n >= 1e12) return `$${(n / 1e12).toFixed(2)}T`;
  if (n >= 1e9) return `$${(n / 1e9).toFixed(2)}B`;
  if (n >= 1e6) return `$${(n / 1e6).toFixed(1)}M`;
  return `$${n.toLocaleString()}`;
}

export default function Dashboard() {
  const [timeframe] = useState("1D");

  return (
    <div className="space-y-6 fade-in">
      {/* Market Indices */}
      <div className="grid grid-cols-4 gap-4">
        {marketIndices.map((idx) => (
          <div key={idx.symbol} className="glass-card p-4 transition-all hover:scale-[1.01]">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs text-slate-500 font-medium">{idx.name}</span>
              <span className="text-[10px] text-slate-600 font-mono">{idx.symbol}</span>
            </div>
            <div className="flex items-end justify-between">
              <div>
                <p className="text-xl font-bold text-white">{idx.value.toLocaleString("en-US", { minimumFractionDigits: 2 })}</p>
                <div className="flex items-center gap-1.5 mt-1">
                  {idx.change >= 0 ? (
                    <ArrowUpRight className="w-3.5 h-3.5 text-emerald-400" />
                  ) : (
                    <ArrowDownRight className="w-3.5 h-3.5 text-red-400" />
                  )}
                  <span className={`text-xs font-semibold ${idx.change >= 0 ? "text-emerald-400" : "text-red-400"}`}>
                    {idx.change >= 0 ? "+" : ""}{idx.change.toFixed(2)} ({idx.changePercent >= 0 ? "+" : ""}{idx.changePercent.toFixed(2)}%)
                  </span>
                </div>
              </div>
              <div className="w-20 h-10">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={miniChartData.slice(-20)}>
                    <defs>
                      <linearGradient id={`grad-${idx.symbol}`} x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor={idx.change >= 0 ? "#10b981" : "#ef4444"} stopOpacity={0.3} />
                        <stop offset="100%" stopColor={idx.change >= 0 ? "#10b981" : "#ef4444"} stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <Area
                      type="monotone" dataKey="close"
                      stroke={idx.change >= 0 ? "#10b981" : "#ef4444"}
                      fill={`url(#grad-${idx.symbol})`}
                      strokeWidth={1.5}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-12 gap-6">
        {/* Market Chart */}
        <div className="col-span-8 glass-card p-5">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-lg font-bold text-white">Market Overview</h2>
              <p className="text-xs text-slate-500 mt-0.5">S&P 500 — Intraday</p>
            </div>
            <div className="flex gap-1">
              {["1D", "1W", "1M", "3M", "1Y", "ALL"].map((tf) => (
                <button
                  key={tf}
                  className={`px-3 py-1 text-xs font-medium rounded-md transition-colors ${
                    timeframe === tf
                      ? "bg-blue-500/20 text-blue-400 border border-blue-500/30"
                      : "text-slate-500 hover:text-slate-300 hover:bg-white/5"
                  }`}
                >
                  {tf}
                </button>
              ))}
            </div>
          </div>
          <div className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={miniChartData}>
                <defs>
                  <linearGradient id="chartGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#3b82f6" stopOpacity={0.2} />
                    <stop offset="100%" stopColor="#3b82f6" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <XAxis
                  dataKey="date" axisLine={false} tickLine={false}
                  tick={{ fill: "#64748b", fontSize: 10 }}
                  tickFormatter={(v) => new Date(v).toLocaleDateString("en-US", { month: "short", day: "numeric" })}
                  interval={Math.floor(miniChartData.length / 6)}
                />
                <YAxis
                  axisLine={false} tickLine={false} width={60}
                  tick={{ fill: "#64748b", fontSize: 10 }}
                  tickFormatter={(v) => `$${v.toFixed(0)}`}
                  domain={["auto", "auto"]}
                />
                <Tooltip
                  contentStyle={{
                    background: "#1a2332",
                    border: "1px solid #1e2d3d",
                    borderRadius: "8px",
                    fontSize: "12px",
                    color: "#e2e8f0",
                  }}
                  labelFormatter={(v) => new Date(v).toLocaleDateString("en-US", { weekday: "short", month: "short", day: "numeric" })}
                  formatter={(value: unknown) => [`$${Number(value).toFixed(2)}`, "Price"]}
                />
                <Area
                  type="monotone" dataKey="close"
                  stroke="#3b82f6" fill="url(#chartGradient)"
                  strokeWidth={2}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
          <div className="h-[80px] mt-2">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={miniChartData}>
                <XAxis dataKey="date" hide />
                <YAxis hide />
                <Bar dataKey="volume" fill="#1e2d3d" radius={[2, 2, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* AI Insights Panel */}
        <div className="col-span-4 space-y-4">
          <div className="glass-card p-5">
            <div className="flex items-center gap-2 mb-4">
              <Brain className="w-5 h-5 text-purple-400" />
              <h3 className="text-sm font-bold text-white">AI Quick Insights</h3>
              <span className="ml-auto px-2 py-0.5 text-[10px] font-medium bg-purple-500/10 text-purple-400 rounded-full border border-purple-500/20">
                BETA
              </span>
            </div>
            <div className="space-y-3">
              <div className="p-3 rounded-lg bg-emerald-500/5 border border-emerald-500/10">
                <div className="flex items-center gap-2 mb-1">
                  <Zap className="w-3.5 h-3.5 text-emerald-400" />
                  <span className="text-xs font-semibold text-emerald-400">Top Pick Today</span>
                </div>
                <p className="text-sm text-slate-300">
                  <span className="font-bold text-white">NVDA</span> — AI infrastructure demand accelerating. Strong momentum with 89% confidence score.
                </p>
              </div>
              <div className="p-3 rounded-lg bg-red-500/5 border border-red-500/10">
                <div className="flex items-center gap-2 mb-1">
                  <Shield className="w-3.5 h-3.5 text-red-400" />
                  <span className="text-xs font-semibold text-red-400">Trap Alert</span>
                </div>
                <p className="text-sm text-slate-300">
                  <span className="font-bold text-white">TSLA</span> — FOMO trap detected. Volume anomaly + social media pump signals.
                </p>
              </div>
              <div className="p-3 rounded-lg bg-blue-500/5 border border-blue-500/10">
                <div className="flex items-center gap-2 mb-1">
                  <Activity className="w-3.5 h-3.5 text-blue-400" />
                  <span className="text-xs font-semibold text-blue-400">Sector Rotation</span>
                </div>
                <p className="text-sm text-slate-300">
                  Money flowing from Growth → Value. Financials and Energy showing relative strength.
                </p>
              </div>
            </div>
          </div>

          <div className="glass-card p-5">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <Shield className="w-4 h-4 text-red-400" />
                Active Alerts
              </h3>
              <Link href="/traps" className="text-xs text-blue-400 hover:text-blue-300 flex items-center gap-1">
                View all <ChevronRight className="w-3 h-3" />
              </Link>
            </div>
            <div className="space-y-2">
              {trapExamples.slice(0, 3).map((trap, i) => (
                <div key={i} className="flex items-center gap-3 p-2 rounded-lg hover:bg-white/5 transition-colors">
                  <div className={`w-2 h-2 rounded-full ${
                    trap.severity === "CRITICAL" ? "bg-red-500 animate-pulse" :
                    trap.severity === "HIGH" ? "bg-orange-500" : "bg-yellow-500"
                  }`} />
                  <div className="flex-1 min-w-0">
                    <p className="text-xs font-medium text-slate-300 truncate">{trap.type.replace(/_/g, " ")}</p>
                    <p className="text-[10px] text-slate-600 truncate">{trap.description.slice(0, 60)}...</p>
                  </div>
                  <span className={`text-[10px] font-bold ${
                    trap.severity === "CRITICAL" ? "text-red-400" :
                    trap.severity === "HIGH" ? "text-orange-400" : "text-yellow-400"
                  }`}>{trap.severity}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Trending Stocks Table */}
      <div className="glass-card">
        <div className="flex items-center justify-between p-5 pb-0">
          <div className="flex items-center gap-3">
            <h2 className="text-lg font-bold text-white">Trending Stocks</h2>
            <span className="px-2 py-0.5 text-[10px] font-medium bg-blue-500/10 text-blue-400 rounded-full border border-blue-500/20">
              LIVE
            </span>
          </div>
          <div className="flex gap-2">
            {["All", "Tech", "Finance", "Energy"].map((cat) => (
              <button
                key={cat}
                className="px-3 py-1 text-xs font-medium text-slate-500 hover:text-slate-300 hover:bg-white/5 rounded-md transition-colors"
              >
                {cat}
              </button>
            ))}
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-[#1e2d3d]">
                <th className="text-left px-5 py-3 text-[10px] font-semibold text-slate-500 uppercase tracking-wider">Symbol</th>
                <th className="text-right px-5 py-3 text-[10px] font-semibold text-slate-500 uppercase tracking-wider">Price</th>
                <th className="text-right px-5 py-3 text-[10px] font-semibold text-slate-500 uppercase tracking-wider">Change</th>
                <th className="text-right px-5 py-3 text-[10px] font-semibold text-slate-500 uppercase tracking-wider">Volume</th>
                <th className="text-right px-5 py-3 text-[10px] font-semibold text-slate-500 uppercase tracking-wider">Mkt Cap</th>
                <th className="text-center px-5 py-3 text-[10px] font-semibold text-slate-500 uppercase tracking-wider">Signal</th>
                <th className="text-center px-5 py-3 text-[10px] font-semibold text-slate-500 uppercase tracking-wider">Score</th>
                <th className="text-right px-5 py-3 text-[10px] font-semibold text-slate-500 uppercase tracking-wider">Action</th>
              </tr>
            </thead>
            <tbody>
              {trendingStocks.map((stock) => {
                const score = Math.floor(40 + Math.random() * 55);
                const signal = score >= 80 ? "STRONG_BUY" : score >= 65 ? "BUY" : score >= 45 ? "HOLD" : "SELL";
                return (
                  <tr key={stock.symbol} className="border-b border-[#1e2d3d]/50 hover:bg-white/[0.02] transition-colors">
                    <td className="px-5 py-3.5">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-lg bg-blue-500/10 flex items-center justify-center">
                          {stock.change >= 0 ? (
                            <TrendingUp className="w-4 h-4 text-emerald-400" />
                          ) : (
                            <TrendingDown className="w-4 h-4 text-red-400" />
                          )}
                        </div>
                        <div>
                          <p className="text-sm font-bold text-white">{stock.symbol}</p>
                          <p className="text-[10px] text-slate-500">{stock.name}</p>
                        </div>
                      </div>
                    </td>
                    <td className="px-5 py-3.5 text-right">
                      <span className="text-sm font-semibold text-white font-mono">${stock.price.toFixed(2)}</span>
                    </td>
                    <td className="px-5 py-3.5 text-right">
                      <span className={`text-sm font-semibold ${stock.change >= 0 ? "text-emerald-400" : "text-red-400"}`}>
                        {stock.change >= 0 ? "+" : ""}{stock.changePercent.toFixed(2)}%
                      </span>
                    </td>
                    <td className="px-5 py-3.5 text-right">
                      <span className="text-sm text-slate-400 font-mono">{(stock.volume / 1e6).toFixed(1)}M</span>
                    </td>
                    <td className="px-5 py-3.5 text-right">
                      <span className="text-sm text-slate-400">{formatLargeNumber(stock.marketCap)}</span>
                    </td>
                    <td className="px-5 py-3.5 text-center">
                      <SignalBadge signal={signal} size="sm" />
                    </td>
                    <td className="px-5 py-3.5">
                      <div className="flex justify-center">
                        <ScoreMeter score={score} />
                      </div>
                    </td>
                    <td className="px-5 py-3.5 text-right">
                      <Link
                        href={`/analyze?symbol=${stock.symbol}`}
                        className="inline-flex items-center gap-1 px-3 py-1.5 text-xs font-medium text-blue-400 hover:text-blue-300 bg-blue-500/10 hover:bg-blue-500/20 rounded-lg border border-blue-500/20 transition-all"
                      >
                        <Eye className="w-3 h-3" />
                        Analyze
                      </Link>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
