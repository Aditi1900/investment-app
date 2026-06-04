"use client";

import { useState, useEffect } from "react";
import {
    Plus,
    Trash2,
    Filter,
    ChevronLeft,
    ChevronRight,
    MoreVertical,
} from "lucide-react";
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
import { createPortfolio, removePortfolio } from "@/lib/api";
import AppLayout from "@/components/AppLayout";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const tabs = ["All Stocks", "Tech", "Finance", "ETF"];
const sectorMap = {
    "All Stocks": [],
    Tech: ["Technology", "Semiconductors"],
    Finance: ["Finance", "Banking"],
    ETF: ["ETF"],
};

export default function Portfolio() {
    const { user, setUser, sessionId } = useSession();

    const portfolios = Object.values(user?.portfolios || {}).map((p) => ({
        id: p.name,
        name: p.name,
        stocks: p.stocks || {},
    }));

    const [activeTab, setActiveTab] = useState("All Stocks");
    const [activePortfolio, setActivePortfolio] = useState(portfolios[0]?.id ?? "");
    const [createOpen, setCreateOpen] = useState(false);
    const [removeOpen, setRemoveOpen] = useState(false);
    const [newName, setNewName] = useState("");
    const [newDesc, setNewDesc] = useState("");
    const [liveData, setLiveData] = useState({});

    const current = portfolios.find((p) => p.id === activePortfolio) ?? portfolios[0];

    useEffect(() => {
        if (!sessionId || portfolios.length === 0) return;

        const controllers = portfolios.map((p) => {
            const controller = new AbortController();
            const url = `${BASE_URL}/live_data?session_id=${sessionId}&portfolio_name=${encodeURIComponent(p.name)}`;

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
                                    setLiveData((prev) => ({ ...prev, [p.name]: data }));
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
    }, [sessionId, portfolios.map((p) => p.name).join(",")]);

    const live = liveData[current?.name];
    const enrichedHoldings = (live?.holdings ?? []).map((h) => ({
        ticker: h.ticker ?? "",
        qty: h.quantity ?? 0,
        price: h.price ?? 0,
        value: h.value ?? 0,
        sector: "",
        exchange: "",
        name: h.ticker ?? "",
    }));

    const totalValue = live?.total ?? (enrichedHoldings.length === 0 ? "$0.00" : "Loading...");

    const filteredHoldings = enrichedHoldings.filter((h) => {
        if (activeTab === "All Stocks") return true;
        return sectorMap[activeTab]?.some((s) =>
            h.sector.toLowerCase().includes(s.toLowerCase())
        );
    });

    const handleCreate = async () => {
        if (!newName.trim()) {
            toast({ title: "Name required", description: "Please enter a portfolio name.", variant: "destructive" });
            return;
        }
        try {
            const data = await createPortfolio(sessionId, newName.trim());
            setUser(data.user);
            setActivePortfolio(newName.trim());
            setNewName("");
            setNewDesc("");
            setCreateOpen(false);
            toast({ title: "Portfolio Created", description: `"${newName}" has been created.` });
        } catch (err) {
            toast({ title: "Error", description: err.message, variant: "destructive" });
        }
    };

    const handleRemove = async () => {
        if (portfolios.length <= 1) {
            toast({ title: "Cannot remove", description: "You must have at least one portfolio.", variant: "destructive" });
            setRemoveOpen(false);
            return;
        }
        if (current && Object.keys(current.stocks).length > 0) {
            toast({ title: "Cannot remove", description: "Please sell all holdings before removing this portfolio.", variant: "destructive" });
            setRemoveOpen(false);
            return;
        }
        try {
            const removed = current?.name;
            const data = await removePortfolio(sessionId, activePortfolio);
            setUser(data.user);
            setActivePortfolio(Object.keys(data.user.portfolios)[0] || "");
            setRemoveOpen(false);
            toast({ title: "Portfolio Removed", description: `"${removed}" has been deleted.` });
        } catch (err) {
            toast({ title: "Error", description: err.message, variant: "destructive" });
        }
    };

    return (
        <AppLayout>
            <div className="space-y-8">
                <div className="flex items-start justify-between">
                    <div>
                        <div className="section-label">Asset Allocation</div>
                        <h1 className="mt-1 text-3xl font-bold text-foreground">
                            {current?.name ?? "Portfolio"}
                        </h1>
                        {portfolios.length > 1 && (
                            <div className="mt-2 flex gap-2">
                                {portfolios.map((p) => (
                                    <button
                                        key={p.id}
                                        onClick={() => setActivePortfolio(p.id)}
                                        className={`rounded-lg px-3 py-1 text-xs font-medium transition-colors ${p.id === activePortfolio
                                                ? "bg-primary text-primary-foreground"
                                                : "border border-border text-muted-foreground hover:text-foreground"
                                            }`}
                                    >
                                        {p.name}
                                    </button>
                                ))}
                            </div>
                        )}
                    </div>
                    <div className="text-right">
                        <div className="section-label">Total Valuation</div>
                        <div className="text-3xl font-bold text-foreground">{totalValue}</div>
                    </div>
                </div>

                <div className="flex items-center gap-2">
                    <button className="inline-flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground">
                        <Filter size={14} /> Filters
                    </button>
                    {tabs.map((t) => (
                        <button
                            key={t}
                            onClick={() => setActiveTab(t)}
                            className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors ${activeTab === t
                                    ? "bg-card border border-border text-foreground"
                                    : "text-muted-foreground hover:text-foreground"
                                }`}
                        >
                            {t}
                        </button>
                    ))}
                    <div className="ml-auto flex items-center gap-2">
                        <button
                            onClick={() => setCreateOpen(true)}
                            className="inline-flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground"
                        >
                            <Plus size={14} /> New Portfolio
                        </button>
                        <button
                            onClick={() => setRemoveOpen(true)}
                            className="inline-flex items-center gap-2 rounded-lg border border-border bg-card px-4 py-2 text-sm font-medium text-foreground"
                        >
                            <Trash2 size={14} /> Remove
                        </button>
                    </div>
                </div>

                <div className="card-surface overflow-hidden">
                    {filteredHoldings.length > 0 ? (
                        <table className="w-full">
                            <thead>
                                <tr className="border-b border-border">
                                    {["Holding", "Current Price", "Quantity", "Total Value", "Actions"].map((h) => (
                                        <th key={h} className="px-6 py-4 text-left text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
                                            {h}
                                        </th>
                                    ))}
                                </tr>
                            </thead>
                            <tbody>
                                {filteredHoldings.map((h) => (
                                    <tr key={h.ticker} className="border-b border-border last:border-0 hover:bg-muted/30">
                                        <td className="px-6 py-4">
                                            <div className="flex items-center gap-3">
                                                <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-secondary text-[10px] font-bold text-foreground">
                                                    {h.ticker}
                                                </div>
                                                <div>
                                                    <div className="text-sm font-semibold text-foreground">{h.name}</div>
                                                </div>
                                            </div>
                                        </td>
                                        <td className="px-6 py-4 text-sm text-foreground">
                                            {h.price != null && h.price > 0 ? `$${h.price.toFixed(2)}` : "—"}
                                        </td>
                                        <td className="px-6 py-4 text-sm text-foreground">{h.qty != null ? h.qty.toLocaleString() : "—"}</td>
                                        <td className="px-6 py-4 text-sm font-semibold text-foreground">
                                            {h.value != null && h.value > 0
                                                ? `$${h.value.toLocaleString(undefined, { minimumFractionDigits: 2 })}`
                                                : "—"}
                                        </td>
                                        <td className="px-6 py-4">
                                            <button className="text-muted-foreground hover:text-foreground">
                                                <MoreVertical size={16} />
                                            </button>
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
                        <span>Showing {filteredHoldings.length} of {enrichedHoldings.length} holdings</span>
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
                            <Input placeholder="Description (optional)" value={newDesc} onChange={(e) => setNewDesc(e.target.value)} />
                            <button onClick={handleCreate} className="w-full rounded-lg bg-primary py-3 text-sm font-semibold text-primary-foreground">
                                Create Portfolio
                            </button>
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