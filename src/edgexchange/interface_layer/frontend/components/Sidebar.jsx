"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  LayoutDashboard,
  Briefcase,
  Zap,
  HelpCircle,
  LogOut,
  Home,
} from "lucide-react";
import Image from "next/image";
import logo from "@/assets/logo.jpeg";
import { useSession } from "@/context/SessionContext";

const mainLinks = [
  { icon: Home, label: "Home", path: "/" },
  { icon: LayoutDashboard, label: "Dashboard", path: "/dashboard" },
  { icon: Briefcase, label: "Portfolio", path: "/portfolio" },
  { icon: Zap, label: "Execute", path: "/execute" },
];

export default function AppSidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const { logout } = useSession();

  const handleLogout = async () => {
    await logout();
    router.push("/");
  };

  return (
    <aside className="flex h-screen w-56 flex-col border-r border-border bg-card">
      <div className="p-6">
        <div className="flex items-center gap-3">
          <Image
            src={logo}
            alt="EdgeXchange"
            width={36}
            height={36}
            className="rounded-lg object-cover"
          />
          <div>
            <div className="text-sm font-bold uppercase">EdgeXchange</div>
            <div className="text-[10px] uppercase text-accent">
              Institutional Ledger
            </div>
          </div>
        </div>
      </div>

      <nav className="flex-1 space-y-1 px-3">
        {mainLinks.map((link) => {
          const isActive = pathname === link.path;
          return (
            <Link
              key={link.path}
              href={link.path}
              className={`flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm ${
                isActive
                  ? "bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:bg-secondary"
              }`}
            >
              <link.icon size={18} />
              {link.label}
            </Link>
          );
        })}
      </nav>

      <div className="border-t border-border p-3 space-y-1">
        <button className="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm text-muted-foreground hover:bg-secondary">
          <HelpCircle size={18} />
          Support
        </button>
        <button
          onClick={handleLogout}
          className="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm text-muted-foreground hover:bg-secondary"
        >
          <LogOut size={18} />
          Sign Out
        </button>
      </div>
    </aside>
  );
}