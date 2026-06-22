"use client";

import Link from "next/link";
import Navbar from "@/components/Navbar";
import { ArrowRight, ArrowUpRight, BarChart3, Zap, Shield } from "lucide-react";
import { BarChart, Bar, ResponsiveContainer } from "recharts";

const heroChartData = [
    { value: 40 },
    { value: 55 },
    { value: 35 },
    { value: 60 },
    { value: 45 },
    { value: 70 },
    { value: 50 },
    { value: 80 },
    { value: 65 },
    { value: 90 },
];

const FEATURES = [
    {
        icon: Shield,
        title: "Portfolio Security",
        description:
            "Secure account architecture with encrypted transactions, session-based authentication, and real-time validation across all portfolio operations.",
        cta: "Manage Security",
        href: "/portfolio",
    },
    {
        icon: BarChart3,
        title: "Real-Time Analytics",
        description:
            "Stream live market data directly into interactive charts with millisecond updates. Track portfolio performance, trends, and signals as they happen.",
        cta: "View Dashboard",
        href: "/dashboard",
    },
    {
        icon: Zap,
        title: "Execution Engine",
        description:
            "Execute trades instantly with optimized backend routing and minimal latency. Designed for precision, speed, and reliability under load.",
        cta: "Start Trading",
        href: "/execute",
    },
];

const FOOTER_COLUMNS = [
    {
        title: "Platform",
        links: [
            { label: "Terminal", href: "/execute" },
            { label: "Mobile App", href: "#" },
            { label: "API Docs", href: "#" },
            { label: "Connectivity", href: "#" },
        ],
    },
    {
        title: "Firm",
        links: [
            { label: "Advisory", href: "#" },
            { label: "Research", href: "#" },
            { label: "Compliance", href: "#" },
            { label: "Careers", href: "#" },
        ],
    },
    {
        title: "Support",
        links: [
            { label: "Help Center", href: "#" },
            { label: "Security", href: "#" },
            { label: "Terms", href: "#" },
            { label: "Privacy", href: "#" },
        ],
    },
];

