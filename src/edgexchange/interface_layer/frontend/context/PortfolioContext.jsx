"use client";

import { createContext, useContext, useState, useEffect, useRef } from "react";
import { useSession } from "@/context/SessionContext";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const PortfolioContext = createContext(null);

const CACHE_KEY = "edgexchange_live_data";

function readCache() {
    try {
        const raw = localStorage.getItem(CACHE_KEY);
        return raw ? JSON.parse(raw) : {};
    } catch {
        return {};
    }
}

function writeCache(data) {
    try {
        localStorage.setItem(CACHE_KEY, JSON.stringify(data));
    } catch {
        // storage quota exceeded or unavailable — fail silently
    }
}

export const usePortfolio = () => {
    const ctx = useContext(PortfolioContext);
    if (!ctx) throw new Error("usePortfolio must be used within PortfolioProvider");
    return ctx;
};

export const PortfolioProvider = ({ children }) => {
    const { sessionId, user } = useSession();
    const [liveData, setLiveData] = useState(() => readCache());
    const controllersRef = useRef([]);

    useEffect(() => {
        controllersRef.current.forEach((c) => c.abort());
        controllersRef.current = [];

        const portfolioNames = Object.keys(user?.portfolios ?? {});
        if (!sessionId || portfolioNames.length === 0) return;

        portfolioNames.forEach((name) => {
            const controller = new AbortController();
            controllersRef.current.push(controller);

            const url = `${BASE_URL}/live_data?session_id=${sessionId}&portfolio_name=${encodeURIComponent(name)}`;

            fetch(url, { signal: controller.signal })
                .then(async (res) => {
                    const reader = res.body.getReader();
                    const decoder = new TextDecoder();
                    while (true) {
                        const { done, value } = await reader.read();
                        if (done) break;
                        const lines = decoder.decode(value).trim().split("\n");
                        for (const line of lines) {
                            if (line) {
                                try {
                                    const data = JSON.parse(line);
                                    setLiveData((prev) => {
                                        const next = { ...prev, [name]: data };
                                        writeCache(next);
                                        return next;
                                    });
                                } catch {
                                    // skip malformed lines
                                }
                            }
                        }
                    }
                })
                .catch((err) => {
                    if (err.name !== "AbortError") console.error("Stream error", err);
                });
        });

        return () => {
            controllersRef.current.forEach((c) => c.abort());
            controllersRef.current = [];
        };
    }, [sessionId, Object.keys(user?.portfolios ?? {}).join(",")]);

    return (
        <PortfolioContext.Provider value={{ liveData }}>
            {children}
        </PortfolioContext.Provider>
    );
};