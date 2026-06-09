"use client";

import { createContext, useContext, useState, useEffect } from "react";
import { loginUser, logoutUser, registerUser } from "@/lib/api";
import { useRouter } from "next/navigation";

const SessionContext = createContext(null);

const isTesting = process.env.NEXT_PUBLIC_TESTING === "true";
const API_BASE   = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Storage helpers — no-ops in test mode
const store = {
  set:    (k, v) => !isTesting && localStorage.setItem(k, v),
  get:    (k)    => isTesting ? null : localStorage.getItem(k),
  remove: (k)    => !isTesting && localStorage.removeItem(k),
};

const clearSession = () => {
  ["session_id", "user"].forEach(store.remove);
  document.cookie = "session_id=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT";
};

const setSessionCookie = (id) => {
  document.cookie = `session_id=${id}; path=/; SameSite=Lax`;
};

export function SessionProvider({ children }) {
  const router = useRouter();
  const [sessionId, setSessionId] = useState(null);
  const [user,      setUser]      = useState(null);
  const [ready,     setReady]     = useState(false);

  // Validate stored session on mount
  useEffect(() => {
    const stored = store.get("session_id");
    if (!stored) return setReady(true);

    fetch(`${API_BASE}/user?session_id=${stored}`)
      .then((res) => { if (!res.ok) throw new Error(); return res.json(); })
      .then(({ user }) => {
        if (!user) throw new Error();
        setSessionId(stored);
        setUser(user);
        store.set("user", JSON.stringify(user));
      })
      .catch(() => { clearSession(); router.push("/login"); })
      .finally(() => setReady(true));
  }, []);

  const persistUser = (id, user) => {
    setSessionId(id);
    setUser(user);
    store.set("session_id", id);
    store.set("user", JSON.stringify(user));
    setSessionCookie(id);
  };

  const login = async (login, password) => {
    const data = await loginUser(login, password);
    persistUser(data.session_id, data.user);
    return data;
  };

  const logout = async () => {
    try { if (sessionId) await logoutUser(sessionId); } catch {}
    setSessionId(null);
    setUser(null);
    clearSession();
    router.push("/login");
  };

  const register = async (login, password) => {
    await registerUser(login, password);
    router.push("/login");
  };

  const refreshUser = (updatedUser) => {
    setUser(updatedUser);
    store.set("user", JSON.stringify(updatedUser));
  };

  return (
    <SessionContext.Provider value={{ sessionId, user, setUser, refreshUser, login, logout, register, ready }}>
      {children}
    </SessionContext.Provider>
  );
}

export const useSession = () => {
  const ctx = useContext(SessionContext);
  if (!ctx) throw new Error("useSession must be used within SessionProvider");
  return ctx;
};
