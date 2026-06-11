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

const SECTOR_HUE = {
    "Technology": 142,
    "Financial Services": 45,
    "Healthcare": 0,
    "Energy": 35,
    "Consumer Cyclical": 25,
    "Consumer Defensive": 80,
    "Industrials": 210,
    "Basic Materials": 55,
    "Real Estate": 160,
    "Communication Services": 270,
    "Utilities": 195,
};

const generateSectorColors = (holdings) => {
    const sectorGroups = {};
    holdings.forEach((h, i) => {
        const sector = h.sector ?? "Other";
        if (!sectorGroups[sector]) sectorGroups[sector] = [];
        sectorGroups[sector].push(i);
    });

    const colors = {};
    holdings.forEach((h, i) => {
        const sector = h.sector ?? "Other";
        const hue = SECTOR_HUE[sector] ?? (
            [...(h.ticker ?? "?")].reduce((acc, c) => acc + c.charCodeAt(0), 0) % 360
        );
        const group = sectorGroups[sector];
        const posInGroup = group.indexOf(i);
        const count = group.length;
        const lightness = count === 1 ? 52 : 42 + (posInGroup / (count - 1)) * 22;
        colors[h.ticker] = `hsl(${hue}, 55%, ${lightness.toFixed(1)}%)`;
    });

    return colors;
};

const QUICK_AMOUNTS = [1000, 5000, 10000, 50000];

function PortfolioCard({ portfolio: p }) {
    const { name, totalValue, holdings, isEmpty, isLoading } = p;
    const topFour = [...holdings].sort((a, b) => b.value - a.value).slice(0, 4);
    const topHolder = topFour[0] ?? null;

    const sectorColors = generateSectorColors(holdings);
    const sortedHoldings = [...holdings].sort((a, b) => b.value - a.value);
    const chartData = isEmpty
        ? [{ name: "Empty", value: 1 }]
        : sortedHoldings.map((h) => ({ name: h.ticker, value: h.value, color: sectorColors[h.ticker] }));

    return (
        <div className="card-surface p-5 sm:p-6">
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
                            {chartData.map((entry, i) => (
                                <Cell key={i} fill={isEmpty ? "hsl(0,0%,80%)" : entry.color} />
                            ))}
                        </Pie>
                        {!isEmpty && (
                            <Tooltip
                                formatter={(val, name) => [`$${Number(val).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`, name]}
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
                {topFour.map((h) => (
                    <div key={h.ticker} className="flex items-center justify-between text-sm">
                        <div className="flex items-center gap-2">
                            <div className="h-2 w-2 rounded-full" style={{ backgroundColor: sectorColors[h.ticker] }} />
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
    const [fundAmount, setFundAmount] = useState("");

    const funds = user?.balance ?? 0;

    const portfolios = Object.values(user?.portfolios ?? {}).map((p) => {
        const live = liveData[p.name];
        const holdings = live?.holdings ?? [];
        const isEmpty = !holdings.length;
        return {
            id: p.name,
            name: p.name,
            totalValue: live?.total ?? "$0.00",
            holdings,
            isEmpty,
            isLoading: !live,
        };
    });

    const handleAddFunds = async () => {
        const amount = parseFloat(fundAmount);
        try {
            const data = await fundAccount(sessionId, amount);
            setUser(data.user);
            setFundAmount("");
            setAddFundsOpen(false);
            toast({ title: `$${amount.toLocaleString(undefined, { minimumFractionDigits: 2 })} added to your account.` });
        } catch (err) {
            toast({ title: err.message, variant: "destructive" });
        }
    };

    return (
        <AppLayout>
            <div className="space-y-6 sm:space-y-8">
                <div>
                    <h1 className="text-2xl font-bold text-foreground sm:text-3xl">Dashboard</h1>
                    <p className="text-muted-foreground">Hello, {user?.login ?? "User"}</p>
                </div>

                {/* Funds card — stacks vertically on mobile */}
                <div className="card-surface flex flex-col gap-4 p-5 sm:flex-row sm:items-center sm:justify-between sm:p-6">
                    <div className="flex items-center gap-4">
                        <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-lg bg-secondary">
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
                        className="inline-flex w-full items-center justify-center gap-2 rounded-lg bg-primary px-6 py-3 text-sm font-semibold text-primary-foreground sm:w-auto"
                    >
                        <span className="text-lg">⊕</span> Add Funds
                    </button>
                </div>

                <div>
                    <div className="section-label mb-4">Portfolio Allocations</div>
                    {portfolios.length === 0 ? (
                        <div className="card-surface flex items-center justify-center py-16 text-sm text-muted-foreground">
                            No portfolios yet. Create one on the Portfolio page.
                        </div>
                    ) : (
                        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
                            {portfolios.map((p) => <PortfolioCard key={p.id} portfolio={p} />)}
                        </div>
                    )}
                </div>

                <Dialog open={addFundsOpen} onOpenChange={setAddFundsOpen}>
                    <DialogContent className="w-[calc(100%-2rem)] max-w-lg rounded-xl sm:w-full">
                        <DialogHeader>
                            <DialogTitle>Add Funds</DialogTitle>
                            <DialogDescription>Enter the amount you&apos;d like to deposit into your account.</DialogDescription>
                        </DialogHeader>
                        <div className="space-y-4 pt-2">
                            <Input type="number" placeholder="Enter amount (USD)" value={fundAmount} onChange={(e) => setFundAmount(e.target.value)} min="0" step="0.01" />
                            <div className="grid grid-cols-2 gap-2 sm:flex sm:gap-2">
                                {QUICK_AMOUNTS.map((amt) => (
                                    <button key={amt} onClick={() => setFundAmount(String(amt))} className="rounded-lg border border-border px-3 py-2 text-xs font-medium text-foreground hover:bg-secondary sm:py-1.5">
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