export default function Landing() {
    return (
        <div className="min-h-screen bg-background">
            <Navbar />

            {/* ── Hero ─────────────────────────────────────────────────────── */}
            <section className="mx-auto max-w-screen-xl px-4 py-12 sm:px-6 sm:py-20">
                <div className="grid gap-10 lg:grid-cols-2 lg:items-center">

                    {/* Left: headline + CTAs */}
                    <div>
                        <div className="mb-6 inline-flex items-center gap-2 rounded-full bg-secondary px-4 py-1.5 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                            <Zap size={12} className="text-accent" />
                            Institutional Alpha for All
                        </div>

                        <h1 className="text-4xl font-extrabold leading-[1.1] tracking-tight text-foreground sm:text-5xl lg:text-6xl">
                            EdgeXchange
                        </h1>

                        <p className="mt-6 max-w-md text-base leading-relaxed text-muted-foreground">
                            EdgeXchange is a simulated investment platform that lets users build portfolios,
                            execute trades, and observe how their picks perform under realistic market volatility.
                        </p>

                        <div className="mt-8 flex flex-wrap items-center gap-3">
                            <Link
                                href="/register"
                                className="inline-flex items-center gap-2 rounded-lg bg-primary px-6 py-3 text-sm font-semibold text-primary-foreground transition-opacity hover:opacity-90"
                            >
                                Start Trading <ArrowRight size={16} />
                            </Link>

                        </div>
                    </div>

                    {/* Right: preview card + feature chips */}
                    <div className="space-y-4">
                        <Link href="/dashboard" className="block">
                            <div className="card-surface p-6 transition-colors hover:bg-secondary/50">
                                <div className="section-label text-accent">Elevate your Wealth</div>
                                <div className="mt-1 flex items-baseline justify-between">
                                    <span className="text-2xl font-bold text-foreground sm:text-3xl">$2,840,192.44</span>
                                    <span className="badge-positive">↗ +14.2%</span>
                                </div>
                                <div className="mt-4 h-24">
                                    <ResponsiveContainer width="100%" height="100%">
                                        <BarChart data={heroChartData}>
                                            <Bar dataKey="value" fill="hsl(166, 60%, 45%)" radius={[3, 3, 0, 0]} />
                                        </BarChart>
                                    </ResponsiveContainer>
                                </div>
                            </div>
                        </Link>

                        <div className="grid grid-cols-2 gap-4">
                            <Link href="/execute" className="block">
                                <div className="card-surface p-4 transition-colors hover:bg-secondary/50">
                                    <BarChart3 size={20} className="text-accent" />
                                    <div className="mt-2 text-sm font-semibold text-foreground">Realistic Trade Simulation</div>
                                    <div className="text-xs text-muted-foreground">Practice trading in live-style market conditions</div>
                                </div>
                            </Link>
                            <Link href="/portfolio" className="block">
                                <div className="card-surface p-4 transition-colors hover:bg-secondary/50">
                                    <Zap size={20} className="text-accent" />
                                    <div className="mt-2 text-sm font-semibold text-foreground">Portfolio Drift Insights</div>
                                    <div className="text-xs text-muted-foreground">Track how allocations shift when positions go unmanaged.</div>
                                </div>
                            </Link>
                        </div>
                    </div>
                </div>
            </section>

            {/* ── Features ──────────────────────────────────────────────────── */}
            <section id="features" className="border-t border-border bg-card py-16 sm:py-20">
                <div className="mx-auto max-w-screen-xl px-4 text-center sm:px-6">
                    <div className="section-label">Core Advantage</div>
                    <h2 className="mt-3 text-2xl font-bold text-foreground sm:text-3xl">
                        The Architecture of Performance
                    </h2>

                    <div className="mt-10 grid gap-6 sm:grid-cols-2 md:grid-cols-3">
                        {FEATURES.map((feature) => {
                            const Icon = feature.icon;
                            return (
                                <div key={feature.title} className="card-surface p-6 text-left">
                                    <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-secondary">
                                        <Icon size={18} className="text-foreground" />
                                    </div>
                                    <h3 className="mt-4 text-lg font-bold text-foreground">{feature.title}</h3>
                                    <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{feature.description}</p>
                                    <Link
                                        href={feature.href}
                                        className="mt-6 flex items-center gap-1 text-xs font-semibold uppercase tracking-wider text-foreground hover:text-accent transition-colors"
                                    >
                                        {feature.cta} <ArrowUpRight size={12} />
                                    </Link>
                                </div>
                            );
                        })}
                    </div>
                </div>
            </section>

            {/* ── CTA Banner ────────────────────────────────────────────────── */}
            <section className="py-16 sm:py-20">
                <div className="mx-auto max-w-screen-xl px-4 sm:px-6">
                    <div className="rounded-2xl bg-primary px-6 py-14 text-center sm:px-8 sm:py-16">
                        <h2 className="text-2xl font-bold text-primary-foreground sm:text-3xl lg:text-4xl">
                            Elevate your wealth
                            <br />
                            to the <span className="text-accent">EdgeXchange tier.</span>
                        </h2>
                        <p className="mx-auto mt-4 max-w-lg text-sm text-primary-foreground/70">
                            By removing the risk of real financial loss, it gives beginners a confidence-building
                            environment to learn trading fundamentals — including how portfolio drift develops over
                            time when positions go unmanaged.
                        </p>
                        <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
                            <Link
                                href="/register"
                                className="rounded-lg bg-card px-6 py-3 text-sm font-semibold text-foreground transition-opacity hover:opacity-90"
                            >
                                Start Trading
                            </Link>
                            <a
                                href="#features"
                                className="rounded-lg border border-primary-foreground/20 px-6 py-3 text-sm font-semibold text-primary-foreground transition-colors hover:bg-primary-foreground/10"
                            >
                                Learn more
                            </a>
                        </div>
                    </div>
                </div>
            </section>

            {/* ── Footer ────────────────────────────────────────────────────── */}
            <footer className="border-t border-border py-12">
                <div className="mx-auto max-w-screen-xl px-4 sm:px-6">
                    <div className="grid gap-8 sm:grid-cols-2 md:grid-cols-4">

                        {/* Brand blurb */}
                        <div className="sm:col-span-2 md:col-span-1">
                            <div className="text-lg font-bold text-foreground">EdgeXchange</div>
                            <p className="mt-2 text-sm text-muted-foreground">
                                The premium standard for digital asset exchange and portfolio management.
                            </p>
                        </div>

                        {/* Link columns */}
                        {FOOTER_COLUMNS.map((column) => (
                            <div key={column.title}>
                                <div className="section-label">{column.title}</div>
                                <ul className="mt-3 space-y-2">
                                    {column.links.map((link) => (
                                        <li key={link.label}>
                                            <Link href={link.href} className="text-sm text-muted-foreground hover:text-foreground">
                                                {link.label}
                                            </Link>
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        ))}
                    </div>

                    {/* Bottom bar */}
                    <div className="mt-12 flex flex-col gap-4 border-t border-border pt-6 text-xs text-muted-foreground sm:flex-row sm:items-center sm:justify-between">
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