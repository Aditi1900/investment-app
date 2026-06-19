"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import AppSidebar from "../components/Sidebar";
import { Bell, Settings, User, Menu } from "lucide-react";
import { useSession } from "@/context/SessionContext";

export default function AppLayout({ children }) {
    const router = useRouter();
    const { ready, user } = useSession();
    const [sidebarOpen, setSidebarOpen] = useState(false);

    useEffect(() => {
        if (ready && !user) {
            router.push("/login");
        }
    }, [ready, user, router]);

    // Loading session, or redirecting because there's no user — same UI either way.
    if (!ready || !user) {
        return (
            <div className="flex h-screen items-center justify-center bg-background">
                <div className="h-8 w-8 rounded-full border-2 border-border border-t-foreground animate-spin" />
            </div>
        );
    }

    return (
        <div className="flex h-screen overflow-hidden bg-background">
            {sidebarOpen && (
                <div
                    className="fixed inset-0 z-20 bg-black/40 lg:hidden"
                    onClick={() => setSidebarOpen(false)}
                />
            )}

            <div
                className={`fixed inset-y-0 left-0 z-30 transition-transform duration-200
                    lg:static lg:z-auto lg:translate-x-0 lg:w-56 lg:shrink-0
                    ${sidebarOpen ? "translate-x-0" : "-translate-x-full"}`}
            >
                <AppSidebar onClose={() => setSidebarOpen(false)} />
            </div>

            <div className="flex flex-1 flex-col overflow-hidden min-w-0">
                <header className="flex h-16 items-center justify-between border-b border-border bg-card px-4 sm:px-6">
                    <button
                        className="flex items-center justify-center rounded-lg p-2 text-muted-foreground hover:bg-secondary lg:hidden"
                        onClick={() => setSidebarOpen(true)}
                        aria-label="Open menu"
                    >
                        <Menu size={20} />
                    </button>

                    <div className="ml-auto flex items-center gap-4">
                        <button aria-label="Notifications">
                            <Bell size={18} />
                        </button>

                        <button aria-label="Settings">
                            <Settings size={18} />
                        </button>

                        <button
                            onClick={() => router.push("/dashboard")}
                            className="flex h-8 w-8 items-center justify-center rounded-full bg-secondary"
                            aria-label="Profile"
                        >
                            <User size={16} />
                        </button>
                    </div>
                </header>

                <main className="flex-1 overflow-y-auto px-4 pt-4 pb-24 sm:px-6 sm:pt-6">
                    {children}
                </main>
            </div>
        </div>
    );
}