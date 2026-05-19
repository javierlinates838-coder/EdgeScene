import {
  StockQuote, AISignal, TrapIndicator, TechnicalIndicators,
  ChartDataPoint, MarketIndex, NewsItem, SentimentData
} from "./types";

export const marketIndices: MarketIndex[] = [
  { name: "S&P 500", symbol: "SPX", value: 5892.34, change: 23.45, changePercent: 0.40 },
  { name: "NASDAQ", symbol: "IXIC", value: 19234.56, change: -45.12, changePercent: -0.23 },
  { name: "DOW", symbol: "DJI", value: 42567.89, change: 156.78, changePercent: 0.37 },
  { name: "Russell 2000", symbol: "RUT", value: 2134.56, change: 12.34, changePercent: 0.58 },
];

export const trendingStocks: StockQuote[] = [
  {
    symbol: "NVDA", name: "NVIDIA Corp", price: 924.56, change: 34.21, changePercent: 3.84,
    volume: 45_230_000, avgVolume: 38_500_000, marketCap: 2_280_000_000_000,
    high: 932.10, low: 889.45, open: 891.00, previousClose: 890.35,
    fiftyTwoWeekHigh: 974.00, fiftyTwoWeekLow: 373.56, pe: 64.2, eps: 14.40,
    dividend: 0.04, sector: "Technology", exchange: "NASDAQ",
  },
  {
    symbol: "AAPL", name: "Apple Inc", price: 198.45, change: -1.23, changePercent: -0.62,
    volume: 52_340_000, avgVolume: 48_900_000, marketCap: 3_050_000_000_000,
    high: 200.12, low: 197.34, open: 199.80, previousClose: 199.68,
    fiftyTwoWeekHigh: 237.49, fiftyTwoWeekLow: 164.08, pe: 31.8, eps: 6.24,
    dividend: 1.00, sector: "Technology", exchange: "NASDAQ",
  },
  {
    symbol: "TSLA", name: "Tesla Inc", price: 245.67, change: 12.89, changePercent: 5.54,
    volume: 98_560_000, avgVolume: 72_000_000, marketCap: 780_000_000_000,
    high: 248.90, low: 231.45, open: 232.78, previousClose: 232.78,
    fiftyTwoWeekHigh: 299.29, fiftyTwoWeekLow: 138.80, pe: 72.5, eps: 3.39,
    dividend: null, sector: "Automotive", exchange: "NASDAQ",
  },
  {
    symbol: "MSFT", name: "Microsoft Corp", price: 425.30, change: 3.67, changePercent: 0.87,
    volume: 22_100_000, avgVolume: 20_500_000, marketCap: 3_160_000_000_000,
    high: 427.80, low: 420.10, open: 421.63, previousClose: 421.63,
    fiftyTwoWeekHigh: 430.82, fiftyTwoWeekLow: 309.45, pe: 36.1, eps: 11.78,
    dividend: 3.00, sector: "Technology", exchange: "NASDAQ",
  },
  {
    symbol: "AMZN", name: "Amazon.com Inc", price: 186.23, change: -2.45, changePercent: -1.30,
    volume: 41_200_000, avgVolume: 38_700_000, marketCap: 1_930_000_000_000,
    high: 189.50, low: 185.10, open: 188.68, previousClose: 188.68,
    fiftyTwoWeekHigh: 201.20, fiftyTwoWeekLow: 118.35, pe: 58.4, eps: 3.19,
    dividend: null, sector: "Technology", exchange: "NASDAQ",
  },
  {
    symbol: "META", name: "Meta Platforms", price: 512.34, change: 8.91, changePercent: 1.77,
    volume: 18_900_000, avgVolume: 17_200_000, marketCap: 1_310_000_000_000,
    high: 515.60, low: 502.45, open: 503.43, previousClose: 503.43,
    fiftyTwoWeekHigh: 542.81, fiftyTwoWeekLow: 279.40, pe: 28.6, eps: 17.91,
    dividend: 2.00, sector: "Technology", exchange: "NASDAQ",
  },
  {
    symbol: "GOOGL", name: "Alphabet Inc", price: 174.56, change: 1.23, changePercent: 0.71,
    volume: 25_600_000, avgVolume: 23_400_000, marketCap: 2_150_000_000_000,
    high: 175.90, low: 172.30, open: 173.33, previousClose: 173.33,
    fiftyTwoWeekHigh: 180.10, fiftyTwoWeekLow: 120.21, pe: 26.3, eps: 6.64,
    dividend: 0.80, sector: "Technology", exchange: "NASDAQ",
  },
  {
    symbol: "JPM", name: "JPMorgan Chase", price: 198.45, change: 2.34, changePercent: 1.19,
    volume: 9_800_000, avgVolume: 8_900_000, marketCap: 572_000_000_000,
    high: 199.80, low: 195.60, open: 196.11, previousClose: 196.11,
    fiftyTwoWeekHigh: 205.88, fiftyTwoWeekLow: 144.34, pe: 11.8, eps: 16.82,
    dividend: 4.60, sector: "Financial", exchange: "NYSE",
  },
];

