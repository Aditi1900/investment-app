import { useState, useEffect } from "react";

const API_BASE = "http://localhost:8000";

const fetchQuote = (ticker) =>
  fetch(`${API_BASE}/quote?ticker=${ticker}`)
    .then((res) => res.ok ? res.json() : null)
    .then((json) => json?.quote ?? null)
    .catch(() => null);

export function usePrices(tickers) {
  const [prices,  setPrices]  = useState({});
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const unique = [...new Set(tickers)];
    if (!unique.length) return;

    const fetchAll = async () => {
      setLoading(true);
      const results = await Promise.all(unique.map(async (t) => [t, await fetchQuote(t)]));
      setPrices((prev) => {
        const next = { ...prev };
        for (const [t, data] of results) if (data) next[t] = data;
        return next;
      });
      setLoading(false);
    };

    fetchAll();
    const interval = setInterval(fetchAll, 30_000);
    return () => clearInterval(interval);
  }, [tickers.join(",")]);

  return { prices, loading };
}
