"use client";

import { createContext, useContext, useState, useEffect, useRef } from "react";
import { useSession } from "@/context/SessionContext";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const CACHE_KEY = "edgexchange_live_data";

const readCache = () => { try { return JSON.parse(localStorage.getItem(CACHE_KEY)) ?? {}; } catch { return {}; } };
const writeCache = (data) => { try { localStorage.setItem(CACHE_KEY, JSON.stringify(data)); } catch { } };

const PortfolioContext = createContext(null);

export const usePortfolio = () => {
    const ctx = useContext(PortfolioContext);
    if (!ctx) throw new Error("usePortfolio must be used within PortfolioProvider");
    return ctx;
};

export const PortfolioProvider = ({ children }) => {
    const { sessionId, user } = useSession();
    const [liveData, setLiveData] = useState({});
    const controllers = useRef([]);
    const roundRef = useRef(0);
    const receivedRef = useRef({});

    useEffect(() => {
        setLiveData(readCache());
    }, []);

    useEffect(() => {
        controllers.current.forEach((c) => c.abort());
        controllers.current = [];
        roundRef.current = 0;
        receivedRef.current = {};

        const portfolioNames = Object.keys(user?.portfolios ?? {});
        if (!sessionId || !portfolioNames.length) return;

        portfolioNames.forEach((name) => {
            const controller = new AbortController();
            controllers.current.push(controller);

            const url = `${BASE_URL}/live_data?session_id=${sessionId}&portfolio_name=${encodeURIComponent(name)}`;

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
                                const data = JSON.parse(line);
                                receivedRef.current[name] = { data, round: roundRef.current };

                                const currentRound = roundRef.current;
                                const allPresent = portfolioNames.every(
                                    (n) => receivedRef.current[n]?.round === currentRound
                                );

                                if (allPresent) {
                                    roundRef.current++;
                                    const snapshot = Object.fromEntries(
                                        portfolioNames.map((n) => [n, receivedRef.current[n].data])
                                    );
                                    setLiveData((prev) => {
                                        const next = { ...prev, ...snapshot };
                                        writeCache(next);
                                        return next;
                                    });
                                }
                            } catch { }
                        }
                    }
                })
                .catch((err) => { if (err.name !== "AbortError") console.error("Stream error", err); });
        });

        return () => {
            controllers.current.forEach((c) => c.abort());
            controllers.current = [];
            roundRef.current = 0;
            receivedRef.current = {};
        };
    }, [sessionId, Object.keys(user?.portfolios ?? {}).join(",")]);

    return <PortfolioContext.Provider value={{ liveData }}>{children}</PortfolioContext.Provider>;
};