"use client";

import { useState, memo } from "react";
import { Plus, Trash2, Filter, ChevronLeft, ChevronRight, MoreVertical } from "lucide-react";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { toast } from "@/hooks/use-toast";
import { useSession } from "@/context/SessionContext";
import { usePortfolio } from "@/context/PortfolioContext";
import { createPortfolio, removePortfolio } from "@/lib/api";
import AppLayout from "@/components/AppLayout";
import { useAnimatedNumber } from "@/hooks/use-animated-number"

const parseNum = (v) => parseFloat(String(v).replace(/[^0-9.]/g, "")) || 0;

const AnimatedValue = memo(function AnimatedValue({ value, prefix = "$", decimals = 2, fallback = "—" }) {
    const animated = useAnimatedNumber(value);
    if (animated === null) return <span>{fallback}</span>;
    return <span>{prefix}{animated.toLocaleString(undefined, { minimumFractionDigits: decimals, maximumFractionDigits: decimals })}</span>;
});

const AnimatedTotal = memo(function AnimatedTotal({ rawTotal, hasHoldings }) {
    const num = rawTotal ? parseNum(rawTotal) : null;
    const animated = useAnimatedNumber(hasHoldings ? num : 0);
    if (animated === null) return <span>Loading...</span>;
    return <span>${animated.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>;
});

export default function Portfolio() {
    const { user, setUser, sessionId } = useSession();
    const { liveData } = usePortfolio();

    const portfolios = Object.values(user?.portfolios ?? {}).map((p) => ({ id: p.name, name: p.name, stocks: p.stocks ?? {} }));

    const [activeTab, setActiveTab] = useState("All Stocks");
    const [activePortfolio, setActivePortfolio] = useState(portfolios[0]?.id ?? "");
    const [createOpen, setCreateOpen] = useState(false);
    const [removeOpen, setRemoveOpen] = useState(false);
    const [newName, setNewName] = useState("");

    const current = portfolios.find((p) => p.id === activePortfolio) ?? portfolios[0];
    const live = liveData[current?.name];

    const holdings = (live?.holdings ?? []).map((h) => ({
        ticker: h.ticker ?? "", qty: h.quantity ?? 0, price: h.price ?? 0,
        value: h.value ?? 0,
        sector: typeof h.sector === "string" && h.sector !== "Unknown" ? h.sector : "Other",
        name: h.ticker ?? "",
    }));

    const sectors = [...new Set(holdings.map((h) => h.sector).filter((s) => s && s !== "Other"))];
    const presentSectors = ["All Stocks", ...sectors, ...(holdings.some((h) => h.sector === "Other") ? ["Other"] : [])];
    const resolvedTab = presentSectors.includes(activeTab) ? activeTab : "All Stocks";
    const filteredHoldings = resolvedTab === "All Stocks" ? holdings : holdings.filter((h) => h.sector === resolvedTab);
    const rawTotal = live?.total ? `$${String(live.total).replace(/^\$+/, "")}` : holdings.length === 0 ? "$0.00" : null;

    const handleCreate = async () => {
        try {
            const data = await createPortfolio(sessionId, newName);
            setUser(data.user);
            setActivePortfolio(newName.trim());
            setNewName("");
            setCreateOpen(false);
            toast({ title: `Portfolio "${newName}" created.` });
        } catch (err) { toast({ title: err.message, variant: "destructive" }); }
    };

    const handleRemove = async () => {
        try {
            const removed = current?.name;
            const data = await removePortfolio(sessionId, activePortfolio);
            setUser(data.user);
            setActivePortfolio(Object.keys(data.user.portfolios)[0] ?? "");
            setRemoveOpen(false);
            toast({ title: `Portfolio "${removed}" deleted.` });
        } catch (err) {
            toast({ title: err.message, variant: "destructive" });
            setRemoveOpen(false);
        }
    };

    return (
        <AppLayout>
            <div className="space-y-8">
                <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
                    <div>
                        <div className="section-label">Asset Allocation</div>
                        <h1 className="mt-1 text-3xl font-bold text-foreground">{current?.name ?? "Portfolio"}</h1>
                        {portfolios.length > 1 && (
                            <div className="mt-2 flex flex-wrap gap-2">
                                {portfolios.map((p) => (
                                    <button key={p.id} onClick={() => setActivePortfolio(p.id)}
                                        className={`rounded-lg px-3 py-1 text-xs font-medium transition-colors ${p.id === activePortfolio ? "bg-primary text-primary-foreground" : "border border-border text-muted-foreground hover:text-foreground"}`}>
                                        {p.name}
                                    </button>
                                ))}
                            </div>
                        )}
                    </div>
                    <div className="sm:text-right">
                        <div className="section-label">Total Valuation</div>
                        <div className="text-3xl font-bold text-foreground">
                            <AnimatedTotal key={current?.name} rawTotal={rawTotal} hasHoldings={holdings.length > 0} />
                        </div>
                    </div>
                </div>

                <div className="flex flex-wrap items-center gap-2">
                    <button className="inline-flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground">
                        <Filter size={14} /> Filters
                    </button>
                    {presentSectors.map((t) => (
                        <button key={t} onClick={() => setActiveTab(t)}
                            className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors ${resolvedTab === t ? "bg-card border border-border text-foreground" : "text-muted-foreground hover:text-foreground"}`}>
                            {t}
                        </button>
                    ))}
                    <div className="ml-auto flex items-center gap-2">
                        <button onClick={() => setCreateOpen(true)} className="inline-flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground">
                            <Plus size={14} /> New Portfolio
                        </button>
                        <button onClick={() => setRemoveOpen(true)} className="inline-flex items-center gap-2 rounded-lg border border-border bg-card px-4 py-2 text-sm font-medium text-foreground">
                            <Trash2 size={14} /> Remove
                        </button>
                    </div>
                </div>

                <div className="card-surface overflow-x-auto">
                    {filteredHoldings.length > 0 ? (
                        <table className="w-full min-w-[640px]">
                            <thead>
                                <tr className="border-b border-border">
                                    {["Holding", "Sector", "Current Price", "Quantity", "Total Value", "Actions"].map((h) => (
                                        <th key={h} className="px-6 py-4 text-left text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">{h}</th>
                                    ))}
                                </tr>
                            </thead>
                            <tbody>
                                {filteredHoldings.map((h) => (
                                    <tr key={h.ticker} className="border-b border-border last:border-0 hover:bg-muted/30">
                                        <td className="px-6 py-4">
                                            <div className="flex items-center gap-3">
                                                <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-secondary text-[10px] font-bold text-foreground">{h.ticker}</div>
                                                <div className="text-sm font-semibold text-foreground">{h.name}</div>
                                            </div>
                                        </td>
                                        <td className="px-6 py-4">
                                            {h.sector !== "Other" && <span className="rounded-md bg-secondary px-2 py-1 text-xs font-medium text-muted-foreground">{h.sector}</span>}
                                        </td>
                                        <td className="px-6 py-4 text-sm text-foreground">
                                            {h.price > 0 ? <AnimatedValue key={`${current?.name}-${h.ticker}-price`} value={h.price} /> : "—"}
                                        </td>
                                        <td className="px-6 py-4 text-sm text-foreground">{h.qty.toLocaleString()}</td>
                                        <td className="px-6 py-4 text-sm font-semibold text-foreground">
                                            {h.value > 0 ? <AnimatedValue key={`${current?.name}-${h.ticker}-value`} value={h.value} /> : "—"}
                                        </td>
                                        <td className="px-6 py-4">
                                            <button className="text-muted-foreground hover:text-foreground"><MoreVertical size={16} /></button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    ) : (
                        <div className="flex flex-col items-center justify-center py-16 text-center">
                            <div className="text-sm text-muted-foreground">No holdings in this portfolio yet.</div>
                            <div className="mt-1 text-xs text-muted-foreground">Use the Execute page to place trades.</div>
                        </div>
                    )}
                </div>

                {filteredHoldings.length > 0 && (
                    <div className="flex items-center justify-between text-sm text-muted-foreground">
                        <span>Showing {filteredHoldings.length} of {holdings.length} holdings</span>
                        <div className="flex items-center gap-1">
                            <button className="rounded-lg p-2 hover:bg-secondary"><ChevronLeft size={16} /></button>
                            <button className="h-9 w-9 rounded-lg bg-primary text-sm font-medium text-primary-foreground">1</button>
                            <button className="rounded-lg p-2 hover:bg-secondary"><ChevronRight size={16} /></button>
                        </div>
                    </div>
                )}

                <Dialog open={createOpen} onOpenChange={setCreateOpen}>
                    <DialogContent>
                        <DialogHeader>
                            <DialogTitle>Create New Portfolio</DialogTitle>
                            <DialogDescription>Set up a new portfolio to organize your investments.</DialogDescription>
                        </DialogHeader>
                        <div className="space-y-4 pt-2">
                            <Input placeholder="Portfolio name" value={newName} onChange={(e) => setNewName(e.target.value)} />
                            <button onClick={handleCreate} className="w-full rounded-lg bg-primary py-3 text-sm font-semibold text-primary-foreground">Create Portfolio</button>
                        </div>
                    </DialogContent>
                </Dialog>

                <Dialog open={removeOpen} onOpenChange={setRemoveOpen}>
                    <DialogContent>
                        <DialogHeader>
                            <DialogTitle>Remove Portfolio</DialogTitle>
                            <DialogDescription>Are you sure you want to delete &quot;{current?.name}&quot;? This action cannot be undone.</DialogDescription>
                        </DialogHeader>
                        <div className="flex gap-3 pt-2">
                            <button onClick={() => setRemoveOpen(false)} className="flex-1 rounded-lg border border-border py-3 text-sm font-semibold text-foreground">Cancel</button>
                            <button onClick={handleRemove} className="flex-1 rounded-lg bg-destructive py-3 text-sm font-semibold text-destructive-foreground">Delete Portfolio</button>
                        </div>
                    </DialogContent>
                </Dialog>
            </div>
        </AppLayout>
    );
}