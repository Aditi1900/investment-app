"use client";

import { createContext, useContext, useState } from "react";
import { loginUser, logoutUser, registerUser } from "@/lib/api";
import { useRouter } from "next/navigation";

const SessionContext = createContext(null);

const isTesting = process.env.NEXT_PUBLIC_TESTING === "true";

// Only persists to localStorage in production mode
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

export function SessionProvider({ children }) {

  const router = useRouter();
  const [sessionId, setSessionId] = useState(() => {
    if (typeof window === "undefined") return null;
    return store.get("session_id") || null;

  });

  const [user, setUser] = useState(() => {
    if (typeof window === "undefined") return null;
    const stored = store.get("user");
    return stored ? JSON.parse(stored) : null;

  });

  
  const login = async (loginVal, password) => {
    const data = await loginUser(loginVal, password);
    setSessionId(data.session_id);
    setUser(data.user);
    store.set("session_id", data.session_id);
    store.set("user", JSON.stringify(data.user));
    router.push("/dashboard");
    console.log(data);
    return data;
  };

  const logout = async () => {
    try {
      if (sessionId) await logoutUser(sessionId);
    } catch {
      // session may already be invalid, proceed with local cleanup
    } finally {
      setSessionId(null);
      setUser(null);
      store.remove("session_id");
      store.remove("user");
      router.push("/login");
    }
  };

  const register = async (loginVal, password) => {
    await registerUser(loginVal, password);
    router.push("/login");
  };

  // Call this after any backend operation that returns updated user data
  const refreshUser = (updatedUser) => {
    setUser(updatedUser);
    store.set("user", JSON.stringify(updatedUser));
  };

  return (
    <SessionContext.Provider
      value={{ sessionId, user, setUser, refreshUser, login, logout, register }}
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