"use client";

import { useState } from "react";
import { useSearchParams } from "next/navigation";
import {
    Search,
    ShieldCheck,
    ArrowRight,
    TrendingUp,
    TrendingDown,
} from "lucide-react";
import { toast } from "@/hooks/use-toast";
import { useSession } from "@/context/SessionContext";
import { executeBuy, executeSell } from "@/lib/api";
import AppLayout from "@/components/AppLayout";
import { usePrices } from "@/hooks/use-prices";

export default function Execution() {
    const searchParams = useSearchParams();
    const { user, setUser, sessionId } = useSession();

    const funds = user?.balance || 0;
    const portfolios = Object.values(user?.portfolios || {}).map((p) => ({
        id: p.name,
        name: p.name,
        holdings: Object.values(p.stocks || {}).map((s) => ({
            ticker: s.ticker,
            qty: s.quantity,
        })),
    }));

    const [side, setSide] = useState("buy");
    const [ticker, setTicker] = useState(() =>
        searchParams.get("ticker")?.toUpperCase() ?? ""
    );
    const [searchInput, setSearchInput] = useState(ticker);
    const [quantity, setQuantity] = useState(0);
    const [selectedPortfolio, setSelectedPortfolio] = useState(
        portfolios[0]?.id ?? ""
    );

    const { prices } = usePrices(ticker ? [ticker] : []);
    const tickerData = prices[ticker];
    const currentPrice = tickerData?.price ?? null;
    const priceChange = tickerData?.change ?? null;
    const isPositive = tickerData?.positive ?? true;

    const isBuy = side === "buy";
    const currentPortfolio = portfolios.find((p) => p.id === selectedPortfolio);
    const sharesHeld =
        currentPortfolio?.holdings.find((h) => h.ticker === ticker)?.qty ?? 0;

    const estimatedTotal =
        currentPrice && quantity > 0
            ? (currentPrice * quantity).toLocaleString(undefined, { minimumFractionDigits: 2 })
            : null;

    const handleSearchKeyDown = (e) => {
        if (e.key === "Enter" && searchInput.trim()) {
            setTicker(searchInput.trim().toUpperCase());
        }
    };

    const handleQuantityChange = (e) => {
        const val = Number(e.target.value);
        setQuantity(val < 0 ? 0 : val);
    };

    const handleExecute = async () => {
        if (!ticker.trim()) {
            toast({ title: "No ticker entered", description: "Please enter a stock ticker.", variant: "destructive" });
            return;
        }
        if (quantity <= 0) {
            toast({ title: "Invalid quantity", description: "Please enter a valid number of shares.", variant: "destructive" });
            return;
        }
        if (!selectedPortfolio) {
            toast({ title: "No portfolio selected", description: "Please select a portfolio.", variant: "destructive" });
            return;
        }
        if (isBuy && funds <= 0) {
            toast({ title: "No funds available", description: "Please add funds to your account first.", variant: "destructive" });
            return;
        }
        try {
            const fn = isBuy ? executeBuy : executeSell;
            const data = await fn(sessionId, selectedPortfolio, ticker, quantity);
            setUser((prev) => ({
                ...prev,
                portfolios: {
                    ...prev.portfolios,
                    [selectedPortfolio]: data.portfolio,
                },
            }));
            const userRes = await fetch(
                `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/user?session_id=${sessionId}`
            );
            if (userRes.ok) {
                const userData = await userRes.json();
                setUser(userData.user);
            }
            toast({
                title: `${isBuy ? "Buy" : "Sell"} Order Placed`,
                description: `${isBuy ? "Bought" : "Sold"} ${quantity} shares of ${ticker}.`,
            });
            setQuantity(0);
        } catch (err) {
            toast({ title: "Trade failed", description: err.message, variant: "destructive" });
        }
    };

    return (
        <AppLayout>
            <div className="space-y-8">
                <div className="grid gap-8 lg:grid-cols-5">
                    <div className="space-y-6 lg:col-span-3">
                        <div className="flex items-center gap-4">
                            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-secondary text-xs font-bold text-foreground">
                                {ticker || "—"}
                            </div>
                            <div>
                                <h1 className="text-2xl font-bold text-foreground">
                                    {ticker || "Enter a ticker"}
                                </h1>
                                <p className="text-xs text-muted-foreground">Press Enter to set ticker</p>
                            </div>
                        </div>

                        <div className="flex items-baseline gap-3">
                            <span className="text-4xl font-bold text-foreground">
                                {currentPrice != null ? `$${currentPrice.toFixed(2)}` : "—"}
                            </span>
                            {priceChange != null && (
                                <span className={`text-sm font-semibold ${isPositive ? "text-emerald-500" : "text-red-500"}`}>
                                    {isPositive ? "+" : ""}{priceChange}%
                                </span>
                            )}
                        </div>

                        <div className="grid grid-cols-4 gap-4">
                            {["Open", "High", "Low", "Volume"].map((label) => (
                                <div key={label} className="card-surface p-4">
                                    <div className="section-label">{label}</div>
                                    <div className="mt-1 text-lg font-bold text-foreground">—</div>
                                </div>
                            ))}
                        </div>
                    </div>

                    <div className="space-y-4 lg:col-span-2">
                        <div className={`card-surface space-y-5 border-t-4 p-6 ${isBuy ? "border-t-emerald-500" : "border-t-red-500"}`}>
                            <div className="grid grid-cols-2 overflow-hidden rounded-lg border border-border">
                                <button
                                    onClick={() => setSide("buy")}
                                    className={`py-2.5 text-sm font-semibold transition-colors ${isBuy ? "bg-emerald-500 text-white" : "text-muted-foreground hover:bg-secondary"}`}
                                >
                                    <span className="flex items-center justify-center gap-1.5">
                                        <TrendingUp size={14} /> BUY
                                    </span>
                                </button>
                                <button
                                    onClick={() => setSide("sell")}
                                    className={`py-2.5 text-sm font-semibold transition-colors ${!isBuy ? "bg-red-500 text-white" : "text-muted-foreground hover:bg-secondary"}`}
                                >
                                    <span className="flex items-center justify-center gap-1.5">
                                        <TrendingDown size={14} /> SELL
                                    </span>
                                </button>
                            </div>

                            <div>
                                <label className="section-label">Ticker Symbol</label>
                                <div className="mt-2 flex items-center rounded-lg border border-border px-3 py-2.5">
                                    <input
                                        value={searchInput}
                                        onChange={(e) => setSearchInput(e.target.value.toUpperCase())}
                                        onKeyDown={handleSearchKeyDown}
                                        placeholder="Enter stock ticker e.g. AAPL"
                                        className="flex-1 bg-transparent text-sm font-medium text-foreground outline-none placeholder:text-muted-foreground"
                                    />
                                    <Search size={16} className="text-muted-foreground" />
                                </div>
                                {ticker && (
                                    <p className="mt-1 text-xs text-muted-foreground">
                                        Active ticker: <span className="font-semibold text-foreground">{ticker}</span>
                                        {currentPrice && <span className="ml-2 text-foreground">${currentPrice.toFixed(2)}</span>}
                                    </p>
                                )}
                            </div>

                            <div>
                                <label className="section-label">Select Portfolio</label>
                                <select
                                    value={selectedPortfolio}
                                    onChange={(e) => setSelectedPortfolio(e.target.value)}
                                    className="mt-2 w-full rounded-lg border border-border bg-transparent px-3 py-2.5 text-sm font-medium text-foreground outline-none"
                                >
                                    {portfolios.map((p) => (
                                        <option key={p.id} value={p.id}>{p.name}</option>
                                    ))}
                                </select>
                            </div>

                            <div>
                                <label className="section-label">Quantity (Shares)</label>
                                <input
                                    type="number"
                                    min={0}
                                    value={quantity}
                                    onChange={handleQuantityChange}
                                    className="mt-2 w-full rounded-lg border border-border bg-transparent px-3 py-2.5 text-2xl font-bold text-foreground outline-none"
                                />
                                <div className="mt-1 flex justify-between text-xs text-muted-foreground">
                                    <span>
                                        {estimatedTotal ? `Est. total: $${estimatedTotal}` : "Price confirmed at execution"}
                                    </span>
                                    <span className="font-medium text-foreground">
                                        {isBuy ? "Buying Power" : "Shares Held"}:{" "}
                                        {isBuy
                                            ? `$${funds.toLocaleString(undefined, { minimumFractionDigits: 2 })}`
                                            : sharesHeld}
                                    </span>
                                </div>
                            </div>

                            <div className="space-y-2 rounded-lg border border-border p-4 text-sm">
                                <div className="flex justify-between">
                                    <span className="text-muted-foreground">Quantity</span>
                                    <span className="text-foreground">{quantity} shares</span>
                                </div>
                                {estimatedTotal && (
                                    <div className="flex justify-between">
                                        <span className="text-muted-foreground">Est. Total</span>
                                        <span className="text-foreground">${estimatedTotal}</span>
                                    </div>
                                )}
                                <div className="flex justify-between border-t border-border pt-2 font-bold">
                                    <span className="section-label">Ticker</span>
                                    <span className="text-foreground">{ticker || "—"}</span>
                                </div>
                            </div>

                            <button
                                onClick={handleExecute}
                                className={`flex w-full items-center justify-center gap-2 rounded-lg py-4 text-sm font-bold uppercase tracking-wider text-white transition-colors ${isBuy ? "bg-emerald-500 hover:bg-emerald-600" : "bg-red-500 hover:bg-red-600"
                                    }`}
                            >
                                {isBuy ? "BUY" : "SELL"} <ArrowRight size={16} />
                            </button>
                            <p className="text-center text-[10px] text-muted-foreground">
                                By clicking {isBuy ? "BUY" : "SELL"}, you agree to EdgeXchange&apos;s Terms of Service and Risk Disclosure statement.
                            </p>
                        </div>

                        <div className="card-surface flex items-start gap-3 p-4">
                            <ShieldCheck size={20} className="mt-0.5 text-accent" />
                            <div>
                                <div className="text-sm font-bold text-foreground">Insured Execution</div>
                                <p className="text-xs text-muted-foreground">
                                    Your trades are protected by SIPC insurance up to $500,000 for securities and cash assets.
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </AppLayout>
    );
}