export const screenerStocks: (StockQuote & { aiScore: number; signal: string })[] = [
  { ...trendingStocks[0], aiScore: 92, signal: "STRONG_BUY" },
  { ...trendingStocks[3], aiScore: 85, signal: "BUY" },
  { ...trendingStocks[5], aiScore: 81, signal: "BUY" },
  { ...trendingStocks[6], aiScore: 74, signal: "HOLD" },
  { ...trendingStocks[7], aiScore: 71, signal: "BUY" },
  { ...trendingStocks[1], aiScore: 58, signal: "HOLD" },
  { ...trendingStocks[4], aiScore: 52, signal: "HOLD" },
  { ...trendingStocks[2], aiScore: 45, signal: "SELL" },
];

export function generateChartData(days: number = 90): ChartDataPoint[] {
  const data: ChartDataPoint[] = [];
  let price = 150 + Math.random() * 100;
  const now = new Date();

  for (let i = days; i >= 0; i--) {
    const date = new Date(now);
    date.setDate(date.getDate() - i);
    const volatility = 0.02 + Math.random() * 0.03;
    const change = price * volatility * (Math.random() - 0.48);
    const open = price;
    const close = price + change;
    const high = Math.max(open, close) + Math.abs(change) * Math.random();
    const low = Math.min(open, close) - Math.abs(change) * Math.random();

    data.push({
      date: date.toISOString().split("T")[0],
      open: +open.toFixed(2),
      high: +high.toFixed(2),
      low: +low.toFixed(2),
      close: +close.toFixed(2),
      volume: Math.floor(20_000_000 + Math.random() * 60_000_000),
    });
    price = close;
  }
  return data;
}

export function getMockAISignal(symbol: string): AISignal {
  const signals: Record<string, AISignal> = {
    NVDA: {
      signal: "STRONG_BUY", confidence: 0.89,
      reasoning: "NVIDIA continues to dominate AI/ML accelerator market with data center revenue growing 400%+ YoY. Supply constraints are easing, new Blackwell architecture launching, and enterprise AI adoption is accelerating. Technical momentum remains strong with price above all major moving averages.",
      risks: ["Extreme valuation multiples", "Customer concentration in hyperscalers", "China export restrictions", "Potential AI spending pullback"],
      catalysts: ["Blackwell GPU architecture ramp", "Enterprise AI adoption wave", "Sovereign AI infrastructure builds", "Automotive/robotics growth"],
      priceTarget: 1050.00, timeframe: "6-12 months",
      botRisk: "LOW",
      trapIndicators: [],
    },
    TSLA: {
      signal: "HOLD", confidence: 0.62,
      reasoning: "Tesla faces margin pressure from price cuts and increasing competition. However, energy storage and FSD progress provide upside optionality. Volume surge suggests speculative interest — watch for trap signals. Mixed signals across technical indicators.",
      risks: ["Margin compression", "Increasing EV competition", "Regulatory risks", "CEO distraction factor"],
      catalysts: ["FSD robotaxi launch", "Energy storage growth", "Model refresh cycle", "Manufacturing efficiency gains"],
      priceTarget: 260.00, timeframe: "6 months",
      botRisk: "HIGH",
      trapIndicators: [
        { type: "FOMO_TRAP", severity: "HIGH", description: "Unusual volume spike with social media pump activity detected. Retail sentiment disconnected from fundamentals.", evidence: ["Volume 37% above average", "Social mention spike 450%", "Options skew extreme bullish"], detectedAt: new Date().toISOString() },
        { type: "SHORT_SQUEEZE_TRAP", severity: "MEDIUM", description: "Short interest elevated but declining. Squeeze mechanics may be priced in.", evidence: ["Short interest 3.2%", "Days to cover: 1.8", "Put/call ratio declining"], detectedAt: new Date().toISOString() },
      ],
    },
  };

  return signals[symbol] || {
    signal: "HOLD", confidence: 0.55,
    reasoning: `AI analysis for ${symbol} is pending. Connect your API key for real-time analysis powered by advanced language models.`,
    risks: ["Analysis requires API connection"],
    catalysts: ["Connect AI API for detailed catalysts"],
    priceTarget: 0, timeframe: "N/A",
    botRisk: "MEDIUM",
    trapIndicators: [],
  };
}

export function getMockTechnicals(): TechnicalIndicators {
  return {
    rsi: 58.4, macd: { value: 2.34, signal: 1.89, histogram: 0.45 },
    sma20: 218.45, sma50: 210.23, sma200: 195.67,
    ema12: 222.10, ema26: 215.80,
    bollingerBands: { upper: 238.90, middle: 218.45, lower: 198.00 },
    atr: 8.45, obv: 1_234_567_890, vwap: 220.34,
    stochastic: { k: 72.3, d: 68.1 },
  };
}

