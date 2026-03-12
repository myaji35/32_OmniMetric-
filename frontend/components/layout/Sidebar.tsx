"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Home,
  Link2,
  Upload,
  BarChart2,
  FileText,
  Sliders,
  Zap,
  MessageCircle,
} from "react-feather";

const navItems = [
  { href: "/", label: "대시보드", icon: Home },
  { href: "/connectors", label: "B2B 커넥터", icon: Link2 },
  { href: "/data", label: "데이터 관리", icon: Upload },
  { href: "/analyze", label: "분석 실행", icon: BarChart2 },
  { href: "/report", label: "분석 결과", icon: FileText, dynamic: true },
  { href: "/simulate", label: "시뮬레이션", icon: Sliders, dynamic: true },
  { href: "/actions", label: "행동 시나리오", icon: Zap, dynamic: true },
  { href: "/qa", label: "AI Q&A", icon: MessageCircle, dynamic: true },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-60 bg-white border-r border-gray-200 flex flex-col h-full">
      <div className="h-14 flex items-center px-5 border-b border-gray-200">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-[#00A1E0] flex items-center justify-center">
            <BarChart2 size={18} className="text-white" />
          </div>
          <span className="font-bold text-[#16325C] text-sm">OmniMetric</span>
        </div>
      </div>
      <nav className="flex-1 py-3 px-3">
        {navItems.map((item) => {
          const isActive =
            pathname === item.href ||
            (item.href !== "/" && pathname.startsWith(item.href));
          const Icon = item.icon;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm mb-0.5 transition-colors ${
                isActive
                  ? "bg-[#00A1E0]/10 text-[#00A1E0] font-medium"
                  : "text-[#54698D] hover:bg-gray-50 hover:text-[#16325C]"
              }`}
            >
              <Icon size={18} strokeWidth={2} />
              <span>{item.label}</span>
            </Link>
          );
        })}
      </nav>
      <div className="px-5 py-4 border-t border-gray-200">
        <p className="text-xs text-[#54698D]">v1.0.0 | Port 3032</p>
      </div>
    </aside>
  );
}
