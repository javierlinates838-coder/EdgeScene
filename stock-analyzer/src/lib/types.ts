export interface StockQuote {
  symbol: string;
  name: string;
  price: number;
  change: number;
  changePercent: number;
  volume: number;
  avgVolume: number;
  marketCap: number;
  high: number;
  low: number;
  open: number;
  previousClose: number;
  fiftyTwoWeekHigh: number;
  fiftyTwoWeekLow: number;
  pe: number | null;
  eps: number | null;
  dividend: number | null;
  sector: string;
  exchange: string;
}

export interface AISignal {
  signal: "STRONG_BUY" | "BUY" | "HOLD" | "SELL" | "STRONG_SELL";
  confidence: number;
  reasoning: string;
  risks: string[];
  catalysts: string[];
  priceTarget: number;
  timeframe: string;
  botRisk: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  trapIndicators: TrapIndicator[];
}

export interface TrapIndicator {
  type: "PUMP_DUMP" | "WASH_TRADE" | "SPOOFING" | "LAYERING" | "FRONT_RUNNING" | "SHORT_SQUEEZE_TRAP" | "FOMO_TRAP" | "DEAD_CAT_BOUNCE";
  severity: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  description: string;
  evidence: string[];
  detectedAt: string;
}

export interface TechnicalIndicators {
  rsi: number;
  macd: { value: number; signal: number; histogram: number };
  sma20: number;
  sma50: number;
  sma200: number;
  ema12: number;
  ema26: number;
  bollingerBands: { upper: number; middle: number; lower: number };
  atr: number;
  obv: number;
  vwap: number;
  stochastic: { k: number; d: number };
}

export interface ScreenerFilter {
  minPrice: number;
  maxPrice: number;
  minVolume: number;
  minMarketCap: number;
  maxMarketCap: number;
  sector: string;
  signal: string;
  minScore: number;
}

export interface ChartDataPoint {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface MarketIndex {
  name: string;
  symbol: string;
  value: number;
  change: number;
  changePercent: number;
}

export interface NewsItem {
  title: string;
  source: string;
  url: string;
  publishedAt: string;
  sentiment: "BULLISH" | "BEARISH" | "NEUTRAL";
  relevanceScore: number;
  summary: string;
}

export interface SentimentData {
  overall: number;
  social: number;
  news: number;
  analyst: number;
  insider: number;
  institutional: number;
}
