const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function request(endpoint, options = {}) {
  const res = await fetch(`${BASE_URL}${endpoint}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Request failed");
  }
  return res.json();
}

const post = (endpoint, body) => request(endpoint, { method: "POST", body: JSON.stringify(body) });

// Auth
export const registerUser = (login, password) => post("/register", { login, password });
export const loginUser    = (login, password) => post("/login",    { login, password });
export const logoutUser   = (session_id)       => post("/logout",  { session_id });

// User
export const getUser    = (session_id)                        => request(`/user?session_id=${session_id}`);
export const fundAccount = (session_id, funds_requested)      => post("/fund", { session_id, funds_requested });

// Portfolios
export const createPortfolio = (session_id, name) => post("/portfolio/create", { session_id, name });
export const removePortfolio = (session_id, name) => post("/portfolio/remove", { session_id, name });

// Trades
export const executeBuy  = (session_id, portfolio_name, ticker, quantity) => post("/buy",  { session_id, portfolio_name, ticker, quantity });
export const executeSell = (session_id, portfolio_name, ticker, quantity) => post("/sell", { session_id, portfolio_name, ticker, quantity });

// Live portfolio stream
export function subscribeLiveData(session_id, portfolio_name, onData, onError) {
  const url = `${BASE_URL}/live_data?session_id=${session_id}&portfolio_name=${portfolio_name}`;
  const controller = new AbortController();

  fetch(url, { signal: controller.signal })
    .then(async (res) => {
      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        for (const line of decoder.decode(value).trim().split("\n")) {
          if (line) try { onData(JSON.parse(line)); } catch {}
        }
      }
    })
    .catch((err) => { if (err.name !== "AbortError") onError?.(err); });

  return () => controller.abort();
}

// Stock data
export const getStockData = (ticker) =>
  fetch(`/api/stock/${ticker.toUpperCase()}`)
    .then(async (res) => {
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Failed to fetch stock");
      return data;
    });
