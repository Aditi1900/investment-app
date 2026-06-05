"use client";

import { useRouter } from "next/navigation";
import AppSidebar from "../components/Sidebar";
import { Bell, Settings, User } from "lucide-react";
import { useSession } from "@/context/SessionContext";

export default function AppLayout({ children }) {
    const router = useRouter();
    const { ready, user } = useSession();

    if (!ready) return null;
    if (!user) return null;

    return (
        <div className="flex h-screen overflow-hidden bg-background">
            <AppSidebar />

            <div className="flex flex-1 flex-col overflow-hidden">
                <header className="flex h-16 items-center justify-end border-b border-border bg-card px-6">
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