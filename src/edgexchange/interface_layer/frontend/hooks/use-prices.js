import { useState, useEffect, useRef } from "react";

const API_BASE = "http://localhost:8000";

async function fetchTickerData(ticker) {
    try {
        const res = await fetch(`${API_BASE}/quote?ticker=${ticker}`);
        if (!res.ok) return null;
        const json = await res.json();
        return json.quote ?? null;
    } catch {
        return null;
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
                        next[t] = data;
                    }
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