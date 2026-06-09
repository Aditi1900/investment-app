"use client";

import { useState } from "react";
import { Building2 } from "lucide-react";
import { PieChart, Pie, Cell, Tooltip } from "recharts";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { toast } from "@/hooks/use-toast";
import { useSession } from "@/context/SessionContext";
import { usePortfolio } from "@/context/PortfolioContext";
import { fundAccount } from "@/lib/api";
import AppLayout from "@/components/AppLayout";

const COLORS = [
  "hsl(220, 40%, 13%)",
  "hsl(220, 30%, 35%)",
  "hsl(214, 20%, 75%)",
  "hsl(166, 60%, 45%)",
  "hsl(38, 92%, 50%)",
];

const QUICK_AMOUNTS = [1000, 5000, 10000, 50000];

function PortfolioCard({ portfolio: p }) {
  const { name, totalValue, chartData, holdings, isEmpty, isLoading } = p;
  const topHolder = holdings.length ? holdings.reduce((a, b) => b.value > a.value ? b : a) : null;

  return (
    <div className="card-surface p-6">
      <div className="flex items-center justify-between">
        <div>
          <div className="text-lg font-bold text-foreground">{name}</div>
          <div className="text-xs text-muted-foreground">
            {!isLoading && (isEmpty ? "No holdings" : `${holdings.length} stocks`)}
          </div>
        </div>
        {!isLoading && <span className="text-xs font-medium text-muted-foreground">{totalValue}</span>}
      </div>

      <div className="relative mx-auto my-6 h-40 w-40">
        {isLoading ? (
          <div className="relative h-full w-full">
            <div className="h-full w-full rounded-full border-[20px] border-secondary opacity-20" />
            <div className="absolute inset-0 rounded-full border-[20px] border-transparent border-t-muted-foreground opacity-40 animate-spin" style={{ animationDuration: "1.2s" }} />
          </div>
        ) : (
          <PieChart width={160} height={160}>
            <Pie data={chartData} cx="50%" cy="50%" innerRadius={50} outerRadius={70} dataKey="value" stroke="none" animationBegin={0} animationDuration={600} animationEasing="ease-out">
              {chartData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
            </Pie>
            {!isEmpty && (
              <Tooltip
                formatter={(val, name) => [`$${Number(val).toFixed(2)}`, name]}
                contentStyle={{ backgroundColor: "hsl(0 0% 100%)", border: "1px solid hsl(214 20% 90%)", borderRadius: "8px", fontSize: "11px" }}
              />
            )}
            <text x={80} y={75} textAnchor="middle" dominantBaseline="middle" style={{ fontSize: "22px", fontWeight: "700", fill: "currentColor" }}>
              {isEmpty ? "—" : holdings.length}
            </text>
            <text x={80} y={97} textAnchor="middle" dominantBaseline="middle" style={{ fontSize: "9px", letterSpacing: "0.1em", fill: "currentColor", opacity: 0.5 }}>
              {isEmpty ? "EMPTY" : topHolder?.ticker || "—"}
            </text>
          </PieChart>
        )}
      </div>

      <div className="space-y-2">
        {holdings.slice(0, 4).map((h, i) => (
          <div key={h.ticker} className="flex items-center justify-between text-sm">
            <div className="flex items-center gap-2">
              <div className="h-2 w-2 rounded-full" style={{ backgroundColor: COLORS[i % COLORS.length] }} />
              <span className="text-foreground">{h.ticker}</span>
            </div>
            <span className="text-muted-foreground">${Number(h.value).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
          </div>
        ))}
        {!isLoading && isEmpty && <div className="text-center text-xs text-muted-foreground">No holdings yet</div>}
      </div>
    </div>
  );
}

export default function Dashboard() {
  const { user, setUser, sessionId } = useSession();
  const { liveData } = usePortfolio();
  const [addFundsOpen, setAddFundsOpen] = useState(false);
  const [fundAmount,   setFundAmount]   = useState("");

  const funds = user?.balance ?? 0;

  const portfolios = Object.values(user?.portfolios ?? {}).map((p) => {
    const live     = liveData[p.name];
    const holdings = live?.holdings ?? [];
    const isEmpty  = !holdings.length;
    return {
      id: p.name,
      name: p.name,
      totalValue: live?.total ?? "$0.00",
      holdings,
      isEmpty,
      isLoading: !live,
      chartData: isEmpty ? [{ name: "Empty", value: 1 }] : holdings.map((h) => ({ name: h.ticker, value: h.value })),
    };
  });

  const handleAddFunds = async () => {
    const amount = parseFloat(fundAmount);
    try {
      const data = await fundAccount(sessionId, amount);
      setUser(data.user);
      setFundAmount("");
      setAddFundsOpen(false);
      toast({ title: "Funds Added", description: `$${amount.toLocaleString(undefined, { minimumFractionDigits: 2 })} has been added to your account.` });
    } catch (err) {
      toast({ title: "Error", description: err.message, variant: "destructive" });
    }
  };

  return (
    <AppLayout>
      <div className="space-y-8">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Dashboard</h1>
          <p className="text-muted-foreground">Hello, {user?.login ?? "User"}</p>
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
          <button onClick={() => setAddFundsOpen(true)} className="inline-flex items-center gap-2 rounded-lg bg-primary px-6 py-3 text-sm font-semibold text-primary-foreground">
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
              {portfolios.map((p) => <PortfolioCard key={p.id} portfolio={p} />)}
            </div>
          )}
        </div>

        {/* Add Funds Dialog */}
        <Dialog open={addFundsOpen} onOpenChange={setAddFundsOpen}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Add Funds</DialogTitle>
              <DialogDescription>Enter the amount you&apos;d like to deposit into your account.</DialogDescription>
            </DialogHeader>
            <div className="space-y-4 pt-2">
              <Input type="number" placeholder="Enter amount (USD)" value={fundAmount} onChange={(e) => setFundAmount(e.target.value)} min="0" step="0.01" />
              <div className="flex gap-2">
                {QUICK_AMOUNTS.map((amt) => (
                  <button key={amt} onClick={() => setFundAmount(String(amt))} className="rounded-lg border border-border px-3 py-1.5 text-xs font-medium text-foreground hover:bg-secondary">
                    ${amt.toLocaleString()}
                  </button>
                ))}
              </div>
              <button onClick={handleAddFunds} className="w-full rounded-lg bg-primary py-3 text-sm font-semibold text-primary-foreground">
                Confirm Deposit
              </button>
            </div>
          </DialogContent>
        </Dialog>
      </div>
    </AppLayout>
  );
}
