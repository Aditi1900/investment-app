"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useState } from "react";
import { Bell, Settings, User, Menu, X } from "lucide-react";
import logo from "../assets/logo.jpeg";
import Image from "next/image";

const navLinks = [
    { label: "Dashboard", path: "/dashboard" },
    { label: "Portfolio", path: "/portfolio" },
    { label: "Execute", path: "/execute" },
];

export default function Navbar() {
    const router = useRouter();
    const pathname = usePathname();
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

    return (
        <header className="sticky top-0 z-50 border-b border-border bg-card">
            <div className="mx-auto flex h-16 max-w-screen-xl items-center justify-between px-4 sm:px-6">
                <Link href="/" className="flex items-center gap-2 font-bold">
                    <Image
                        src={logo}
                        alt="EdgeXchange"
                        width={36}
                        height={36}
                        className="rounded-lg object-cover"
                    />
                    EdgeXchange
                </Link>

                {/* Desktop nav */}
                <nav className="hidden gap-8 md:flex">
                    {navLinks.map((link) => (
                        <Link
                            key={link.path}
                            href={link.path}
                            className={`text-sm font-medium ${pathname === link.path
                                    ? "text-foreground underline underline-offset-8"
                                    : "text-muted-foreground hover:text-foreground"
                                }`}
                        >
                            {link.label}
                        </Link>
                    ))}
                </nav>

                {/* Desktop right icons */}
                <div className="hidden items-center gap-4 md:flex">
                    <Bell size={18} />
                    <Settings size={18} />
                    <button
                        onClick={() => router.push("/dashboard")}
                        className="flex h-8 w-8 items-center justify-center rounded-full bg-secondary"
                    >
                        <User size={16} />
                    </button>
                </div>

                {/* Mobile hamburger */}
                <button
                    className="flex items-center justify-center rounded-lg p-2 text-muted-foreground hover:bg-secondary md:hidden"
                    onClick={() => setMobileMenuOpen((o) => !o)}
                    aria-label="Toggle menu"
                >
                    {mobileMenuOpen ? <X size={20} /> : <Menu size={20} />}
                </button>
            </div>

            {/* Mobile dropdown menu */}
            {mobileMenuOpen && (
                <div className="border-t border-border bg-card px-4 pb-4 md:hidden">
                    <nav className="flex flex-col gap-1 pt-2">
                        {navLinks.map((link) => (
                            <Link
                                key={link.path}
                                href={link.path}
                                onClick={() => setMobileMenuOpen(false)}
                                className={`rounded-lg px-3 py-2.5 text-sm font-medium ${pathname === link.path
                                        ? "bg-primary text-primary-foreground"
                                        : "text-muted-foreground hover:bg-secondary"
                                    }`}
                            >
                                {link.label}
                            </Link>
                        ))}
                    </nav>
                    <div className="mt-3 flex items-center gap-3 border-t border-border pt-3">
                        <button aria-label="Notifications"><Bell size={18} /></button>
                        <button aria-label="Settings"><Settings size={18} /></button>
                        <button
                            onClick={() => { router.push("/dashboard"); setMobileMenuOpen(false); }}
                            className="flex h-8 w-8 items-center justify-center rounded-full bg-secondary"
                            aria-label="Profile"
                        >
                            <User size={16} />
                        </button>
                    </div>
                </div>
            )}
        </header>
    );
}