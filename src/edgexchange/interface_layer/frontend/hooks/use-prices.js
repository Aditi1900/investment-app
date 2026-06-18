import { useState, useEffect, useRef } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const fetchQuote = (ticker) =>
    fetch(`${API_BASE}/quote?ticker=${ticker}`)
        .then((res) => {
            if (res.status === 400) return { error: "not_found" };
            return res.ok ? res.json() : null;
        })
        .then((json) => {
            if (json?.error === "not_found") return { error: "not_found" };
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
            if (isFetchingRef.current) return; // skip if previous cycle isn't done
            isFetchingRef.current = true;

            try {
                const results = await Promise.all(unique.map(async (t) => [t, await fetchQuote(t)]));

                const hasNotFound = results.some(([, data]) => data?.error === "not_found");

                setPrices((prev) => {
                    const next = { ...prev };
                    for (const [t, data] of results) if (data && !data.error) next[t] = data;
                    return next;
                });
                setErrors((prev) => {
                    const next = { ...prev };
                    for (const [t, data] of results) {
                        if (data?.error === "not_found") next[t] = "Ticker does not exist";
                        else if (data !== null) delete next[t];
                    }
                    return next;
                });

                if (hasNotFound && intervalRef.current) {
                    clearInterval(intervalRef.current);
                    intervalRef.current = null;
                }
            } finally {
                isFetchingRef.current = false;
            }
        };

        fetchAll();
        intervalRef.current = setInterval(fetchAll, 5_000);
        return () => {
            clearInterval(intervalRef.current);
            intervalRef.current = null;
            isFetchingRef.current = false;
        };
    }, [tickers.join(",")]);

    const loading = tickers.some((t) => !prices[t] && !errors[t]);

    return { prices, errors, loading };
}