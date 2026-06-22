"use client";

import { useState, useEffect } from "react";
import { useSearchParams } from "next/navigation";
import { Search, ShieldCheck, ArrowRight, TrendingUp, TrendingDown, Loader2 } from "lucide-react";
import { AreaChart, Area, ResponsiveContainer, Tooltip, XAxis } from "recharts";
import { toast } from "@/hooks/use-toast";
import { useSession } from "@/context/SessionContext";
import { executeBuy, executeSell, getUser } from "@/lib/api";
import AppLayout from "@/components/AppLayout";
import { usePrices } from "@/hooks/use-prices";

function fmt(val, prefix = "$") {
    if (val == null) return "—";
    return `${prefix}${Number(val).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

function fmtVol(val) {
    if (val == null) return "—";
    if (val >= 1_000_000) return `${(val / 1_000_000).toFixed(2)}M`;
    if (val >= 1_000) return `${(val / 1_000).toFixed(1)}K`;
    return val.toString();
}

export default function Execution() {
    const searchParams = useSearchParams();
    const { user, setUser, sessionId } = useSession();

    const funds = user?.balance ?? 0;
    const portfolios = Object.values(user?.portfolios ?? {}).map((p) => ({
        id: p.name,
        name: p.name,
        holdings: Object.values(p.stocks ?? {}).map((s) => ({ ticker: s.ticker, qty: s.quantity })),
    }));

    const [side, setSide] = useState("buy");
    const [ticker, setTicker] = useState(() => searchParams.get("ticker")?.toUpperCase() ?? "");
    const [searchInput, setSearchInput] = useState(ticker);
    const [quantity, setQuantity] = useState("");
    const [selectedPortfolio, setSelectedPortfolio] = useState(portfolios[0]?.id ?? "");
    const [isProcessing, setIsProcessing] = useState(false);

    useEffect(() => {
        const trimmed = searchInput.trim().toUpperCase();
        if (!trimmed) { setTicker(""); return; }
        const timeout = setTimeout(() => setTicker(trimmed), 800);
        return () => clearTimeout(timeout);
    }, [searchInput]);

    const { prices, errors, loading: priceLoading } = usePrices(ticker ? [ticker] : []);
    const td = prices[ticker];
    const currentPrice = td?.price ?? null;
    const priceChange = td?.change ?? null;
    const isPositive = td?.positive ?? true;
    const companyName = td?.companyName ?? ticker;
    const chartData = (td?.sparkline ?? []).map((v, i) => ({ i, v }));
    const tickerHasError = Boolean(ticker && errors[ticker]);

    const isBuy = side === "buy";
    const currentPortfolio = portfolios.find((p) => p.id === selectedPortfolio);
    const sharesHeld = currentPortfolio?.holdings.find((h) => h.ticker === ticker)?.qty ?? 0;
    const quantityNum = quantity === "" ? 0 : Number(quantity);
    const estimatedTotal = currentPrice && quantityNum > 0
        ? (currentPrice * quantityNum).toLocaleString(undefined, { minimumFractionDigits: 2 })
        : null;

    const handleQuantityChange = (e) => {
        const value = e.target.value;
        if (value === "") {
            setQuantity("");
            return;
        }
        setQuantity(value.replace(/^0+/, "") || "0");
    };

    const handleExecute = async () => {
        if (isProcessing) return;
        setIsProcessing(true);

        try {
            const fn = isBuy ? executeBuy : executeSell;
            await fn(sessionId, selectedPortfolio, ticker, quantityNum);

            const { user: updatedUser } = await getUser(sessionId);
            setUser(updatedUser);

            toast({
                title: `${isBuy ? "Bought" : "Sold"} ${quantityNum} shares of ${ticker}.`,
                description: `Transaction completed successfully.`
            });
            setQuantity("");
        } catch (err) {
            const is400 = err.status === 400 || err.statusCode === 400;
            toast({
                title: err.message,
                variant: "destructive",
                ...(is400 ? {} : { description: "Please try again or contact support if the issue persists." }),
            });
        } finally {
            setIsProcessing(false);
        }
    };

    const canExecute = ticker && !tickerHasError && currentPrice && quantityNum > 0 && !isProcessing;
    const buttonDisabled = !canExecute;
    const buttonClass = isProcessing
        ? "bg-gray-400 cursor-not-allowed"
        : isBuy
            ? "bg-emerald-500 hover:bg-emerald-600"
            : "bg-red-500 hover:bg-red-600";

    return (
        <AppLayout>
            <div className="space-y-8">
                <div className="grid gap-8 lg:grid-cols-5">
                    {/* Left: Stock Info */}
                    <div className="space-y-6 lg:col-span-3">
                        <div className="flex items-center gap-4">
                            <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-lg bg-secondary text-xs font-bold text-foreground">
                                {ticker || "—"}
                            </div>
                            <div className="min-w-0">
                                <h1 className="truncate text-2xl font-bold text-foreground">
                                    {ticker
                                        ? tickerHasError ? "Ticker not found"
                                            : priceLoading ? ticker
                                                : companyName
                                        : "Enter a ticker"}
                                </h1>
                                {ticker && !tickerHasError && td?.exchange && (
                                    <p className="text-xs text-muted-foreground">{td.exchange} · {td.currency}</p>
                                )}
                                {tickerHasError && (
                                    <p className="text-xs text-red-500">Please enter a different symbol</p>
                                )}
                                {!ticker && (
                                    <p className="text-xs text-muted-foreground">Type a ticker symbol to load stock data</p>
                                )}
                            </div>
                        </div>

                        <div className="flex items-baseline gap-3">
                            <span className="text-4xl font-bold text-foreground">
                                {currentPrice != null ? `$${currentPrice.toFixed(2)}` : "—"}
                            </span>
                            {priceChange != null && (
                                <span className={`flex items-center gap-1 text-sm font-semibold ${isPositive ? "text-emerald-500" : "text-red-500"}`}>
                                    {isPositive ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
                                    {isPositive ? "+" : ""}{priceChange}% today
                                </span>
                            )}
                        </div>

                        {chartData.length > 1 && (
                            <div className="card-surface p-4">
                                <div className="mb-2 text-xs text-muted-foreground">5-Day Price</div>
                                <div className="h-32">
                                    <ResponsiveContainer width="100%" height="100%">
                                        <AreaChart data={chartData}>
                                            <defs>
                                                <linearGradient id="priceGrad" x1="0" y1="0" x2="0" y2="1">
                                                    <stop offset="5%" stopColor={isPositive ? "#10b981" : "#ef4444"} stopOpacity={0.3} />
                                                    <stop offset="95%" stopColor={isPositive ? "#10b981" : "#ef4444"} stopOpacity={0} />
                                                </linearGradient>
                                            </defs>
                                            <XAxis dataKey="i" hide />
                                            <Tooltip
                                                formatter={(v) => [`$${Number(v).toFixed(2)}`, "Price"]}
                                                contentStyle={{ backgroundColor: "hsl(0 0% 100%)", border: "1px solid hsl(214 20% 90%)", borderRadius: "8px", fontSize: "11px" }}
                                            />
                                            <Area type="monotone" dataKey="v" stroke={isPositive ? "#10b981" : "#ef4444"} strokeWidth={2} fill="url(#priceGrad)" dot={false} />
                                        </AreaChart>
                                    </ResponsiveContainer>
                                </div>
                            </div>
                        )}

                        <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
                            {[
                                { label: "Open", value: fmt(td?.open) },
                                { label: "High", value: fmt(td?.high) },
                                { label: "Low", value: fmt(td?.low) },
                                { label: "Volume", value: fmtVol(td?.volume) },
                            ].map(({ label, value }) => (
                                <div key={label} className="card-surface p-4">
                                    <div className="section-label">{label}</div>
                                    <div className="mt-1 truncate text-lg font-bold text-foreground">{value}</div>
                                </div>
                            ))}
                        </div>

                        {(td?.fiftyTwoWeekLow || td?.fiftyTwoWeekHigh) && (
                            <div className="card-surface p-4">
                                <div className="mb-3 text-xs font-semibold uppercase tracking-wider text-muted-foreground">52-Week Range</div>
                                <div className="flex items-center justify-between text-sm">
                                    <span className="text-muted-foreground">{fmt(td.fiftyTwoWeekLow)}</span>
                                    <div className="relative mx-4 h-1.5 flex-1 rounded-full bg-secondary">
                                        {currentPrice && td.fiftyTwoWeekLow && td.fiftyTwoWeekHigh && (
                                            <div
                                                className="absolute top-0 h-1.5 rounded-full bg-primary"
                                                style={{ width: `${Math.min(100, Math.max(0, ((currentPrice - td.fiftyTwoWeekLow) / (td.fiftyTwoWeekHigh - td.fiftyTwoWeekLow)) * 100))}%` }}
                                            />
                                        )}
                                    </div>
                                    <span className="text-muted-foreground">{fmt(td.fiftyTwoWeekHigh)}</span>
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Right: Order Form */}
                    <div className="space-y-4 lg:col-span-2">
                        <div className={`card-surface space-y-5 border-t-4 p-6 ${isBuy ? "border-t-emerald-500" : "border-t-red-500"}`}>
                            <div className="grid grid-cols-2 overflow-hidden rounded-lg border border-border">
                                <button
                                    onClick={() => !isProcessing && setSide("buy")}
                                    disabled={isProcessing}
                                    className={`py-2.5 text-sm font-semibold transition-colors ${isBuy ? "bg-emerald-500 text-white" : "text-muted-foreground hover:bg-secondary"} ${isProcessing ? "opacity-50 cursor-not-allowed" : ""}`}
                                >
                                    <span className="flex items-center justify-center gap-1.5"><TrendingUp size={14} /> BUY</span>
                                </button>
                                <button
                                    onClick={() => !isProcessing && setSide("sell")}
                                    disabled={isProcessing}
                                    className={`py-2.5 text-sm font-semibold transition-colors ${!isBuy ? "bg-red-500 text-white" : "text-muted-foreground hover:bg-secondary"} ${isProcessing ? "opacity-50 cursor-not-allowed" : ""}`}
                                >
                                    <span className="flex items-center justify-center gap-1.5"><TrendingDown size={14} /> SELL</span>
                                </button>
                            </div>

                            <div>
                                <label className="section-label">Ticker Symbol</label>
                                <div className="mt-2 flex items-center rounded-lg border border-border px-3 py-2.5">
                                    <input
                                        value={searchInput}
                                        onChange={(e) => setSearchInput(e.target.value.toUpperCase())}
                                        placeholder="e.g. AAPL"
                                        disabled={isProcessing}
                                        className="flex-1 bg-transparent text-sm font-medium text-foreground outline-none placeholder:text-muted-foreground disabled:opacity-50"
                                    />
                                    <Search size={16} className="text-muted-foreground" />
                                </div>
                                {tickerHasError && (
                                    <p className="mt-1 text-xs text-red-500">{errors[ticker]}</p>
                                )}
                                {ticker && currentPrice && !tickerHasError && (
                                    <p className="mt-1 text-xs text-muted-foreground">
                                        <span className="font-semibold text-foreground">{ticker}</span>
                                        <span className="ml-2">${currentPrice.toFixed(2)}</span>
                                        {priceChange != null && (
                                            <span className={`ml-1 ${isPositive ? "text-emerald-500" : "text-red-500"}`}>
                                                ({isPositive ? "+" : ""}{priceChange}%)
                                            </span>
                                        )}
                                    </p>
                                )}
                                {ticker && priceLoading && !tickerHasError && (
                                    <p className="mt-1 text-xs text-muted-foreground">Loading...</p>
                                )}
                            </div>

                            <div>
                                <label className="section-label">Select Portfolio</label>
                                <select
                                    value={selectedPortfolio}
                                    onChange={(e) => setSelectedPortfolio(e.target.value)}
                                    disabled={isProcessing}
                                    className="mt-2 w-full rounded-lg border border-border bg-transparent px-3 py-2.5 text-sm font-medium text-foreground outline-none disabled:opacity-50"
                                >
                                    {portfolios.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
                                </select>
                            </div>

                            <div>
                                <label className="section-label">Quantity (Shares)</label>
                                <input
                                    type="text"
                                    inputMode="numeric"
                                    value={quantity}
                                    onChange={handleQuantityChange}
                                    placeholder="0"
                                    disabled={isProcessing}
                                    className="mt-2 w-full rounded-lg border border-border bg-transparent px-3 py-2.5 text-2xl font-bold text-foreground outline-none placeholder:text-muted-foreground disabled:opacity-50"
                                />
                                <div className="mt-1 flex justify-between text-xs text-muted-foreground">
                                    <span>{estimatedTotal ? `Est. total: $${estimatedTotal}` : "Enter quantity"}</span>
                                    <span className="font-medium text-foreground">
                                        {isBuy ? "Buying Power" : "Shares Held"}:{" "}
                                        {isBuy ? `$${funds.toLocaleString(undefined, { minimumFractionDigits: 2 })}` : sharesHeld}
                                    </span>
                                </div>
                            </div>

                            <div className="space-y-2 rounded-lg border border-border p-4 text-sm">
                                <div className="flex justify-between">
                                    <span className="text-muted-foreground">Ticker</span>
                                    <span className="text-foreground">{ticker || "—"}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-muted-foreground">Quantity</span>
                                    <span className="text-foreground">{quantityNum} shares</span>
                                </div>
                                {currentPrice && (
                                    <div className="flex justify-between">
                                        <span className="text-muted-foreground">Market Price</span>
                                        <span className="text-foreground">${currentPrice.toFixed(2)}</span>
                                    </div>
                                )}
                                {estimatedTotal && (
                                    <div className="flex justify-between border-t border-border pt-2 font-bold">
                                        <span className="section-label">Est. Total</span>
                                        <span className="text-foreground">${estimatedTotal}</span>
                                    </div>
                                )}
                            </div>

                            <button
                                onClick={handleExecute}
                                disabled={buttonDisabled}
                                className={`flex w-full items-center justify-center gap-2 rounded-lg py-4 text-sm font-bold uppercase tracking-wider text-white transition-colors ${buttonClass} ${buttonDisabled && !isProcessing ? "opacity-50 cursor-not-allowed" : ""}`}
                            >
                                {isProcessing ? (
                                    <>
                                        <Loader2 size={16} className="animate-spin" />
                                        PROCESSING...
                                    </>
                                ) : (
                                    <>
                                        {isBuy ? "BUY" : "SELL"} <ArrowRight size={16} />
                                    </>
                                )}
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