import { useState, useEffect } from "react";

const API_BASE_PROXY = "https://api.allorigins.win/get?url=";

async function fetchTickerData(ticker) {
    try {
        const url = `https://query1.finance.yahoo.com/v8/finance/chart/${ticker}?interval=1d&range=5d`;
        const res = await fetch(`${API_BASE_PROXY}${encodeURIComponent(url)}`);
        const json = await res.json();
        const data = JSON.parse(json.contents);
        const result = data?.chart?.result?.[0];
        const meta = result?.meta;
        const quote = result?.indicators?.quote?.[0];
        const closes = quote?.close ?? [];
        const opens = quote?.open ?? [];
        const highs = quote?.high ?? [];
        const lows = quote?.low ?? [];
        const volumes = quote?.volume ?? [];

        const price = meta?.regularMarketPrice ?? null;
        const prevClose = meta?.chartPreviousClose ?? closes[closes.length - 2] ?? price;
        const change = price && prevClose ? ((price - prevClose) / prevClose) * 100 : 0;
        const sparkline = closes.filter(Boolean);

        const lastIdx = closes.length - 1;

        return {
            price,
            change: parseFloat(change.toFixed(2)),
            positive: change >= 0,
            sparkline,
            open: opens[lastIdx] ?? null,
            high: highs[lastIdx] ?? null,
            low: lows[lastIdx] ?? null,
            volume: volumes[lastIdx] ?? null,
            companyName: meta?.longName ?? meta?.shortName ?? ticker,
            exchange: meta?.exchangeName ?? null,
            currency: meta?.currency ?? "USD",
            fiftyTwoWeekHigh: meta?.fiftyTwoWeekHigh ?? null,
            fiftyTwoWeekLow: meta?.fiftyTwoWeekLow ?? null,
        };
    } catch {
        return {
            price: null, change: 0, positive: true, sparkline: [],
            open: null, high: null, low: null, volume: null,
            companyName: ticker, exchange: null, currency: "USD",
            fiftyTwoWeekHigh: null, fiftyTwoWeekLow: null,
        };
    }
}

export function usePrices(tickers) {
    const [prices, setPrices] = useState({});
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (!tickers || tickers.length === 0) return;
        const unique = [...new Set(tickers)];
        setLoading(true);

        const fetchAll = async () => {
            const results = {};
            await Promise.all(unique.map(async (t) => {
                results[t] = await fetchTickerData(t);
            }));
            setPrices(results);
            setLoading(false);
        };

        fetchAll();
        const interval = setInterval(fetchAll, 30000);
        return () => clearInterval(interval);
    }, [tickers.join(",")]);

    return { prices, loading };
}