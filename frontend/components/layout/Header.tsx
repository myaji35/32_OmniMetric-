"use client";

import { Activity } from "react-feather";

interface HeaderProps {
  title: string;
  subtitle?: string;
  actions?: React.ReactNode;
}

export default function Header({ title, subtitle, actions }: HeaderProps) {
  return (
    <header className="h-14 bg-[#16325C] flex items-center justify-between px-6">
      <div className="flex items-center gap-3">
        <h1 className="text-white font-semibold text-base">{title}</h1>
        {subtitle && (
          <span className="text-white/65 text-sm">{subtitle}</span>
        )}
      </div>
      <div className="flex items-center gap-3">
        {actions}
        <div className="flex items-center gap-1.5 text-white/70 text-xs">
          <Activity size={14} />
          <span>API 연결됨</span>
        </div>
      </div>
    </header>
  );
}
