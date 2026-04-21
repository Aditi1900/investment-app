"use client";

import { createContext, useContext, useState, useEffect } from "react";
import { loginUser, logoutUser, registerUser } from "@/lib/api";
import { useRouter } from "next/navigation";

const SessionContext = createContext(null);

const isTesting = process.env.NEXT_PUBLIC_TESTING === "true";
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const store = {
    set: (key, value) => {
        if (!isTesting) localStorage.setItem(key, value);
    },
    get: (key) => {
        if (isTesting) return null;
        return localStorage.getItem(key);
    },
    remove: (key) => {
        if (!isTesting) localStorage.removeItem(key);
    },
};

const cookie = {
    set: (key, value) => {
        document.cookie = `${key}=${value}; path=/; SameSite=Lax`;
    },
    remove: (key) => {
        document.cookie = `${key}=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT`;
    },
};

export function SessionProvider({ children }) {
    const router = useRouter();

    const [sessionId, setSessionId] = useState(null);
    const [user, setUser] = useState(null);
    const [ready, setReady] = useState(false);

    // On mount, hydrate session and fetch fresh user data from backend
    useEffect(() => {
        const storedSession = store.get("session_id");
        const storedUser = store.get("user");

        if (storedSession) {
            setSessionId(storedSession);
            // Always fetch fresh user from backend to avoid stale localStorage
            fetch(`${API_BASE}/user?session_id=${storedSession}`)
                .then((res) => res.ok ? res.json() : null)
                .then((data) => {
                    if (data?.user) {
                        setUser(data.user);
                        store.set("user", JSON.stringify(data.user));
                    } else if (storedUser) {
                        try { setUser(JSON.parse(storedUser)); } catch { store.remove("user"); }
                    }
                })
                .catch(() => {
                    if (storedUser) {
                        try { setUser(JSON.parse(storedUser)); } catch { store.remove("user"); }
                    }
                })
                .finally(() => setReady(true));
        } else {
            setReady(true);
        }
    }, []);

    const login = async (loginVal, password) => {
        const data = await loginUser(loginVal, password);
        setSessionId(data.session_id);
        setUser(data.user);
        store.set("session_id", data.session_id);
        store.set("user", JSON.stringify(data.user));
        cookie.set("session_id", data.session_id);
        return data;
    };

    const logout = async () => {
        try {
            if (sessionId) await logoutUser(sessionId);
        } catch {
            // session may already be invalid
        } finally {
            setSessionId(null);
            setUser(null);
            store.remove("session_id");
            store.remove("user");
            cookie.remove("session_id");
            router.push("/login");
        }
    };

    const register = async (loginVal, password) => {
        await registerUser(loginVal, password);
        router.push("/login");
    };

    const refreshUser = (updatedUser) => {
        setUser(updatedUser);
        store.set("user", JSON.stringify(updatedUser));
    };

    return (
        <SessionContext.Provider
            value={{ sessionId, user, setUser, refreshUser, login, logout, register, ready }}
        >
            {children}
        </SessionContext.Provider>
    );
}

export const useSession = () => {
    const ctx = useContext(SessionContext);
    if (!ctx) throw new Error("useSession must be used within SessionProvider");
    return ctx;
};