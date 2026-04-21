"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import AppSidebar from "../components/Sidebar";
import { Bell, Settings, Search, User } from "lucide-react";
import { useSession } from "@/context/SessionContext";

export default function AppLayout({ children }) {
    const router = useRouter();
    const { ready, user } = useSession();

    const [searchQuery, setSearchQuery] = useState("");

    const handleSearchKeyDown = (e) => {
        if (e.key === "Enter" && searchQuery.trim()) {
            router.push(
                `/execute?ticker=${encodeURIComponent(
                    searchQuery.trim().toUpperCase()
                )}`
            );
            setSearchQuery("");
        }
    };

    // Wait for hydration
    if (!ready) return null;

    // Not logged in — just show nothing, login page handles auth
    if (!user) return null;

    return (
        <div className="flex h-screen overflow-hidden bg-background">
            <AppSidebar />

            <div className="flex flex-1 flex-col overflow-hidden">
                <header className="flex h-16 items-center justify-between border-b border-border bg-card px-6">
                    <div className="flex items-center gap-2 rounded-lg bg-secondary px-3 py-2 text-sm text-muted-foreground">
                        <Search size={16} />
                        <input
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            onKeyDown={handleSearchKeyDown}
                            placeholder="Search stocks..."
                            className="w-40 bg-transparent text-sm outline-none"
                        />
                    </div>

                    <div className="flex items-center gap-4">
                        <button>
                            <Bell size={18} />
                        </button>
                        <button>
                            <Settings size={18} />
                        </button>

                        <button
                            onClick={() => router.push("/dashboard")}
                            className="flex h-8 w-8 items-center justify-center rounded-full bg-secondary"
                        >
                            <User size={16} />
                        </button>
                    </div>
                </header>

                <main className="flex-1 overflow-y-auto p-6">
                    {children}
                </main>
            </div>
        </div>
    );
}