"use client";

import { createContext, useContext, useState, useRef, useEffect } from "react";
import { useSession } from "@/context/SessionContext";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const CACHE_KEY = "edgexchange_live_data";

const readCache = () => {
    try { return JSON.parse(localStorage.getItem(CACHE_KEY)) ?? {}; }
    catch { return {}; }
};

const writeCache = (data) => {
    try { localStorage.setItem(CACHE_KEY, JSON.stringify(data)); }
    catch { }
};

const PortfolioContext = createContext(null);

export const usePortfolio = () => {
    const ctx = useContext(PortfolioContext);
    if (!ctx) throw new Error("usePortfolio must be used within PortfolioProvider");
    return ctx;
};

export const PortfolioProvider = ({ children }) => {
    const { sessionId, user } = useSession();
    const [liveData, setLiveData] = useState({});

    useEffect(() => {
        setLiveData(readCache());
    }, []);

    useEffect(() => {
        const portfolioNames = Object.keys(user?.portfolios ?? {});
        if (!sessionId || !portfolioNames.length) return;

        const controller = new AbortController();
        const url = `${BASE_URL}/live_data?session_id=${sessionId}`;

        fetch(url, { signal: controller.signal })
            .then(async (res) => {
                const reader = res.body.getReader();
                const decoder = new TextDecoder();

                while (true) {
                    const { done, value } = await reader.read();
                    if (done) break;

                    for (const line of decoder.decode(value).trim().split("\n")) {
                        if (!line) continue;
                        try {
                            const parsed = JSON.parse(line);
                            for (const entry of parsed.portfolios ?? []) {
                                if (!entry.portfolio) continue;
                                setLiveData((prev) => {
                                    const next = { ...prev, [entry.portfolio]: entry };
                                    writeCache(next);
                                    return next;
                                });
                            }
                        } catch { }
                    }
                }
            })
            .catch((err) => {
                if (err.name !== "AbortError") console.error("Stream error", err);
            });

        return () => controller.abort();
    }, [sessionId, Object.keys(user?.portfolios ?? {}).join(",")]);

    return (
        <PortfolioContext.Provider value={{ liveData }}>
            {children}
        </PortfolioContext.Provider>
    );
};