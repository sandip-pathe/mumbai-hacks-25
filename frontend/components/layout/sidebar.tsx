"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Bell,
  MessageSquare,
  FileText,
  Shield,
  Settings,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useUIStore } from "@/store/ui-store";
import Image from "next/image";

const navigation = [
  { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { name: "Alerts", href: "/alerts", icon: Bell },
  { name: "Chat", href: "/chat", icon: MessageSquare },
  { name: "Policies", href: "/policies", icon: FileText },
  { name: "Scanner", href: "/scanner", icon: Shield },
  { name: "Settings", href: "/settings", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();
  const { sidebarOpen, toggleSidebar } = useUIStore();

  return (
    <aside
      className={cn(
        "fixed left-0 top-0 h-screen transition-all duration-300 z-40",
        sidebarOpen ? "w-64" : "w-20"
      )}
      style={{ backgroundColor: "#0B0B0D", color: "#E1EAF2" }}
    >
      {/* Logo */}
      <div className="h-16 flex items-center px-4 border-b border-white/20">
        {sidebarOpen ? (
          // Expanded: show logo + brand name + chevron side by side
          <div className="w-full flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Image
                width={40}
                height={40}
                src="/logo.svg"
                alt="Anaya logo"
                className="w-10 h-10 rounded-md object-cover"
              />
              <span
                className="text-xl font-heading font-bold"
                style={{
                  background: "linear-gradient(135deg, #3D6DEB, #7B61FF)",
                  WebkitBackgroundClip: "text",
                  WebkitTextFillColor: "transparent",
                  backgroundClip: "text",
                }}
              >
                Anaya
              </span>
            </div>
            <button
              onClick={toggleSidebar}
              className="p-1 hover:bg-white/10 rounded-lg transition-colors"
              aria-label="Collapse sidebar"
            >
              <ChevronLeft size={20} />
            </button>
          </div>
        ) : (
          // Collapsed: show only logo, chevron overlays on hover
          <div className="relative group w-full flex justify-center">
            <button
              onClick={toggleSidebar}
              className="relative w-10 h-10"
              aria-label="Expand sidebar"
            >
              <Image
                width={40}
                height={40}
                src="/logo.svg"
                alt="Anaya logo"
                className="w-10 h-10 rounded-md object-cover"
              />
              {/* Chevron overlay - appears on hover */}
              <div className="absolute inset-0 flex items-center justify-center bg-black/60 rounded-md opacity-0 group-hover:opacity-100 transition-opacity">
                <ChevronRight size={20} className="text-white" />
              </div>
            </button>
          </div>
        )}
      </div>

      {/* Navigation */}
      <nav className="p-4 space-y-2">
        {navigation.map((item) => {
          const isActive = pathname === item.href;
          const Icon = item.icon;

          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                "flex items-center gap-3 px-4 py-3 rounded-lg transition-all",
                // center icons when collapsed, align left when expanded
                sidebarOpen ? "justify-start" : "justify-center",
                // hover: subtle white background with light text (not pure white text)
                "hover:bg-white/5",
                // inactive: light gray text, active: accent bg with white text
                !isActive && "text-gray-300",
                isActive && "bg-accent text-white shadow-md"
              )}
            >
              <Icon className="text-current" size={20} />
              {sidebarOpen && <span className="font-medium">{item.name}</span>}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
