"use client";

import { useState, useEffect, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import {
  TrendingUp, TrendingDown, Activity, Brain, Shield, Target,
  AlertTriangle, ChevronRight, BarChart3, Gauge, ArrowUpRight,
  ArrowDownRight, Clock, Volume2, DollarSign, PieChart, Zap,
} from "lucide-react";
import {
  AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer,
  BarChart, Bar, RadarChart, PolarGrid, PolarAngleAxis,
  PolarRadiusAxis, Radar, LineChart, Line,
} from "recharts";
import {
  trendingStocks, generateChartData, getMockAISignal,
  getMockTechnicals, getMockSentiment, getMockNews,
} from "@/lib/mock-data";
import { SignalBadge, SeverityBadge, ScoreMeter } from "@/components/SignalBadge";

function AnalyzeContent() {
  const searchParams = useSearchParams();
  const symbolParam = searchParams.get("symbol") || "NVDA";
  const [symbol, setSymbol] = useState(symbolParam);
  const [chartData] = useState(() => generateChartData(90));
  const [timeframe, setTimeframe] = useState("3M");

  useEffect(() => {
    const s = searchParams.get("symbol");
    if (s) setSymbol(s);
  }, [searchParams]);

  const stock = trendingStocks.find((s) => s.symbol === symbol) || trendingStocks[0];
  const aiSignal = getMockAISignal(symbol);
  const technicals = getMockTechnicals();
  const sentiment = getMockSentiment();
  const news = getMockNews(symbol);

  const sentimentRadar = [
    { subject: "Social", value: sentiment.social },
    { subject: "News", value: sentiment.news },
    { subject: "Analyst", value: sentiment.analyst },
    { subject: "Insider", value: sentiment.insider },
    { subject: "Institutional", value: sentiment.institutional },
  ];

  const techGauges = [
    { label: "RSI", value: technicals.rsi, max: 100, warn: technicals.rsi > 70 || technicals.rsi < 30 },
    { label: "Stoch %K", value: technicals.stochastic.k, max: 100, warn: technicals.stochastic.k > 80 || technicals.stochastic.k < 20 },
    { label: "MACD", value: technicals.macd.histogram, max: 5, warn: false },
  ];

  return (
    <div className="space-y-6 fade-in">
      {/* Stock Header */}
      <div className="glass-card p-6">
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-3 mb-1">
              <h1 className="text-3xl font-bold text-white">{stock.symbol}</h1>
              <SignalBadge signal={aiSignal.signal} size="lg" />
              {aiSignal.botRisk !== "LOW" && (
                <span className="flex items-center gap-1 px-2 py-0.5 text-xs font-bold text-red-400 bg-red-500/10 rounded-md border border-red-500/20">
                  <Shield className="w-3 h-3" />
                  Bot Risk: {aiSignal.botRisk}
                </span>
              )}
            </div>
            <p className="text-slate-400 text-sm">{stock.name} · {stock.exchange} · {stock.sector}</p>
          </div>
          <div className="text-right">
            <p className="text-3xl font-bold text-white font-mono">${stock.price.toFixed(2)}</p>
            <div className="flex items-center justify-end gap-2 mt-1">
              {stock.change >= 0 ? (
                <ArrowUpRight className="w-4 h-4 text-emerald-400" />
              ) : (
                <ArrowDownRight className="w-4 h-4 text-red-400" />
              )}
              <span className={`text-lg font-bold ${stock.change >= 0 ? "text-emerald-400" : "text-red-400"}`}>
                {stock.change >= 0 ? "+" : ""}{stock.change.toFixed(2)} ({stock.changePercent >= 0 ? "+" : ""}{stock.changePercent.toFixed(2)}%)
              </span>
            </div>
          </div>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-8 gap-4 mt-6 pt-5 border-t border-[#1e2d3d]">
          {[
            { label: "Open", value: `$${stock.open.toFixed(2)}` },
            { label: "High", value: `$${stock.high.toFixed(2)}` },
            { label: "Low", value: `$${stock.low.toFixed(2)}` },
            { label: "Volume", value: `${(stock.volume / 1e6).toFixed(1)}M` },
            { label: "Avg Volume", value: `${(stock.avgVolume / 1e6).toFixed(1)}M` },
            { label: "P/E Ratio", value: stock.pe ? stock.pe.toFixed(1) : "N/A" },
            { label: "52W High", value: `$${stock.fiftyTwoWeekHigh.toFixed(2)}` },
            { label: "52W Low", value: `$${stock.fiftyTwoWeekLow.toFixed(2)}` },
          ].map((stat) => (
            <div key={stat.label}>
              <p className="text-[10px] text-slate-500 font-medium uppercase">{stat.label}</p>
              <p className="text-sm font-semibold text-white mt-0.5 font-mono">{stat.value}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-12 gap-6">
        {/* Price Chart */}
        <div className="col-span-8 glass-card p-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm font-bold text-white flex items-center gap-2">
              <BarChart3 className="w-4 h-4 text-blue-400" />
              Price Chart
            </h2>
            <div className="flex gap-1">
              {["1D", "1W", "1M", "3M", "6M", "1Y"].map((tf) => (
                <button
                  key={tf}
                  onClick={() => setTimeframe(tf)}
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
          <div className="h-[350px]">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartData}>
                <defs>
                  <linearGradient id="priceGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#3b82f6" stopOpacity={0.2} />
                    <stop offset="100%" stopColor="#3b82f6" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <XAxis
                  dataKey="date" axisLine={false} tickLine={false}
                  tick={{ fill: "#64748b", fontSize: 10 }}
                  tickFormatter={(v) => new Date(v).toLocaleDateString("en-US", { month: "short", day: "numeric" })}
                  interval={Math.floor(chartData.length / 6)}
                />
                <YAxis
                  axisLine={false} tickLine={false} width={65}
                  tick={{ fill: "#64748b", fontSize: 10 }}
                  tickFormatter={(v) => `$${v.toFixed(0)}`}
                  domain={["auto", "auto"]}
                />
                <Tooltip
                  contentStyle={{ background: "#1a2332", border: "1px solid #1e2d3d", borderRadius: "8px", fontSize: "12px", color: "#e2e8f0" }}
                  formatter={(value: unknown) => [`$${Number(value).toFixed(2)}`, "Price"]}
                />
                <Area type="monotone" dataKey="close" stroke="#3b82f6" fill="url(#priceGrad)" strokeWidth={2} />
                <Line type="monotone" dataKey="high" stroke="#10b981" strokeWidth={1} strokeDasharray="4 4" dot={false} />
                <Line type="monotone" dataKey="low" stroke="#ef4444" strokeWidth={1} strokeDasharray="4 4" dot={false} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
          <div className="h-[60px] mt-2">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData}>
                <XAxis dataKey="date" hide />
                <YAxis hide />
                <Bar dataKey="volume" fill="#1e2d3d" radius={[2, 2, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* AI Analysis Panel */}
        <div className="col-span-4 space-y-4">
          <div className="glass-card p-5">
            <div className="flex items-center gap-2 mb-4">
              <Brain className="w-5 h-5 text-purple-400" />
              <h3 className="text-sm font-bold text-white">AI Analysis</h3>
              <span className="ml-auto text-xs font-medium text-slate-500">
                {(aiSignal.confidence * 100).toFixed(0)}% confidence
              </span>
            </div>

            <div className="flex items-center justify-center gap-6 mb-4 py-3">
              <ScoreMeter score={Math.round(aiSignal.confidence * 100)} label="AI Score" />
              <div className="text-center">
                <SignalBadge signal={aiSignal.signal} size="lg" />
                <p className="text-[10px] text-slate-500 mt-2">
                  Target: <span className="text-white font-semibold">${aiSignal.priceTarget.toFixed(2)}</span>
                </p>
                <p className="text-[10px] text-slate-500">{aiSignal.timeframe}</p>
              </div>
            </div>

            <p className="text-xs text-slate-400 leading-relaxed mb-4">{aiSignal.reasoning}</p>

            <div className="space-y-3">
              <div>
                <p className="text-[10px] text-emerald-400 font-semibold uppercase tracking-wider mb-1.5 flex items-center gap-1">
                  <Zap className="w-3 h-3" /> Catalysts
                </p>
                <ul className="space-y-1">
                  {aiSignal.catalysts.map((c, i) => (
                    <li key={i} className="text-xs text-slate-400 flex items-start gap-2">
                      <ChevronRight className="w-3 h-3 text-emerald-500 mt-0.5 shrink-0" />
                      {c}
                    </li>
                  ))}
                </ul>
              </div>
              <div>
                <p className="text-[10px] text-red-400 font-semibold uppercase tracking-wider mb-1.5 flex items-center gap-1">
                  <AlertTriangle className="w-3 h-3" /> Risks
                </p>
                <ul className="space-y-1">
                  {aiSignal.risks.map((r, i) => (
                    <li key={i} className="text-xs text-slate-400 flex items-start gap-2">
                      <ChevronRight className="w-3 h-3 text-red-500 mt-0.5 shrink-0" />
                      {r}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Technical Indicators + Sentiment */}
      <div className="grid grid-cols-12 gap-6">
        <div className="col-span-5 glass-card p-5">
          <h3 className="text-sm font-bold text-white flex items-center gap-2 mb-4">
            <Gauge className="w-4 h-4 text-yellow-400" />
            Technical Indicators
          </h3>
          <div className="grid grid-cols-3 gap-4 mb-4">
            {techGauges.map((g) => (
              <div key={g.label} className="text-center">
                <ScoreMeter score={Math.round(Math.abs(g.value))} label={g.label} />
                {g.warn && <p className="text-[9px] text-yellow-400 mt-1">⚠ Overbought/Oversold</p>}
              </div>
            ))}
          </div>
          <div className="space-y-2 pt-3 border-t border-[#1e2d3d]">
            {[
              { label: "SMA 20", value: technicals.sma20, vs: stock.price },
              { label: "SMA 50", value: technicals.sma50, vs: stock.price },
              { label: "SMA 200", value: technicals.sma200, vs: stock.price },
              { label: "VWAP", value: technicals.vwap, vs: stock.price },
              { label: "ATR", value: technicals.atr, vs: null },
              { label: "Bollinger Upper", value: technicals.bollingerBands.upper, vs: null },
              { label: "Bollinger Lower", value: technicals.bollingerBands.lower, vs: null },
            ].map((ind) => (
              <div key={ind.label} className="flex items-center justify-between text-xs">
                <span className="text-slate-500">{ind.label}</span>
                <div className="flex items-center gap-2">
                  <span className="text-white font-mono">${ind.value.toFixed(2)}</span>
                  {ind.vs && (
                    <span className={`text-[10px] font-semibold ${ind.vs > ind.value ? "text-emerald-400" : "text-red-400"}`}>
                      {ind.vs > ind.value ? "ABOVE" : "BELOW"}
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="col-span-3 glass-card p-5">
          <h3 className="text-sm font-bold text-white flex items-center gap-2 mb-4">
            <PieChart className="w-4 h-4 text-blue-400" />
            Sentiment Radar
          </h3>
          <div className="h-[220px]">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart data={sentimentRadar}>
                <PolarGrid stroke="#1e2d3d" />
                <PolarAngleAxis dataKey="subject" tick={{ fill: "#64748b", fontSize: 10 }} />
                <PolarRadiusAxis tick={false} axisLine={false} domain={[0, 100]} />
                <Radar
                  dataKey="value"
                  stroke="#3b82f6"
                  fill="#3b82f6"
                  fillOpacity={0.15}
                  strokeWidth={2}
                />
              </RadarChart>
            </ResponsiveContainer>
          </div>
          <div className="text-center mt-2">
            <p className="text-xs text-slate-500">Overall Sentiment</p>
            <p className="text-2xl font-bold text-white">{sentiment.overall}<span className="text-sm text-slate-500">/100</span></p>
          </div>
        </div>

        <div className="col-span-4 glass-card p-5">
          <h3 className="text-sm font-bold text-white flex items-center gap-2 mb-4">
            <Activity className="w-4 h-4 text-cyan-400" />
            Latest News
          </h3>
          <div className="space-y-3">
            {news.map((item, i) => (
              <div key={i} className="p-3 rounded-lg hover:bg-white/5 transition-colors border border-transparent hover:border-[#1e2d3d]">
                <div className="flex items-center gap-2 mb-1">
                  <span className={`text-[10px] font-bold ${
                    item.sentiment === "BULLISH" ? "text-emerald-400" :
                    item.sentiment === "BEARISH" ? "text-red-400" : "text-slate-400"
                  }`}>
                    {item.sentiment}
                  </span>
                  <span className="text-[10px] text-slate-600">·</span>
                  <span className="text-[10px] text-slate-600">{item.source}</span>
                  <span className="text-[10px] text-slate-600 ml-auto flex items-center gap-1">
                    <Clock className="w-2.5 h-2.5" />
                    {new Date(item.publishedAt).toLocaleTimeString("en-US", { hour: "numeric", minute: "2-digit" })}
                  </span>
                </div>
                <p className="text-xs font-medium text-slate-300 leading-relaxed">{item.title}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Trap Indicators */}
      {aiSignal.trapIndicators.length > 0 && (
        <div className="glass-card p-5 border-red-500/20">
          <div className="flex items-center gap-2 mb-4">
            <Shield className="w-5 h-5 text-red-400" />
            <h3 className="text-sm font-bold text-red-400">⚠ Active Trap Warnings</h3>
          </div>
          <div className="grid grid-cols-2 gap-4">
            {aiSignal.trapIndicators.map((trap, i) => (
              <div key={i} className="p-4 rounded-lg bg-red-500/5 border border-red-500/10">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-bold text-white">{trap.type.replace(/_/g, " ")}</span>
                  <SeverityBadge severity={trap.severity} />
                </div>
                <p className="text-xs text-slate-400 leading-relaxed mb-3">{trap.description}</p>
                <div>
                  <p className="text-[10px] text-slate-500 font-semibold uppercase mb-1">Evidence</p>
                  <ul className="space-y-0.5">
                    {trap.evidence.map((e, j) => (
                      <li key={j} className="text-[11px] text-slate-500 flex items-start gap-1.5">
                        <span className="text-red-400 mt-0.5">•</span>
                        {e}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default function AnalyzePage() {
  return (
    <Suspense fallback={<div className="text-slate-500 text-center py-20">Loading analysis...</div>}>
      <AnalyzeContent />
    </Suspense>
  );
}
