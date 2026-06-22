import { useState, useEffect, useRef } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const fetchQuote = (ticker) =>
    fetch(`${API_BASE}/quote?ticker=${ticker}`)
        .then(async (res) => {
            if (res.ok) return res.json();

            const text = await res.text();
            let detail;
            try { detail = JSON.parse(text)?.detail; } catch { }
            return { error: res.status === 400 ? detail : detail || `Server error (${res.status})` };
        })
        .then((json) => {
            if (json?.error) return { error: json.error };
            return json?.quote ?? null;
        })
        .catch(() => null);

export function usePrices(tickers) {
    const [prices, setPrices] = useState({});
    const [errors, setErrors] = useState({});
    const intervalRef = useRef(null);
    const isFetchingRef = useRef(false);

    useEffect(() => {
        const unique = [...new Set(tickers)];
        if (!unique.length) return;

        const fetchAll = async () => {
            if (isFetchingRef.current) return;
            isFetchingRef.current = true;

            try {
                const results = await Promise.all(unique.map(async (t) => [t, await fetchQuote(t)]));

                const hasError = results.some(([, data]) => data?.error);

                setPrices((prev) => {
                    const next = { ...prev };
                    for (const [t, data] of results) if (data && !data.error) next[t] = data;
                    return next;
                });
                setErrors((prev) => {
                    const next = { ...prev };
                    for (const [t, data] of results) {
                        if (data?.error) next[t] = data.error;
                        else if (data !== null) delete next[t];
                    }
                    return next;
                });

                if (hasError && intervalRef.current) {
                    clearInterval(intervalRef.current);
                    intervalRef.current = null;
                }
            } finally {
                isFetchingRef.current = false;
            }
        };

        fetchAll();
        intervalRef.current = setInterval(fetchAll, 2_000);
        return () => {
            clearInterval(intervalRef.current);
            intervalRef.current = null;
            isFetchingRef.current = false;
        };
    }, [tickers.join(",")]);

    const loading = tickers.some((t) => !prices[t] && !errors[t]);

    return { prices, errors, loading };
}