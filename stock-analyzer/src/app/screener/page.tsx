"use client";

import { useState, useMemo } from "react";
import Link from "next/link";
import {
  ScanLine, Filter, TrendingUp, TrendingDown, Eye, SortAsc,
  SortDesc, RotateCcw, Sparkles,
} from "lucide-react";
import { screenerStocks } from "@/lib/mock-data";
import { SignalBadge, ScoreMeter } from "@/components/SignalBadge";

function formatLargeNumber(n: number): string {
  if (n >= 1e12) return `$${(n / 1e12).toFixed(2)}T`;
  if (n >= 1e9) return `$${(n / 1e9).toFixed(1)}B`;
  if (n >= 1e6) return `$${(n / 1e6).toFixed(1)}M`;
  return `$${n.toLocaleString()}`;
}

export default function ScreenerPage() {
  const [minScore, setMinScore] = useState(0);
  const [selectedSignal, setSelectedSignal] = useState("ALL");
  const [selectedSector, setSelectedSector] = useState("ALL");
  const [minPrice, setMinPrice] = useState(0);
  const [maxPrice, setMaxPrice] = useState(10000);
  const [sortBy, setSortBy] = useState<"aiScore" | "price" | "changePercent" | "volume" | "marketCap">("aiScore");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("desc");

  const sectors = ["ALL", ...new Set(screenerStocks.map((s) => s.sector))];
  const signals = ["ALL", "STRONG_BUY", "BUY", "HOLD", "SELL", "STRONG_SELL"];

  const filtered = useMemo(() => {
    return screenerStocks
      .filter((s) => {
        if (s.aiScore < minScore) return false;
        if (selectedSignal !== "ALL" && s.signal !== selectedSignal) return false;
        if (selectedSector !== "ALL" && s.sector !== selectedSector) return false;
        if (s.price < minPrice || s.price > maxPrice) return false;
        return true;
      })
      .sort((a, b) => {
        const mul = sortDir === "asc" ? 1 : -1;
        return mul * ((a[sortBy] as number) - (b[sortBy] as number));
      });
  }, [minScore, selectedSignal, selectedSector, minPrice, maxPrice, sortBy, sortDir]);

  function toggleSort(col: typeof sortBy) {
    if (sortBy === col) {
      setSortDir(sortDir === "asc" ? "desc" : "asc");
    } else {
      setSortBy(col);
      setSortDir("desc");
    }
  }

  function resetFilters() {
    setMinScore(0);
    setSelectedSignal("ALL");
    setSelectedSector("ALL");
    setMinPrice(0);
    setMaxPrice(10000);
    setSortBy("aiScore");
    setSortDir("desc");
  }

  const SortIcon = ({ col }: { col: typeof sortBy }) => {
    if (sortBy !== col) return null;
    return sortDir === "desc" ? <SortDesc className="w-3 h-3" /> : <SortAsc className="w-3 h-3" />;
  };

  return (
    <div className="space-y-6 fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-3">
            <ScanLine className="w-7 h-7 text-blue-400" />
            Stock Screener
          </h1>
          <p className="text-sm text-slate-500 mt-1">Find high-potential stocks with AI-powered scoring and filtering</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium bg-purple-500/10 text-purple-400 rounded-lg border border-purple-500/20">
            <Sparkles className="w-3.5 h-3.5" />
            AI Scored
          </span>
          <span className="text-xs text-slate-500">{filtered.length} results</span>
        </div>
      </div>

      {/* Filters */}
      <div className="glass-card p-5">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <Filter className="w-4 h-4 text-slate-400" />
            Filters
          </h3>
          <button onClick={resetFilters} className="flex items-center gap-1 text-xs text-slate-500 hover:text-slate-300 transition-colors">
            <RotateCcw className="w-3 h-3" />
            Reset
          </button>
        </div>
        <div className="grid grid-cols-5 gap-4">
          <div>
            <label className="text-[10px] text-slate-500 font-medium uppercase tracking-wider block mb-1.5">Min AI Score</label>
            <div className="flex items-center gap-3">
              <input
                type="range" min={0} max={100} value={minScore}
                onChange={(e) => setMinScore(+e.target.value)}
                className="flex-1"
              />
              <span className="text-sm font-semibold text-white w-8 text-right">{minScore}</span>
            </div>
          </div>
          <div>
            <label className="text-[10px] text-slate-500 font-medium uppercase tracking-wider block mb-1.5">Signal</label>
            <select
              value={selectedSignal}
              onChange={(e) => setSelectedSignal(e.target.value)}
              className="w-full bg-[#0d1321] border border-[#1e2d3d] rounded-lg px-3 py-2 text-sm text-slate-300 focus:outline-none focus:border-blue-500/50"
            >
              {signals.map((s) => (
                <option key={s} value={s}>{s === "ALL" ? "All Signals" : s.replace("_", " ")}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="text-[10px] text-slate-500 font-medium uppercase tracking-wider block mb-1.5">Sector</label>
            <select
              value={selectedSector}
              onChange={(e) => setSelectedSector(e.target.value)}
              className="w-full bg-[#0d1321] border border-[#1e2d3d] rounded-lg px-3 py-2 text-sm text-slate-300 focus:outline-none focus:border-blue-500/50"
            >
              {sectors.map((s) => (
                <option key={s} value={s}>{s === "ALL" ? "All Sectors" : s}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="text-[10px] text-slate-500 font-medium uppercase tracking-wider block mb-1.5">Min Price</label>
            <input
              type="number" value={minPrice}
              onChange={(e) => setMinPrice(+e.target.value)}
              className="w-full bg-[#0d1321] border border-[#1e2d3d] rounded-lg px-3 py-2 text-sm text-slate-300 focus:outline-none focus:border-blue-500/50"
              placeholder="$0"
            />
          </div>
          <div>
            <label className="text-[10px] text-slate-500 font-medium uppercase tracking-wider block mb-1.5">Max Price</label>
            <input
              type="number" value={maxPrice}
              onChange={(e) => setMaxPrice(+e.target.value)}
              className="w-full bg-[#0d1321] border border-[#1e2d3d] rounded-lg px-3 py-2 text-sm text-slate-300 focus:outline-none focus:border-blue-500/50"
              placeholder="$10,000"
            />
          </div>
        </div>
      </div>

      {/* Results Table */}
      <div className="glass-card overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="border-b border-[#1e2d3d]">
              <th className="text-left px-5 py-3 text-[10px] font-semibold text-slate-500 uppercase tracking-wider">Rank</th>
              <th className="text-left px-5 py-3 text-[10px] font-semibold text-slate-500 uppercase tracking-wider">Stock</th>
              <th className="text-center px-5 py-3 text-[10px] font-semibold text-slate-500 uppercase tracking-wider">
                <button onClick={() => toggleSort("aiScore")} className="flex items-center gap-1 mx-auto hover:text-slate-300">
                  AI Score <SortIcon col="aiScore" />
                </button>
              </th>
              <th className="text-center px-5 py-3 text-[10px] font-semibold text-slate-500 uppercase tracking-wider">Signal</th>
              <th className="text-right px-5 py-3 text-[10px] font-semibold text-slate-500 uppercase tracking-wider">
                <button onClick={() => toggleSort("price")} className="flex items-center gap-1 ml-auto hover:text-slate-300">
                  Price <SortIcon col="price" />
                </button>
              </th>
              <th className="text-right px-5 py-3 text-[10px] font-semibold text-slate-500 uppercase tracking-wider">
                <button onClick={() => toggleSort("changePercent")} className="flex items-center gap-1 ml-auto hover:text-slate-300">
                  Change <SortIcon col="changePercent" />
                </button>
              </th>
              <th className="text-right px-5 py-3 text-[10px] font-semibold text-slate-500 uppercase tracking-wider">
                <button onClick={() => toggleSort("volume")} className="flex items-center gap-1 ml-auto hover:text-slate-300">
                  Volume <SortIcon col="volume" />
                </button>
              </th>
              <th className="text-right px-5 py-3 text-[10px] font-semibold text-slate-500 uppercase tracking-wider">
                <button onClick={() => toggleSort("marketCap")} className="flex items-center gap-1 ml-auto hover:text-slate-300">
                  Mkt Cap <SortIcon col="marketCap" />
                </button>
              </th>
              <th className="text-left px-5 py-3 text-[10px] font-semibold text-slate-500 uppercase tracking-wider">Sector</th>
              <th className="text-right px-5 py-3 text-[10px] font-semibold text-slate-500 uppercase tracking-wider">Action</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((stock, i) => (
              <tr key={stock.symbol} className="border-b border-[#1e2d3d]/50 hover:bg-white/[0.02] transition-colors">
                <td className="px-5 py-3.5">
                  <span className={`w-6 h-6 flex items-center justify-center rounded-full text-[10px] font-bold ${
                    i === 0 ? "bg-yellow-500/20 text-yellow-400" :
                    i === 1 ? "bg-slate-500/20 text-slate-300" :
                    i === 2 ? "bg-orange-500/20 text-orange-400" :
                    "bg-white/5 text-slate-500"
                  }`}>
                    {i + 1}
                  </span>
                </td>
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
                <td className="px-5 py-3.5">
                  <div className="flex justify-center">
                    <ScoreMeter score={stock.aiScore} />
                  </div>
                </td>
                <td className="px-5 py-3.5 text-center">
                  <SignalBadge signal={stock.signal} size="sm" />
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
                <td className="px-5 py-3.5">
                  <span className="text-xs text-slate-500">{stock.sector}</span>
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
            ))}
            {filtered.length === 0 && (
              <tr>
                <td colSpan={10} className="px-5 py-12 text-center text-sm text-slate-500">
                  No stocks match your filters. Try adjusting the criteria.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
