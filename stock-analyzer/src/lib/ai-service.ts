import { AISignal, NewsItem, SentimentData, TrapIndicator } from "./types";

const AI_API_KEY = process.env.AI_API_KEY || "";
const AI_API_URL = process.env.AI_API_URL || "https://api.openai.com/v1/chat/completions";
const AI_MODEL = process.env.AI_MODEL || "gpt-4o";

export function isAIConfigured(): boolean {
  return AI_API_KEY.length > 0;
}

interface AIRequest {
  messages: { role: string; content: string }[];
  temperature?: number;
  max_tokens?: number;
}

async function callAI(request: AIRequest): Promise<string> {
  if (!isAIConfigured()) {
    throw new Error("AI API key not configured. Set AI_API_KEY environment variable.");
  }

  const response = await fetch(AI_API_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${AI_API_KEY}`,
    },
    body: JSON.stringify({
      model: AI_MODEL,
      messages: request.messages,
      temperature: request.temperature ?? 0.3,
      max_tokens: request.max_tokens ?? 2000,
    }),
  });

  if (!response.ok) {
    throw new Error(`AI API error: ${response.status} ${response.statusText}`);
  }

  const data = await response.json();
  return data.choices[0].message.content;
}

export async function analyzeStock(
  symbol: string,
  price: number,
  technicals: Record<string, unknown>,
  fundamentals: Record<string, unknown>
): Promise<AISignal> {
  const prompt = `You are an expert stock analyst AI. Analyze the following stock and provide a detailed recommendation.

Stock: ${symbol}
Current Price: $${price}
Technical Indicators: ${JSON.stringify(technicals)}
Fundamentals: ${JSON.stringify(fundamentals)}

Respond with a JSON object with exactly these fields:
{
  "signal": "STRONG_BUY" | "BUY" | "HOLD" | "SELL" | "STRONG_SELL",
  "confidence": 0.0-1.0,
  "reasoning": "detailed analysis string",
  "risks": ["risk1", "risk2", ...],
  "catalysts": ["catalyst1", "catalyst2", ...],
  "priceTarget": number,
  "timeframe": "timeframe string",
  "botRisk": "LOW" | "MEDIUM" | "HIGH" | "CRITICAL",
  "trapIndicators": []
}

Focus on: price action, volume patterns, momentum, valuation, sector trends, and any signs of manipulation or artificial price movement. Be specific and actionable.`;

  const result = await callAI({
    messages: [
      { role: "system", content: "You are a professional stock analyst. Respond only with valid JSON." },
      { role: "user", content: prompt },
    ],
  });

  return JSON.parse(result.replace(/```json\n?|\n?```/g, "").trim());
}

export async function detectTraps(
  symbol: string,
  priceHistory: { price: number; volume: number; date: string }[],
  socialData: Record<string, unknown>
): Promise<TrapIndicator[]> {
  const prompt = `You are an expert at detecting market manipulation and trading traps. Analyze the following data for suspicious patterns.

Stock: ${symbol}
Recent Price/Volume Data: ${JSON.stringify(priceHistory.slice(-20))}
Social/Sentiment Data: ${JSON.stringify(socialData)}

Look for these specific patterns:
- PUMP_DUMP: Coordinated price inflation followed by insider selling
- WASH_TRADE: Artificial volume through self-dealing
- SPOOFING: Fake orders to manipulate price direction
- LAYERING: Multiple spoofing orders at different price levels
- FRONT_RUNNING: Trading ahead of known large orders
- SHORT_SQUEEZE_TRAP: Manufactured squeeze setups
- FOMO_TRAP: Social media driven buying frenzy disconnected from fundamentals
- DEAD_CAT_BOUNCE: False recovery in a declining stock

Respond with a JSON array of detected traps:
[{
  "type": "TRAP_TYPE",
  "severity": "LOW" | "MEDIUM" | "HIGH" | "CRITICAL",
  "description": "what was detected",
  "evidence": ["evidence1", "evidence2"],
  "detectedAt": "ISO date string"
}]

Return an empty array if no traps detected.`;

  const result = await callAI({
    messages: [
      { role: "system", content: "You are a market manipulation detection specialist. Respond only with valid JSON." },
      { role: "user", content: prompt },
    ],
  });

  return JSON.parse(result.replace(/```json\n?|\n?```/g, "").trim());
}

export async function analyzeSentiment(
  symbol: string,
  newsItems: NewsItem[]
): Promise<SentimentData> {
  const prompt = `Analyze overall market sentiment for ${symbol} based on these news items:

${newsItems.map((n) => `- ${n.title} (${n.source}): ${n.summary}`).join("\n")}

Respond with JSON:
{
  "overall": 0-100,
  "social": 0-100,
  "news": 0-100,
  "analyst": 0-100,
  "insider": 0-100,
  "institutional": 0-100
}

Where 0 = extremely bearish, 50 = neutral, 100 = extremely bullish.`;

  const result = await callAI({
    messages: [
      { role: "system", content: "You are a sentiment analysis specialist. Respond only with valid JSON." },
      { role: "user", content: prompt },
    ],
  });

  return JSON.parse(result.replace(/```json\n?|\n?```/g, "").trim());
}

export async function getResearchSummary(
  symbol: string,
  context: Record<string, unknown>
): Promise<string> {
  const prompt = `Provide a comprehensive research summary for ${symbol}. Cover:

1. Business overview and competitive position
2. Recent financial performance and trends
3. Key growth drivers and risks
4. Valuation assessment
5. Technical analysis summary
6. Institutional activity
7. Actionable conclusion

Context data: ${JSON.stringify(context)}

Be specific, data-driven, and actionable. Format with clear sections.`;

  return callAI({
    messages: [
      { role: "system", content: "You are a senior equity research analyst writing a research note." },
      { role: "user", content: prompt },
    ],
    max_tokens: 3000,
  });
}
