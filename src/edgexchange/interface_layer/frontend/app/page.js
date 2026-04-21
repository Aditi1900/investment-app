"use client"

import Link from "next/link";
import Navbar from "@/components/Navbar";
import { ArrowRight, ArrowUpRight, BarChart3, Zap, Shield } from "lucide-react";
import { BarChart, Bar, ResponsiveContainer } from "recharts";

const chartData = [
  { v: 40 }, { v: 55 }, { v: 35 }, { v: 60 }, { v: 45 },
  { v: 70 }, { v: 50 }, { v: 80 }, { v: 65 }, { v: 90 },
];

const features = [
  {
    icon: Shield,
    title: "Portfolio Security",
    description: "Secure account architecture with encrypted transactions, session-based authentication, and real-time validation across all portfolio operations.",
    cta: "Manage Security",
  },
  {
    icon: BarChart3,
    title: "Real-Time Analytics",
    description: "Stream live market data directly into interactive charts with millisecond updates. Track portfolio performance, trends, and signals as they happen.",
    cta: "View Dashboard",
  },
  {
    icon: Zap,
    title: "Execution Engine",
    description: "Execute trades instantly with optimized backend routing and minimal latency. Designed for precision, speed, and reliability under load.",
    cta: "Start Trading",
  },
];

export default function Landing() {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      {/* Hero */}
      <section className="mx-auto max-w-screen-xl px-6 py-20">
        <div className="grid gap-12 lg:grid-cols-2 lg:items-center">
          <div>
            <div className="mb-6 inline-flex items-center gap-2 rounded-full bg-secondary px-4 py-1.5 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              <Zap size={12} className="text-accent" />
              Institutional Alpha for All
            </div>
            <h1 className="text-5xl font-extrabold leading-[1.1] tracking-tight text-foreground lg:text-6xl">
              EdgeXchange
              <br />
              {/* <span className="text-accent">Capital.</span> */}
            </h1>
            <p className="mt-6 max-w-md text-base leading-relaxed text-muted-foreground">
              EdgeXchange is a simulated investment platform that lets users build portfolios, 
              execute trades, and observe how their picks perform under realistic market volatility. 
            </p>
            <div className="mt-8 flex items-center gap-4">
              <Link
                href="/register"
                className="inline-flex items-center gap-2 rounded-lg bg-primary px-6 py-3 text-sm font-semibold text-primary-foreground transition-opacity hover:opacity-90"
              >
                Start Trading <ArrowRight size={16} />
              </Link>
              <Link
                href="/login"
                className="inline-flex items-center gap-2 rounded-lg border border-border bg-card px-6 py-3 text-sm font-semibold text-foreground transition-colors hover:bg-secondary"
              >
                View Demo
              </Link>
            </div>
          </div>

          <div className="space-y-4">
            <div className="card-surface p-6">
              <div className="section-label text-accent">Elevate your Wealth</div>
              <div className="mt-1 flex items-baseline justify-between">
                <span className="text-3xl font-bold text-foreground">$2,840,192.44</span>
                <span className="badge-positive">↗ +14.2%</span>
              </div>
              <div className="mt-4 h-24">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={chartData}>
                    <Bar dataKey="v" fill="hsl(166, 60%, 45%)" radius={[3, 3, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="card-surface p-4">
                <BarChart3 size={20} className="text-accent" />
                <div className="mt-2 text-sm font-semibold text-foreground">Realistic Trade Simulation</div>
                <div className="text-xs text-muted-foreground">Practice trading in live-style market conditions</div>
              </div>
              <div className="card-surface p-4">
                <Zap size={20} className="text-accent" />
                <div className="mt-2 text-sm font-semibold text-foreground">Portfolio Drift Insights</div>
                <div className="text-xs text-muted-foreground">Track how allocations shift when positions go unmanaged.</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="border-t border-border bg-card py-20">
        <div className="mx-auto max-w-screen-xl px-6 text-center">
          <div className="section-label">Core Advantage</div>
          <h2 className="mt-3 text-3xl font-bold text-foreground">The Architecture of Performance</h2>
          <div className="mt-12 grid gap-6 md:grid-cols-3">
            {features.map((f) => (
              <div key={f.title} className="card-surface p-6 text-left">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-secondary">
                  <f.icon size={18} className="text-foreground" />
                </div>
                <h3 className="mt-4 text-lg font-bold text-foreground">{f.title}</h3>
                <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{f.description}</p>
                <button className="mt-6 flex items-center gap-1 text-xs font-semibold uppercase tracking-wider text-foreground">
                  {f.cta} <ArrowUpRight size={12} />
                </button>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20">
        <div className="mx-auto max-w-screen-xl px-6">
          <div className="rounded-2xl bg-primary px-8 py-16 text-center">
            <h2 className="text-3xl font-bold text-primary-foreground lg:text-4xl">
              Elevate your wealth
              <br />
              to the <span className="text-accent">EdgeXchange tier.</span>
            </h2>
            <p className="mx-auto mt-4 max-w-lg text-sm text-primary-foreground/70">
              By removing the risk of real financial loss, it gives beginners a confidence-building environment to learn trading fundamentals; 
              including how portfolio drift develops over time when positions go unmanaged.
            </p>
            <div className="mt-8 flex items-center justify-center gap-4">
              <Link
                href="/register"
                className="rounded-lg bg-card px-6 py-3 text-sm font-semibold text-foreground transition-opacity hover:opacity-90"
              >
                Start Trading
              </Link>
              <button className="rounded-lg border border-primary-foreground/20 px-6 py-3 text-sm font-semibold text-primary-foreground transition-colors hover:bg-primary-foreground/10">
                Learn more
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border py-12">
        <div className="mx-auto max-w-screen-xl px-6">
          <div className="grid gap-8 md:grid-cols-4">
            <div>
              <div className="text-lg font-bold text-foreground">EdgeXchange</div>
              <p className="mt-2 text-sm text-muted-foreground">
                The premium standard for digital asset exchange and portfolio management.
              </p>
            </div>
            {[
              { title: "Platform", links: ["Terminal", "Mobile App", "API Docs", "Connectivity"] },
              { title: "Firm", links: ["Advisory", "Research", "Compliance", "Careers"] },
              { title: "Support", links: ["Help Center", "Security", "Terms", "Privacy"] },
            ].map((col) => (
              <div key={col.title}>
                <div className="section-label">{col.title}</div>
                <ul className="mt-3 space-y-2">
                  {col.links.map((l) => (
                    <li key={l}>
                      <a href="#" className="text-sm text-muted-foreground hover:text-foreground">{l}</a>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
          <div className="mt-12 flex items-center justify-between border-t border-border pt-6 text-xs text-muted-foreground">
            <span>© 2024 EdgeXchange. All rights reserved.</span>
            <div className="flex gap-6">
              <a href="#" className="hover:text-foreground">LinkedIn</a>
              <a href="#" className="hover:text-foreground">X / Twitter</a>
              <a href="#" className="hover:text-foreground">Bloomberg</a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
