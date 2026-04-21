"use client";

import Link from "next/link";
import { usePathname, useRouter} from "next/navigation";
import { Bell, Settings, User } from "lucide-react";
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

  return (
    <header className="sticky top-0 z-50 border-b border-border bg-card">
      <div className="mx-auto flex h-16 max-w-screen-xl items-center justify-between px-6">
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

        <nav className="hidden gap-8 md:flex">
          {navLinks.map((link) => (
            <Link
              key={link.path}
              href={link.path}
              className={`text-sm font-medium ${
                pathname === link.path
                  ? "text-foreground underline underline-offset-8"
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              {link.label}
            </Link>
          ))}
        </nav>

        <div className="flex items-center gap-4">
          <Bell size={18} />
          <Settings size={18} />
          <button
              onClick={() => router.push("/dashboard")}
              className="flex h-8 w-8 items-center justify-center rounded-full bg-secondary"
            >
              <User size={16} />
            </button>
        </div>
      </div>
    </header>
  );
}