import { NextRequest, NextResponse } from "next/server";
import { trendingStocks, generateChartData, getMockTechnicals, getMockSentiment, getMockNews } from "@/lib/mock-data";

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const symbol = searchParams.get("symbol");
  const type = searchParams.get("type") || "quote";

  if (!symbol) {
    return NextResponse.json(
      { stocks: trendingStocks },
      { headers: { "Cache-Control": "public, s-maxage=60" } }
    );
  }

  const stock = trendingStocks.find((s) => s.symbol.toUpperCase() === symbol.toUpperCase());

  if (!stock) {
    return NextResponse.json({ error: `Stock ${symbol} not found` }, { status: 404 });
  }

  switch (type) {
    case "quote":
      return NextResponse.json({ quote: stock });

    case "chart": {
      const days = parseInt(searchParams.get("days") || "90");
      const chartData = generateChartData(days);
      return NextResponse.json({ symbol: stock.symbol, chart: chartData });
    }

    case "technicals":
      return NextResponse.json({ symbol: stock.symbol, technicals: getMockTechnicals() });

    case "sentiment":
      return NextResponse.json({ symbol: stock.symbol, sentiment: getMockSentiment() });

    case "news":
      return NextResponse.json({ symbol: stock.symbol, news: getMockNews(stock.symbol) });

    case "full":
      return NextResponse.json({
        quote: stock,
        chart: generateChartData(90),
        technicals: getMockTechnicals(),
        sentiment: getMockSentiment(),
        news: getMockNews(stock.symbol),
      });

    default:
      return NextResponse.json({ error: `Unknown type: ${type}` }, { status: 400 });
  }
}
