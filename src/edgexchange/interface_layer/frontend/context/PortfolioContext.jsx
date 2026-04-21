"use client"

import { createContext, useContext, useState } from "react";

const defaultHoldings = [
  {
    ticker: "AAPL",
    name: "Apple Inc.",
    sector: "Technology",
    exchange: "Nasdaq",
    price: 189.43,
    qty: 1240,
    change: 1.42,
    positive: true,
    sparkline: [60, 62, 58, 65, 63, 67, 70, 68, 72],
  },
  {
    ticker: "NVDA",
    name: "NVIDIA Corp",
    sector: "Semiconductors",
    exchange: "Nasdaq",
    price: 875.28,
    qty: 420,
    change: 4.89,
    positive: true,
    sparkline: [40, 45, 50, 48, 55, 60, 58, 65, 70],
  },
  {
    ticker: "TSLA",
    name: "Tesla, Inc.",
    sector: "Automotive",
    exchange: "Nasdaq",
    price: 172.63,
    qty: 850,
    change: -2.15,
    positive: false,
    sparkline: [70, 68, 65, 60, 62, 58, 55, 53, 50],
  },
  {
    ticker: "VOO",
    name: "Vanguard S&P 500",
    sector: "ETF",
    exchange: "NYSE",
    price: 463.12,
    qty: 1000,
    change: 0.12,
    positive: true,
    sparkline: [50, 52, 51, 53, 54, 53, 55, 56, 57],
  },
];

const PortfolioContext = createContext(null);

export const usePortfolio = () => {
  const ctx = useContext(PortfolioContext);
  if (!ctx)
    throw new Error("usePortfolio must be used within PortfolioProvider");
  return ctx;
};

export const PortfolioProvider = ({ children }) => {
  const [funds, setFundsRaw] = useState(412000);
  const [portfolios, setPortfolios] = useState([
    {
      id: "1",
      name: "Equity Portfolio",
      description: "Main equity holdings",
      holdings: defaultHoldings,
    },
  ]);

  const setFunds = (fn) => setFundsRaw(fn);

  const addPortfolio = (name, description) => {
    const p = { id: Date.now().toString(), name, description, holdings: [] };
    setPortfolios((prev) => [...prev, p]);
    return p;
  };

  const removePortfolio = (id) => {
    setPortfolios((prev) => prev.filter((p) => p.id !== id));
  };

  const executeTrade = (
    portfolioId,
    ticker,
    name,
    sector,
    exchange,
    price,
    qty,
    side,
  ) => {
    const cost = price * qty;
    if (side === "buy" && cost > funds) return false;

    setPortfolios((prev) =>
      prev.map((p) => {
        if (p.id !== portfolioId) return p;
        const existing = p.holdings.find((h) => h.ticker === ticker);
        let newHoldings;
        if (side === "buy") {
          if (existing) {
            newHoldings = p.holdings.map((h) =>
              h.ticker === ticker ? { ...h, qty: h.qty + qty, price } : h,
            );
          } else {
            newHoldings = [
              ...p.holdings,
              {
                ticker,
                name,
                sector,
                exchange,
                price,
                qty,
                change: 0,
                positive: true,
                sparkline: [50, 50, 50, 50, 50],
              },
            ];
          }
        } else {
          if (!existing || existing.qty < qty) return p;
          if (existing.qty === qty) {
            newHoldings = p.holdings.filter((h) => h.ticker !== ticker);
          } else {
            newHoldings = p.holdings.map((h) =>
              h.ticker === ticker ? { ...h, qty: h.qty - qty, price } : h,
            );
          }
        }
        return { ...p, holdings: newHoldings };
      }),
    );

    if (side === "buy") {
      setFundsRaw((prev) => prev - cost);
    } else {
      setFundsRaw((prev) => prev + cost);
    }
    return true;
  };

  return (
    <PortfolioContext.Provider
      value={{
        funds,
        setFunds,
        portfolios,
        addPortfolio,
        removePortfolio,
        executeTrade,
      }}
    >
      {children}
    </PortfolioContext.Provider>
  );
};
