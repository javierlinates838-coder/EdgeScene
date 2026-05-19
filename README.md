# StockLens — AI-Powered Stock Analysis Platform

StockLens is a modern stock analysis platform that uses AI to help you make smarter investment decisions. It provides buy/sell signals, detects market manipulation and bot activity, screens for high-potential stocks, and offers an AI research assistant — all in a sleek dark-themed dashboard.

## Features

- **Dashboard** — Market indices, trending stocks with AI scores, quick insights, and active trap alerts
- **Stock Analysis** — Price charts, technical indicators (RSI, MACD, Bollinger Bands, VWAP, etc.), AI buy/sell signals with confidence scores, sentiment radar, and news feed
- **Stock Screener** — Filter and sort stocks by AI score, signal type, sector, price, volume, and market cap
- **Bot & Trap Detector** — Real-time detection of Pump & Dump, Wash Trading, Spoofing, FOMO Traps, Dead Cat Bounces, and more with severity ratings and protection advice
- **AI Research Assistant** — Chat interface to ask anything about stocks and markets, with preset prompts and live market data panels

## Quick Start

```bash
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## AI Configuration

The platform works out of the box with demo data. To enable live AI analysis, set your API key:

```bash
# Option 1: Environment variable
export AI_API_KEY="your-api-key-here"

# Option 2: .env.local file
echo 'AI_API_KEY=your-api-key-here' >> .env.local

# Option 3: Enter it in the Research page settings panel
```

Supports OpenAI, Anthropic, and any compatible chat completions API. You can also configure:

```bash
AI_API_URL="https://api.openai.com/v1/chat/completions"  # API endpoint
AI_MODEL="gpt-4o"                                         # Model to use
```

## Tech Stack

- [Next.js 16](https://nextjs.org/) with App Router
- [TypeScript](https://www.typescriptlang.org/)
- [Tailwind CSS](https://tailwindcss.com/) with custom dark theme
- [Recharts](https://recharts.org/) for charts
- [Lucide React](https://lucide.dev/) for icons

## API Routes

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/stock` | GET | List all stocks or get quote by symbol |
| `/api/stock?symbol=NVDA&type=full` | GET | Full stock data (quote, chart, technicals, sentiment, news) |
| `/api/ai` | POST | AI analysis, trap detection, or research summary |
| `/api/ai` | GET | Check AI configuration status |

## Project Structure

```
src/
├── app/
│   ├── page.tsx              # Dashboard
│   ├── analyze/page.tsx      # Stock analysis
│   ├── screener/page.tsx     # Stock screener
│   ├── traps/page.tsx        # Bot & trap detector
│   ├── research/page.tsx     # AI research assistant
│   └── api/
│       ├── ai/route.ts       # AI analysis endpoints
│       └── stock/route.ts    # Stock data endpoints
├── components/
│   ├── Sidebar.tsx           # Navigation sidebar
│   ├── SignalBadge.tsx       # Signal/severity badges and score meters
│   └── StockSearch.tsx       # Global stock search
└── lib/
    ├── types.ts              # TypeScript interfaces
    ├── mock-data.ts          # Demo data and generators
    └── ai-service.ts         # AI API integration layer
```

## License

This project is a research and educational tool, not financial advice.
