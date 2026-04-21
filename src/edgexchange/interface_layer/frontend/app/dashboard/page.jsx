"use client";

import { useState, useEffect } from "react";
import { Building2 } from "lucide-react";
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from "recharts";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { toast } from "@/hooks/use-toast";
import { useSession } from "@/context/SessionContext";
import { fundAccount } from "@/lib/api";
import AppLayout from "@/components/AppLayout";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const COLORS = [
  "hsl(220, 40%, 13%)",
  "hsl(220, 30%, 35%)",
  "hsl(214, 20%, 75%)",
  "hsl(166, 60%, 45%)",
  "hsl(38, 92%, 50%)",
];

export default function Dashboard() {
  const { user, setUser, sessionId } = useSession();
  const [addFundsOpen, setAddFundsOpen] = useState(false);
  const [fundAmount, setFundAmount] = useState("");
  const [liveData, setLiveData] = useState({});

  const funds = user?.balance || 0;
  const portfolioNames = Object.keys(user?.portfolios || {});

  useEffect(() => {
    if (!sessionId || portfolioNames.length === 0) return;

    const controllers = portfolioNames.map((name) => {
      const controller = new AbortController();
      const url = `${BASE_URL}/live_data?session_id=${sessionId}&portfolio_name=${name}`;

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
                  setLiveData((prev) => ({ ...prev, [name]: data }));
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

      return controller;
    });

    return () => controllers.forEach((c) => c.abort());
  }, [sessionId, portfolioNames.join(",")]);

  const handleAddFunds = async () => {
    const amount = parseFloat(fundAmount);
    if (isNaN(amount) || amount <= 0) {
      toast({
        title: "Invalid amount",
        description: "Please enter a valid positive number.",
        variant: "destructive",
      });
      return;
    }
    try {
      const data = await fundAccount(sessionId, amount);
      setUser(data.user);
      setFundAmount("");
      setAddFundsOpen(false);
      toast({
        title: "Funds Added",
        description: `$${amount.toLocaleString(undefined, {
          minimumFractionDigits: 2,
        })} has been added to your account.`,
      });
    } catch (err) {
      toast({ title: "Error", description: err.message, variant: "destructive" });
    }
  };

  const portfolios = Object.values(user?.portfolios || {}).map((p) => {
    const live = liveData[p.name];
    const holdings = live?.holdings || [];
    const totalValue = live?.total || "$0.00";
    const chartData =
      holdings.length > 0
        ? holdings.map((h) => ({ name: h.ticker, value: h.value, label: h.label }))
        : [{ name: "Empty", value: 1, label: "No holdings" }];
    const topHolding =
      holdings.length > 0
        ? holdings.reduce((a, b) => (b.value > a.value ? b : a), holdings[0])
        : null;

    return {
      id: p.name,
      name: p.name,
      totalValue,
      chartData,
      topHolding,
      holdings,
      isEmpty: holdings.length === 0,
    };
  });

  return (
    <AppLayout>
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-foreground">Dashboard</h1>
        <p className="text-muted-foreground">Hello, {user?.login || "User"}</p>
      </div>

      {/* Available Funds */}
      <div className="card-surface flex items-center justify-between p-6">
        <div className="flex items-center gap-4">
          <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-secondary">
            <Building2 size={20} className="text-foreground" />
          </div>
          <div>
            <div className="section-label text-accent">Available Funds</div>
            <div className="text-2xl font-bold text-foreground">
              ${funds.toLocaleString(undefined, { minimumFractionDigits: 2 })}
            </div>
          </div>
        </div>
        <button
          onClick={() => setAddFundsOpen(true)}
          className="inline-flex items-center gap-2 rounded-lg bg-primary px-6 py-3 text-sm font-semibold text-primary-foreground"
        >
          <span className="text-lg">⊕</span> Add Funds
        </button>
      </div>

      {/* Portfolio Allocations */}
      <div>
        <div className="section-label mb-4">Portfolio Allocations</div>
        {portfolios.length === 0 ? (
          <div className="card-surface flex items-center justify-center py-16 text-sm text-muted-foreground">
            No portfolios yet. Create one on the Portfolio page.
          </div>
        ) : (
          <div className="grid gap-6 md:grid-cols-3">
            {portfolios.map((p) => (
              <div key={p.id} className="card-surface p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-lg font-bold text-foreground">
                      {p.name}
                    </div>
                    <div className="text-xs text-muted-foreground">
                      {p.isEmpty ? "No holdings" : `${p.holdings.length} stocks`}
                    </div>
                  </div>
                  <span className="text-xs font-medium text-muted-foreground">
                    {p.totalValue}
                  </span>
                </div>

                <div className="relative mx-auto my-6 h-40 w-40">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={p.chartData}
                        cx="50%"
                        cy="50%"
                        innerRadius={50}
                        outerRadius={70}
                        dataKey="value"
                        stroke="none"
                      >
                        {p.chartData.map((_, i) => (
                          <Cell key={i} fill={COLORS[i % COLORS.length]} />
                        ))}
                      </Pie>
                      {!p.isEmpty && (
                        <Tooltip
                          formatter={(val, name) => [`$${Number(val).toFixed(2)}`, name]}
                          contentStyle={{
                            backgroundColor: "hsl(0 0% 100%)",
                            border: "1px solid hsl(214 20% 90%)",
                            borderRadius: "8px",
                            fontSize: "11px",
                          }}
                        />
                      )}
                    </PieChart>
                  </ResponsiveContainer>
                  <div className="absolute inset-0 flex flex-col items-center justify-center">
                    <span className="text-2xl font-bold text-foreground">
                      {p.isEmpty ? "—" : p.holdings.length}
                    </span>
                    <span className="text-[10px] uppercase tracking-wider text-muted-foreground">
                      {p.isEmpty ? "empty" : p.topHolding?.ticker || "—"}
                    </span>
                  </div>
                </div>

                <div className="space-y-2">
                  {p.holdings.slice(0, 4).map((h, i) => (
                    <div
                      key={h.ticker}
                      className="flex items-center justify-between text-sm"
                    >
                      <div className="flex items-center gap-2">
                        <div
                          className="h-2 w-2 rounded-full"
                          style={{ backgroundColor: COLORS[i % COLORS.length] }}
                        />
                        <span className="text-foreground">{h.ticker}</span>
                      </div>
                      <span className="text-muted-foreground">
                        ${Number(h.value).toFixed(2)}
                      </span>
                    </div>
                  ))}
                  {p.isEmpty && (
                    <div className="text-center text-xs text-muted-foreground">
                      No holdings yet
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Add Funds Dialog */}
      <Dialog open={addFundsOpen} onOpenChange={setAddFundsOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Add Funds</DialogTitle>
            <DialogDescription>
              Enter the amount you&apos;d like to deposit into your account.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 pt-2">
            <Input
              type="number"
              placeholder="Enter amount (USD)"
              value={fundAmount}
              onChange={(e) => setFundAmount(e.target.value)}
              min="0"
              step="0.01"
            />
            <div className="flex gap-2">
              {[1000, 5000, 10000, 50000].map((amt) => (
                <button
                  key={amt}
                  onClick={() => setFundAmount(String(amt))}
                  className="rounded-lg border border-border px-3 py-1.5 text-xs font-medium text-foreground hover:bg-secondary"
                >
                  ${amt.toLocaleString()}
                </button>
              ))}
            </div>
            <button
              onClick={handleAddFunds}
              className="w-full rounded-lg bg-primary py-3 text-sm font-semibold text-primary-foreground"
            >
              Confirm Deposit
            </button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
    </AppLayout>
  );
}