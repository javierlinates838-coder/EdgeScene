import { NextRequest, NextResponse } from "next/server";
import { isAIConfigured, analyzeStock, detectTraps, getResearchSummary } from "@/lib/ai-service";
import { getMockAISignal, getMockTechnicals } from "@/lib/mock-data";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { action, symbol, data } = body;

    if (!action || !symbol) {
      return NextResponse.json({ error: "Missing required fields: action, symbol" }, { status: 400 });
    }

    if (!isAIConfigured()) {
      const mockSignal = getMockAISignal(symbol);
      return NextResponse.json({
        ...mockSignal,
        _demo: true,
        _message: "Using demo data. Set AI_API_KEY environment variable for live AI analysis.",
      });
    }

    switch (action) {
      case "analyze": {
        const technicals = data?.technicals || getMockTechnicals();
        const result = await analyzeStock(symbol, data?.price || 0, technicals, data?.fundamentals || {});
        return NextResponse.json(result);
      }
      case "detect-traps": {
        const traps = await detectTraps(symbol, data?.priceHistory || [], data?.socialData || {});
        return NextResponse.json({ traps });
      }
      case "research": {
        const summary = await getResearchSummary(symbol, data?.context || {});
        return NextResponse.json({ summary });
      }
      default:
        return NextResponse.json({ error: `Unknown action: ${action}` }, { status: 400 });
    }
  } catch (error) {
    const message = error instanceof Error ? error.message : "Unknown error";
    return NextResponse.json({ error: message }, { status: 500 });
  }
}

export async function GET() {
  return NextResponse.json({
    status: "ok",
    aiConfigured: isAIConfigured(),
    endpoints: {
      "POST /api/ai": {
        actions: ["analyze", "detect-traps", "research"],
        requiredFields: ["action", "symbol"],
        optionalFields: ["data"],
      },
    },
  });
}
