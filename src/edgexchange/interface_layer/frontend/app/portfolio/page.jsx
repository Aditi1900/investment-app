"use client";

import { useState } from "react";
import {
  Plus,
  Trash2,
  Filter,
  ChevronLeft,
  ChevronRight,
  MoreVertical,
} from "lucide-react";
import { LineChart, Line, ResponsiveContainer } from "recharts";
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
    holdings: Object.values(p.stocks || {}).map((s) => ({
      ticker: s.ticker,
      qty: s.quantity,
      price: 0,
      sector: "",
      exchange: "",
      sparkline: [],
      positive: true,
      change: 0,
      name: s.ticker,
    })),
  }));

  const [activeTab, setActiveTab] = useState("All Stocks");
  const [activePortfolio, setActivePortfolio] = useState(
    portfolios[0]?.id ?? ""
  );
  const [createOpen, setCreateOpen] = useState(false);
  const [removeOpen, setRemoveOpen] = useState(false);
  const [newName, setNewName] = useState("");
  const [newDesc, setNewDesc] = useState("");

  const current =
    portfolios.find((p) => p.id === activePortfolio) ?? portfolios[0];

  const filteredHoldings =
    current?.holdings.filter((h) => {
      if (activeTab === "All Stocks") return true;
      return sectorMap[activeTab]?.some((s) =>
        h.sector.toLowerCase().includes(s.toLowerCase())
      );
    }) ?? [];

  const totalValue =
    current?.holdings.reduce((sum, h) => sum + h.price * h.qty, 0) ?? 0;

  const handleCreate = async () => {
    if (!newName.trim()) {
      toast({
        title: "Name required",
        description: "Please enter a portfolio name.",
        variant: "destructive",
      });
      return;
    }
    try {
      const data = await createPortfolio(sessionId, newName.trim());
      setUser(data.user);
      setActivePortfolio(newName.trim());
      setNewName("");
      setNewDesc("");
      setCreateOpen(false);
      toast({
        title: "Portfolio Created",
        description: `"${newName}" has been created.`,
      });
    } catch (err) {
      toast({ title: "Error", description: err.message, variant: "destructive" });
    }
  };

  const handleRemove = async () => {
    if (portfolios.length <= 1) {
      toast({
        title: "Cannot remove",
        description: "You must have at least one portfolio.",
        variant: "destructive",
      });
      setRemoveOpen(false);
      return;
    }
    // Block removal if portfolio still has holdings
    if (current && Object.keys(current.stocks).length > 0) {
      toast({
        title: "Cannot remove",
        description: "Please sell all holdings before removing this portfolio.",
        variant: "destructive",
      });
      setRemoveOpen(false);
      return;
    }
    try {
      const removed = current?.name;
      const data = await removePortfolio(sessionId, activePortfolio);
      setUser(data.user);
      setActivePortfolio(Object.keys(data.user.portfolios)[0] || "");
      setRemoveOpen(false);
      toast({
        title: "Portfolio Removed",
        description: `"${removed}" has been deleted.`,
      });
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
                  className={`rounded-lg px-3 py-1 text-xs font-medium transition-colors ${
                    p.id === activePortfolio
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
          <div className="text-3xl font-bold text-foreground">
            ${totalValue.toLocaleString(undefined, { minimumFractionDigits: 2 })}
          </div>
        </div>
      </div>

      {/* Filters + Create/Remove beside them */}
      <div className="flex items-center gap-2">
        <button className="inline-flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground">
          <Filter size={14} /> Filters
        </button>
        {tabs.map((t) => (
          <button
            key={t}
            onClick={() => setActiveTab(t)}
            className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
              activeTab === t
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

      {/* Table */}
      <div className="card-surface overflow-hidden">
        {filteredHoldings.length > 0 ? (
          <table className="w-full">
            <thead>
              <tr className="border-b border-border">
                {[
                  "Holding",
                  "Current Price",
                  "Quantity",
                  "Total Value",
                  "7D Performance",
                  "% Change",
                  "Actions",
                ].map((h) => (
                  <th
                    key={h}
                    className="px-6 py-4 text-left text-[11px] font-semibold uppercase tracking-wider text-muted-foreground"
                  >
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {filteredHoldings.map((h) => (
                <tr
                  key={h.ticker}
                  className="border-b border-border last:border-0 hover:bg-muted/30"
                >
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-secondary text-[10px] font-bold text-foreground">
                        {h.ticker}
                      </div>
                      <div>
                        <div className="text-sm font-semibold text-foreground">
                          {h.name}
                        </div>
                        <div className="text-xs text-muted-foreground">
                          {h.sector} • {h.exchange}
                        </div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm text-foreground">
                    ${h.price.toFixed(2)}
                  </td>
                  <td className="px-6 py-4 text-sm text-foreground">
                    {h.qty.toLocaleString()}
                  </td>
                  <td className="px-6 py-4 text-sm font-semibold text-foreground">
                    ${(h.price * h.qty).toLocaleString(undefined, {
                      minimumFractionDigits: 2,
                    })}
                  </td>
                  <td className="px-6 py-4">
                    <div className="h-8 w-20">
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={h.sparkline.map((v) => ({ v }))}>
                          <Line
                            type="monotone"
                            dataKey="v"
                            stroke={
                              h.positive
                                ? "hsl(152, 60%, 42%)"
                                : "hsl(0, 72%, 51%)"
                            }
                            strokeWidth={1.5}
                            dot={false}
                          />
                        </LineChart>
                      </ResponsiveContainer>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <span
                      className={
                        h.positive
                          ? "text-sm font-semibold text-success"
                          : "text-sm font-semibold text-destructive"
                      }
                    >
                      {h.positive ? "+" : ""}
                      {h.change.toFixed(2)}%
                    </span>
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
            <div className="text-sm text-muted-foreground">
              No holdings in this portfolio yet.
            </div>
            <div className="mt-1 text-xs text-muted-foreground">
              Use the Execute page to place trades.
            </div>
          </div>
        )}
      </div>

      {filteredHoldings.length > 0 && (
        <div className="flex items-center justify-between text-sm text-muted-foreground">
          <span>
            Showing {filteredHoldings.length} of{" "}
            {current?.holdings.length ?? 0} holdings
          </span>
          <div className="flex items-center gap-1">
            <button className="rounded-lg p-2 hover:bg-secondary">
              <ChevronLeft size={16} />
            </button>
            <button className="h-9 w-9 rounded-lg bg-primary text-sm font-medium text-primary-foreground">
              1
            </button>
            <button className="rounded-lg p-2 hover:bg-secondary">
              <ChevronRight size={16} />
            </button>
          </div>
        </div>
      )}

      {/* Create Portfolio Dialog */}
      <Dialog open={createOpen} onOpenChange={setCreateOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Create New Portfolio</DialogTitle>
            <DialogDescription>
              Set up a new portfolio to organize your investments.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 pt-2">
            <Input
              placeholder="Portfolio name"
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
            />
            <Input
              placeholder="Description (optional)"
              value={newDesc}
              onChange={(e) => setNewDesc(e.target.value)}
            />
            <button
              onClick={handleCreate}
              className="w-full rounded-lg bg-primary py-3 text-sm font-semibold text-primary-foreground"
            >
              Create Portfolio
            </button>
          </div>
        </DialogContent>
      </Dialog>

      {/* Remove Portfolio Dialog */}
      <Dialog open={removeOpen} onOpenChange={setRemoveOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Remove Portfolio</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete &quot;{current?.name}&quot;? This
              action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <div className="flex gap-3 pt-2">
            <button
              onClick={() => setRemoveOpen(false)}
              className="flex-1 rounded-lg border border-border py-3 text-sm font-semibold text-foreground"
            >
              Cancel
            </button>
            <button
              onClick={handleRemove}
              className="flex-1 rounded-lg bg-destructive py-3 text-sm font-semibold text-destructive-foreground"
            >
              Delete Portfolio
            </button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
    </AppLayout>
  );
}