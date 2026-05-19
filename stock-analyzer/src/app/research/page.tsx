"use client";

import { useState } from "react";
import {
  BookOpen, Brain, Send, Sparkles, TrendingUp, Shield, Target,
  BarChart3, FileText, Lightbulb, AlertTriangle, Clock, Zap,
  Key, CheckCircle, XCircle, Settings,
} from "lucide-react";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell,
} from "recharts";
import { getMockNews, getMockSentiment } from "@/lib/mock-data";

const PRESET_PROMPTS = [
  { icon: TrendingUp, label: "Should I buy NVDA?", prompt: "Analyze NVIDIA (NVDA) stock and tell me if I should buy it right now. Include technical analysis, fundamentals, and any red flags." },
  { icon: Shield, label: "Is TSLA being manipulated?", prompt: "Analyze Tesla (TSLA) for any signs of market manipulation, bot activity, or trading traps. Look at volume patterns, social media activity, and price action." },
  { icon: Target, label: "Best AI stocks to buy", prompt: "What are the top 5 AI-related stocks to buy right now? Consider valuation, growth potential, competitive moats, and current market conditions." },
  { icon: BarChart3, label: "Compare MSFT vs GOOGL", prompt: "Compare Microsoft (MSFT) and Alphabet (GOOGL) as investment opportunities. Which is the better buy and why?" },
  { icon: FileText, label: "Market outlook 2025", prompt: "Give me a comprehensive market outlook. What sectors look promising, what are the major risks, and how should I position my portfolio?" },
  { icon: Lightbulb, label: "Find undervalued stocks", prompt: "Find stocks that appear to be significantly undervalued right now. Look for strong fundamentals trading below intrinsic value with upcoming catalysts." },
];

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

