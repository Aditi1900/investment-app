import { useState, useEffect, useRef } from "react";

const API_BASE_PROXY = "https://api.allorigins.win/get?url=";
const MAX_RETRIES = 3;
const RETRY_BASE_MS = 500;

async function fetchWithRetry(url, retries = MAX_RETRIES) {
    for (let attempt = 0; attempt <= retries; attempt++) {
        try {
            const res = await fetch(url);
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            return await res.json();
        } catch (err) {
            if (attempt === retries) throw err;
            await new Promise((r) => setTimeout(r, RETRY_BASE_MS * 2 ** attempt));
        }
    }
}

async function fetchTickerData(ticker) {
    try {
        const url = `https://query1.finance.yahoo.com/v8/finance/chart/${ticker}?interval=1d&range=5d`;
        const json = await fetchWithRetry(`${API_BASE_PROXY}${encodeURIComponent(url)}`);
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

        // Validate we actually got a price — if not, treat as failure
        if (price == null) throw new Error("no price in response");

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
        return null; // null = failed, caller decides what to do
    }
}

export function usePrices(tickers) {
    const [prices, setPrices] = useState({});
    const [loading, setLoading] = useState(false);
    const prevPrices = useRef({});

    useEffect(() => {
        if (!tickers || tickers.length === 0) return;
        const unique = [...new Set(tickers)];
        setLoading(true);

        const fetchAll = async () => {
            const results = await Promise.all(
                unique.map(async (t) => [t, await fetchTickerData(t)])
            );

            setPrices((prev) => {
                const next = { ...prev };
                for (const [t, data] of results) {
                    if (data !== null) {
                        next[t] = data; // fresh data
                    }
                    // if null, keep whatever was there before — no blank flash
                }
                prevPrices.current = next;
                return next;
            });

            setLoading(false);
        };

        fetchAll();
        const interval = setInterval(fetchAll, 30000);
        return () => clearInterval(interval);
    }, [tickers.join(",")]);

    return { prices, loading };
}