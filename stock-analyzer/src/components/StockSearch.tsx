"use client";

import { useState, useRef, useEffect } from "react";
import { Search, TrendingUp, Clock } from "lucide-react";
import { useRouter } from "next/navigation";
import { trendingStocks } from "@/lib/mock-data";

export default function StockSearch() {
  const [query, setQuery] = useState("");
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  const router = useRouter();

  const filtered = query.length > 0
    ? trendingStocks.filter(
        (s) =>
          s.symbol.toLowerCase().includes(query.toLowerCase()) ||
          s.name.toLowerCase().includes(query.toLowerCase())
      )
    : [];

  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, []);

  function handleSelect(symbol: string) {
    setQuery("");
    setOpen(false);
    router.push(`/analyze?symbol=${symbol}`);
  }

  return (
    <div ref={ref} className="relative w-full max-w-md">
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
        <input
          type="text"
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            setOpen(true);
          }}
          onFocus={() => setOpen(true)}
          placeholder="Search stocks... (e.g. NVDA, Apple)"
          className="w-full pl-10 pr-4 py-2.5 bg-[#0d1321] border border-[#1e2d3d] rounded-lg text-sm text-slate-200 placeholder:text-slate-600 focus:outline-none focus:border-blue-500/50 transition-colors"
        />
      </div>

      {open && (
        <div className="absolute top-full mt-2 w-full bg-[#111827] border border-[#1e2d3d] rounded-xl shadow-2xl shadow-black/50 overflow-hidden z-50">
          {filtered.length > 0 ? (
            <div className="py-2">
              {filtered.map((stock) => (
                <button
                  key={stock.symbol}
                  onClick={() => handleSelect(stock.symbol)}
                  className="w-full flex items-center gap-3 px-4 py-2.5 hover:bg-white/5 transition-colors text-left"
                >
                  <div className="w-8 h-8 rounded-lg bg-blue-500/10 flex items-center justify-center">
                    <TrendingUp className="w-4 h-4 text-blue-400" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-semibold text-white">{stock.symbol}</span>
                      <span className="text-xs text-slate-500">{stock.exchange}</span>
                    </div>
                    <p className="text-xs text-slate-500 truncate">{stock.name}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-medium text-white">${stock.price.toFixed(2)}</p>
                    <p className={`text-xs font-medium ${stock.change >= 0 ? "text-emerald-400" : "text-red-400"}`}>
                      {stock.change >= 0 ? "+" : ""}{stock.changePercent.toFixed(2)}%
                    </p>
                  </div>
                </button>
              ))}
            </div>
          ) : query.length > 0 ? (
            <div className="px-4 py-8 text-center">
              <p className="text-sm text-slate-500">No results for &quot;{query}&quot;</p>
              <p className="text-xs text-slate-600 mt-1">Try a different symbol or company name</p>
            </div>
          ) : (
            <div className="py-2">
              <p className="px-4 py-1.5 text-xs font-medium text-slate-600 uppercase tracking-wider">
                <Clock className="w-3 h-3 inline mr-1.5" />
                Popular
              </p>
              {trendingStocks.slice(0, 5).map((stock) => (
                <button
                  key={stock.symbol}
                  onClick={() => handleSelect(stock.symbol)}
                  className="w-full flex items-center gap-3 px-4 py-2 hover:bg-white/5 transition-colors text-left"
                >
                  <span className="text-sm font-semibold text-white w-14">{stock.symbol}</span>
                  <span className="text-xs text-slate-500 flex-1 truncate">{stock.name}</span>
                  <span className={`text-xs font-medium ${stock.change >= 0 ? "text-emerald-400" : "text-red-400"}`}>
                    {stock.change >= 0 ? "+" : ""}{stock.changePercent.toFixed(2)}%
                  </span>
                </button>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