export default function ResearchPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [apiKey, setApiKey] = useState("");
  const [showSettings, setShowSettings] = useState(false);
  const [apiConfigured, setApiConfigured] = useState(false);

  const sentiment = getMockSentiment();
  const news = getMockNews("MARKET");

  const sentimentBars = [
    { name: "Social", value: sentiment.social, fill: "#3b82f6" },
    { name: "News", value: sentiment.news, fill: "#8b5cf6" },
    { name: "Analyst", value: sentiment.analyst, fill: "#10b981" },
    { name: "Insider", value: sentiment.insider, fill: "#f59e0b" },
    { name: "Institutional", value: sentiment.institutional, fill: "#06b6d4" },
  ];

  const sectorAllocation = [
    { name: "Tech", value: 35, fill: "#3b82f6" },
    { name: "Finance", value: 20, fill: "#10b981" },
    { name: "Healthcare", value: 15, fill: "#8b5cf6" },
    { name: "Energy", value: 12, fill: "#f59e0b" },
    { name: "Consumer", value: 10, fill: "#ef4444" },
    { name: "Other", value: 8, fill: "#64748b" },
  ];

  async function handleSend(text?: string) {
    const messageText = text || input;
    if (!messageText.trim()) return;

    const userMessage: ChatMessage = {
      role: "user",
      content: messageText,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    await new Promise((r) => setTimeout(r, 1500));

    const aiResponse: ChatMessage = {
      role: "assistant",
      content: generateMockResponse(messageText),
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, aiResponse]);
    setIsLoading(false);
  }

  function generateMockResponse(query: string): string {
    const q = query.toLowerCase();

    if (q.includes("nvda") || q.includes("nvidia")) {
      return `## NVIDIA (NVDA) Analysis

**Signal: STRONG BUY** | Confidence: 89%

### Key Findings:
- **Data center revenue** grew 400%+ YoY, driven by unprecedented AI/ML demand
- **Blackwell architecture** launching soon, expected to be 2-3x more efficient
- Price is trading above all major moving averages (SMA 20, 50, 200)
- RSI at 58.4 — healthy momentum, not overbought

### Price Target: $1,050 (6-12 months)

### Catalysts:
1. Enterprise AI adoption accelerating across industries
2. Sovereign AI infrastructure builds globally
3. Automotive/robotics revenue emerging as new growth driver

### Risks:
- Valuation multiples remain elevated (P/E ~64x)
- China export restrictions could impact ~15% of revenue
- Customer concentration in hyperscalers (MSFT, GOOG, AMZN, META)

### Bot/Trap Risk: LOW ✅
No significant manipulation signals detected. Volume and price action appear organic.

*Connect your AI API key for real-time, personalized analysis with live market data.*`;
    }

    if (q.includes("tsla") || q.includes("tesla") || q.includes("manipulat")) {
      return `## Tesla (TSLA) Manipulation Analysis

**⚠️ Bot Risk: HIGH** | Multiple trap indicators detected

### Active Warnings:

🔴 **FOMO TRAP** (Severity: HIGH)
- Volume 37% above average with no fundamental catalyst
- Social media mentions spiked 450% in 48 hours
- Options skew extremely bullish — retail-driven

🟡 **SHORT SQUEEZE TRAP** (Severity: MEDIUM)
- Short interest at 3.2% — moderate but declining
- Days to cover: 1.8
- Squeeze mechanics appear largely priced in

### Evidence:
- Retail order flow accounts for 90%+ of recent volume
- Price action disconnected from fundamentals (margins declining, competition increasing)
- Coordinated social media promotion detected across Reddit, Twitter/X, TikTok

### Recommendation:
Exercise extreme caution. If entering a position, use strict stop-losses and reduce position size. Wait for the social media-driven volatility to subside.

*Connect your AI API key for real-time trap detection with live order flow analysis.*`;
    }

    return `## AI Research Assistant

Thank you for your question about: "${query}"

To provide the most accurate, real-time analysis, please configure your AI API key in the settings panel. This enables:

- **Live market data analysis** with real-time prices and volume
- **Advanced pattern recognition** for trap and bot detection
- **Personalized recommendations** based on your risk profile
- **Deep fundamental analysis** with SEC filings and earnings data

### Quick Setup:
1. Get an API key from your preferred AI provider (OpenAI, Anthropic, etc.)
2. Enter it in the Settings panel on this page
3. Set the \`AI_API_KEY\` environment variable for persistent configuration

### What I Can Analyze:
- Individual stock analysis (buy/sell/hold signals)
- Market manipulation detection
- Sector rotation and macro trends
- Portfolio optimization suggestions
- Risk assessment and position sizing

*Try one of the preset prompts to see example analysis, or connect your API for live results.*`;
  }

  function handleSaveApiKey() {
    if (apiKey.trim().length > 10) {
      setApiConfigured(true);
      setShowSettings(false);
    }
  }

  return (
    <div className="space-y-6 fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-3">
            <BookOpen className="w-7 h-7 text-blue-400" />
            AI Research Assistant
          </h1>
          <p className="text-sm text-slate-500 mt-1">Ask anything about stocks, markets, and trading strategies</p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowSettings(!showSettings)}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-slate-400 hover:text-slate-200 bg-white/5 rounded-lg border border-[#1e2d3d] hover:border-[#2e3d4d] transition-all"
          >
            <Settings className="w-3.5 h-3.5" />
            API Settings
          </button>
          <span className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg border ${
            apiConfigured
              ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
              : "bg-yellow-500/10 text-yellow-400 border-yellow-500/20"
          }`}>
            {apiConfigured ? <CheckCircle className="w-3.5 h-3.5" /> : <Key className="w-3.5 h-3.5" />}
            {apiConfigured ? "AI Connected" : "API Key Required"}
          </span>
        </div>
      </div>

      {/* Settings Panel */}
      {showSettings && (
        <div className="glass-card p-5 border-blue-500/20">
          <div className="flex items-center gap-2 mb-4">
            <Key className="w-5 h-5 text-blue-400" />
            <h3 className="text-sm font-bold text-white">AI API Configuration</h3>
          </div>
          <p className="text-xs text-slate-500 mb-4">
            Enter your AI API key to enable live analysis. Supports OpenAI, Anthropic, and compatible APIs.
            For persistent configuration, set the <code className="text-blue-400">AI_API_KEY</code> environment variable.
          </p>
          <div className="flex gap-3">
            <input
              type="password" value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder="sk-..."
              className="flex-1 bg-[#0d1321] border border-[#1e2d3d] rounded-lg px-4 py-2.5 text-sm text-slate-300 placeholder:text-slate-600 focus:outline-none focus:border-blue-500/50 font-mono"
            />
            <button
              onClick={handleSaveApiKey}
              className="px-4 py-2.5 text-sm font-medium text-white bg-blue-600 hover:bg-blue-500 rounded-lg transition-colors"
            >
              Save & Connect
            </button>
          </div>
          {apiConfigured && (
            <div className="mt-3 flex items-center gap-2 text-xs text-emerald-400">
              <CheckCircle className="w-3.5 h-3.5" />
              API key saved. AI analysis is now active.
            </div>
          )}
        </div>
      )}

      <div className="grid grid-cols-12 gap-6">
        {/* Chat Interface */}
        <div className="col-span-8 glass-card flex flex-col" style={{ minHeight: "600px" }}>
          {/* Preset Prompts */}
          {messages.length === 0 && (
            <div className="flex-1 flex flex-col items-center justify-center p-8">
              <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center mb-4 shadow-lg shadow-blue-500/20">
                <Brain className="w-8 h-8 text-white" />
              </div>
              <h2 className="text-lg font-bold text-white mb-1">AI Stock Research</h2>
              <p className="text-sm text-slate-500 mb-6 text-center max-w-md">
                Ask me anything about stocks, market trends, or trading strategies. I can analyze individual stocks, detect manipulation, and provide research insights.
              </p>
              <div className="grid grid-cols-2 gap-3 w-full max-w-lg">
                {PRESET_PROMPTS.map((p, i) => (
                  <button
                    key={i}
                    onClick={() => handleSend(p.prompt)}
                    className="flex items-center gap-3 p-3 rounded-lg bg-white/5 hover:bg-white/10 border border-[#1e2d3d] hover:border-blue-500/30 transition-all text-left"
                  >
                    <p.icon className="w-4 h-4 text-blue-400 shrink-0" />
                    <span className="text-xs font-medium text-slate-300">{p.label}</span>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Messages */}
          {messages.length > 0 && (
            <div className="flex-1 overflow-y-auto p-5 space-y-4">
              {messages.map((msg, i) => (
                <div key={i} className={`flex gap-3 ${msg.role === "user" ? "justify-end" : ""}`}>
                  {msg.role === "assistant" && (
                    <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center shrink-0">
                      <Brain className="w-4 h-4 text-white" />
                    </div>
                  )}
                  <div className={`max-w-[80%] rounded-xl px-4 py-3 ${
                    msg.role === "user"
                      ? "bg-blue-600/20 border border-blue-500/20"
                      : "bg-white/5 border border-[#1e2d3d]"
                  }`}>
                    <div className="text-xs text-slate-300 leading-relaxed whitespace-pre-wrap">
                      {msg.content.split("\n").map((line, j) => {
                        if (line.startsWith("## ")) return <h2 key={j} className="text-base font-bold text-white mt-2 mb-1">{line.slice(3)}</h2>;
                        if (line.startsWith("### ")) return <h3 key={j} className="text-sm font-semibold text-white mt-2 mb-1">{line.slice(4)}</h3>;
                        if (line.startsWith("**") && line.endsWith("**")) return <p key={j} className="font-bold text-white">{line.slice(2, -2)}</p>;
                        if (line.startsWith("- ")) return <p key={j} className="ml-3">{line}</p>;
                        if (line.match(/^\d+\./)) return <p key={j} className="ml-3">{line}</p>;
                        if (line.startsWith("🔴") || line.startsWith("🟡") || line.startsWith("🟢")) return <p key={j} className="font-medium">{line}</p>;
                        return <p key={j}>{line || "\u00A0"}</p>;
                      })}
                    </div>
                    <p className="text-[10px] text-slate-600 mt-2">
                      {msg.timestamp.toLocaleTimeString("en-US", { hour: "numeric", minute: "2-digit" })}
                    </p>
                  </div>
                  {msg.role === "user" && (
                    <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-slate-600 to-slate-700 flex items-center justify-center shrink-0">
                      <span className="text-xs font-bold text-white">U</span>
                    </div>
                  )}
                </div>
              ))}
              {isLoading && (
                <div className="flex gap-3">
                  <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center shrink-0">
                    <Brain className="w-4 h-4 text-white" />
                  </div>
                  <div className="bg-white/5 border border-[#1e2d3d] rounded-xl px-4 py-3">
                    <div className="flex items-center gap-2">
                      <div className="flex gap-1">
                        <span className="w-2 h-2 rounded-full bg-blue-400 animate-bounce" style={{ animationDelay: "0ms" }} />
                        <span className="w-2 h-2 rounded-full bg-blue-400 animate-bounce" style={{ animationDelay: "150ms" }} />
                        <span className="w-2 h-2 rounded-full bg-blue-400 animate-bounce" style={{ animationDelay: "300ms" }} />
                      </div>
                      <span className="text-xs text-slate-500">Analyzing...</span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Input */}
          <div className="p-4 border-t border-[#1e2d3d]">
            <div className="flex gap-3">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && handleSend()}
                placeholder="Ask about any stock, market trend, or strategy..."
                className="flex-1 bg-[#0d1321] border border-[#1e2d3d] rounded-lg px-4 py-3 text-sm text-slate-300 placeholder:text-slate-600 focus:outline-none focus:border-blue-500/50"
              />
              <button
                onClick={() => handleSend()}
                disabled={!input.trim() || isLoading}
                className="px-4 py-3 bg-blue-600 hover:bg-blue-500 disabled:bg-slate-700 disabled:text-slate-500 rounded-lg transition-colors flex items-center gap-2"
              >
                <Send className="w-4 h-4" />
              </button>
            </div>
            <p className="text-[10px] text-slate-600 mt-2 text-center">
              {apiConfigured
                ? "AI analysis powered by your configured API. Responses use live market data."
                : "Using demo mode with sample data. Connect your AI API key for live analysis."}
            </p>
          </div>
        </div>

        {/* Side Panels */}
        <div className="col-span-4 space-y-4">
          {/* Market Sentiment */}
          <div className="glass-card p-5">
            <h3 className="text-sm font-bold text-white flex items-center gap-2 mb-4">
              <BarChart3 className="w-4 h-4 text-blue-400" />
              Market Sentiment
            </h3>
            <div className="h-[180px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={sentimentBars} layout="vertical">
                  <XAxis type="number" domain={[0, 100]} hide />
                  <YAxis
                    type="category" dataKey="name" width={80}
                    axisLine={false} tickLine={false}
                    tick={{ fill: "#64748b", fontSize: 11 }}
                  />
                  <Tooltip
                    contentStyle={{ background: "#1a2332", border: "1px solid #1e2d3d", borderRadius: "8px", fontSize: "12px", color: "#e2e8f0" }}
                  />
                  <Bar dataKey="value" radius={[0, 4, 4, 0]} barSize={16}>
                    {sentimentBars.map((entry, i) => (
                      <Cell key={i} fill={entry.fill} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Sector Allocation */}
          <div className="glass-card p-5">
            <h3 className="text-sm font-bold text-white flex items-center gap-2 mb-4">
              <Target className="w-4 h-4 text-purple-400" />
              Market Sectors
            </h3>
            <div className="h-[180px]">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={sectorAllocation}
                    cx="50%" cy="50%"
                    innerRadius={50} outerRadius={75}
                    paddingAngle={3}
                    dataKey="value"
                    strokeWidth={0}
                  >
                    {sectorAllocation.map((entry, i) => (
                      <Cell key={i} fill={entry.fill} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{ background: "#1a2332", border: "1px solid #1e2d3d", borderRadius: "8px", fontSize: "12px", color: "#e2e8f0" }}
                    formatter={(value: unknown) => [`${Number(value)}%`, "Weight"]}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="grid grid-cols-3 gap-2 mt-3">
              {sectorAllocation.map((s) => (
                <div key={s.name} className="flex items-center gap-1.5">
                  <div className="w-2 h-2 rounded-full" style={{ background: s.fill }} />
                  <span className="text-[10px] text-slate-500">{s.name} {s.value}%</span>
                </div>
              ))}
            </div>
          </div>

          {/* Recent News */}
          <div className="glass-card p-5">
            <h3 className="text-sm font-bold text-white flex items-center gap-2 mb-4">
              <Zap className="w-4 h-4 text-yellow-400" />
              Market News
            </h3>
            <div className="space-y-3">
              {news.slice(0, 4).map((item, i) => (
                <div key={i} className="p-2 rounded-lg hover:bg-white/5 transition-colors">
                  <div className="flex items-center gap-2 mb-0.5">
                    <span className={`w-1.5 h-1.5 rounded-full ${
                      item.sentiment === "BULLISH" ? "bg-emerald-400" :
                      item.sentiment === "BEARISH" ? "bg-red-400" : "bg-slate-400"
                    }`} />
                    <span className="text-[10px] text-slate-600">{item.source}</span>
                    <span className="text-[10px] text-slate-600 ml-auto flex items-center gap-0.5">
                      <Clock className="w-2.5 h-2.5" />
                      {new Date(item.publishedAt).toLocaleTimeString("en-US", { hour: "numeric", minute: "2-digit" })}
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-400 leading-relaxed">{item.title}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
