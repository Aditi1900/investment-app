import { useState, useEffect } from "react";

// Fetches live prices for a list of tickers using Yahoo Finance via allorigins proxy
export function usePrices(tickers) {
    const [prices, setPrices] = useState({});
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (!tickers || tickers.length === 0) return;

        const unique = [...new Set(tickers)];
        setLoading(true);

        const fetchPrices = async () => {
            const results = {};
            await Promise.all(
                unique.map(async (ticker) => {
                    try {
                        const url = `https://query1.finance.yahoo.com/v8/finance/chart/${ticker}?interval=1d&range=5d`;
                        const proxy = `https://api.allorigins.win/get?url=${encodeURIComponent(url)}`;
                        const res = await fetch(proxy);
                        const json = await res.json();
                        const data = JSON.parse(json.contents);
                        const meta = data?.chart?.result?.[0]?.meta;
                        const closes = data?.chart?.result?.[0]?.indicators?.quote?.[0]?.close ?? [];
                        const price = meta?.regularMarketPrice ?? null;
                        const prevClose = meta?.chartPreviousClose ?? closes[closes.length - 2] ?? price;
                        const change = price && prevClose ? ((price - prevClose) / prevClose) * 100 : 0;
                        const sparkline = closes.filter(Boolean).slice(-7);
                        results[ticker] = {
                            price,
                            change: parseFloat(change.toFixed(2)),
                            positive: change >= 0,
                            sparkline,
                        };
                    } catch {
                        results[ticker] = { price: null, change: 0, positive: true, sparkline: [] };
                    }
                })
            );
            setPrices(results);
            setLoading(false);
        };

        fetchPrices();
        const interval = setInterval(fetchPrices, 30000); // refresh every 30s
        return () => clearInterval(interval);
    }, [tickers.join(",")]);

    return { prices, loading };
}