export function getMockSentiment(): SentimentData {
  return { overall: 68, social: 72, news: 65, analyst: 71, insider: 45, institutional: 78 };
}

export function getMockNews(symbol: string): NewsItem[] {
  return [
    { title: `${symbol} Surges on Strong Earnings Beat and Raised Guidance`, source: "Reuters", url: "#", publishedAt: new Date().toISOString(), sentiment: "BULLISH", relevanceScore: 0.95, summary: "The company reported quarterly earnings that exceeded analyst expectations by 15%, with revenue growth accelerating and management raising full-year guidance." },
    { title: `Analysts Divided on ${symbol} After Recent Rally`, source: "Bloomberg", url: "#", publishedAt: new Date(Date.now() - 3600000).toISOString(), sentiment: "NEUTRAL", relevanceScore: 0.88, summary: "Wall Street analysts are split on the stock's outlook following a significant rally, with some citing valuation concerns while others point to strong fundamental momentum." },
    { title: `Institutional Investors Increase Stakes in ${symbol}`, source: "CNBC", url: "#", publishedAt: new Date(Date.now() - 7200000).toISOString(), sentiment: "BULLISH", relevanceScore: 0.82, summary: "Major institutional investors have been accumulating shares, with 13F filings showing increased positions from several prominent hedge funds and pension funds." },
    { title: `${symbol} Faces Regulatory Headwinds in Key Market`, source: "WSJ", url: "#", publishedAt: new Date(Date.now() - 14400000).toISOString(), sentiment: "BEARISH", relevanceScore: 0.75, summary: "New regulatory proposals could impact the company's operations in one of its fastest-growing markets, though analysts say the near-term impact would be limited." },
    { title: `Options Activity Surges for ${symbol} Ahead of Catalyst`, source: "MarketWatch", url: "#", publishedAt: new Date(Date.now() - 21600000).toISOString(), sentiment: "BULLISH", relevanceScore: 0.71, summary: "Unusual options activity detected with heavy call buying at out-of-the-money strikes, suggesting institutional bets on near-term upside catalysts." },
  ];
}

export const trapExamples: TrapIndicator[] = [
  { type: "PUMP_DUMP", severity: "CRITICAL", description: "Coordinated social media campaign detected across multiple platforms promoting XYZQ. Price surged 340% in 48 hours with no fundamental catalyst. Wallet analysis shows concentrated holdings.", evidence: ["340% price surge in 48h", "2,400+ coordinated social posts", "Top 10 wallets hold 78% of float", "No SEC filings or news catalysts", "Volume 12x average"], detectedAt: new Date(Date.now() - 3600000).toISOString() },
  { type: "WASH_TRADE", severity: "HIGH", description: "Repetitive buy-sell patterns detected between related accounts on ABCD. Volume appears artificially inflated to create illusion of liquidity and interest.", evidence: ["Same-size orders repeating every 30s", "Bid-ask spread manipulation", "Volume inconsistent with order book depth", "Pattern matches known wash trade signatures"], detectedAt: new Date(Date.now() - 7200000).toISOString() },
  { type: "SPOOFING", severity: "HIGH", description: "Large limit orders on EFGH being placed and cancelled within milliseconds. Designed to mislead other traders about supply/demand.", evidence: ["500+ cancelled orders in 1 hour", "Order sizes 10x typical", "Cancellation rate >95%", "Price moved 2.3% during activity window"], detectedAt: new Date(Date.now() - 10800000).toISOString() },
  { type: "DEAD_CAT_BOUNCE", severity: "MEDIUM", description: "MNOP showing recovery pattern after 60% decline, but fundamentals remain severely deteriorated. Low-volume bounce typical of dead cat pattern.", evidence: ["Recovery on 30% of selloff volume", "Negative earnings revision trend", "Debt covenant concerns", "Insider selling continues"], detectedAt: new Date(Date.now() - 14400000).toISOString() },
  { type: "FOMO_TRAP", severity: "HIGH", description: "QRST experiencing viral social media attention. Price action diverging significantly from fundamental value. Retail flow dominant.", evidence: ["Social mentions up 800%", "Retail order flow 90%+ of volume", "Options gamma squeeze potential", "Short-term RSI > 85"], detectedAt: new Date(Date.now() - 18000000).toISOString() },
  { type: "FRONT_RUNNING", severity: "MEDIUM", description: "Suspicious pre-announcement accumulation detected in UVWX. Unusual options activity preceding public information release.", evidence: ["Call volume 5x average pre-announcement", "Dark pool prints at ask", "Unusual block trades", "Price drift before news release"], detectedAt: new Date(Date.now() - 21600000).toISOString() },
];
