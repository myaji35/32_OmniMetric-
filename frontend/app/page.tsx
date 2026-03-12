"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  Activity,
  Link2,
  BarChart2,
  Cpu,
  Upload,
  ArrowRight,
} from "react-feather";
import Header from "@/components/layout/Header";
import Card from "@/components/ui/Card";
import Badge from "@/components/ui/Badge";

interface HealthData {
  status: string;
  version: string;
  environment: string;
}

export default function DashboardPage() {
  const [health, setHealth] = useState<HealthData | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch("http://localhost:8000/health")
      .then((r) => r.json())
      .then(setHealth)
      .catch(() => setError("API 서버에 연결할 수 없습니다"));
  }, []);

  return (
    <>
      <Header title="OmniMetric Dashboard" subtitle="분석 엔진 대시보드" />
      <div className="flex-1 overflow-y-auto p-6 bg-[#F3F2F2]">
        {/* KPI Cards */}
        <div className="grid grid-cols-4 gap-4 mb-6">
          <StatCard
            icon={<Activity size={20} />}
            label="API 상태"
            value={health ? "Active" : error ? "Offline" : "확인 중..."}
            color={health ? "#04844B" : error ? "#C23934" : "#FFB75D"}
          />
          <StatCard
            icon={<Link2 size={20} />}
            label="연동 고객사"
            value="-"
            color="#00A1E0"
          />
          <StatCard
            icon={<BarChart2 size={20} />}
            label="최근 분석"
            value="-"
            color="#00A1E0"
          />
          <StatCard
            icon={<Cpu size={20} />}
            label="알고리즘"
            value="155+"
            color="#16325C"
            sub="4 유형"
          />
        </div>

        <div className="grid grid-cols-3 gap-4">
          {/* Quick Actions */}
          <Card title="빠른 실행">
            <div className="space-y-2">
              <QuickAction
                href="/data"
                icon={<Upload size={16} />}
                label="데이터 업로드"
              />
              <QuickAction
                href="/analyze"
                icon={<BarChart2 size={16} />}
                label="분석 시작"
              />
              <QuickAction
                href="/connectors"
                icon={<Link2 size={16} />}
                label="커넥터 관리"
              />
            </div>
          </Card>

          {/* System Info */}
          <Card title="시스템 정보">
            <div className="space-y-3 text-sm">
              <InfoRow label="Version" value={health?.version || "-"} />
              <InfoRow label="Environment" value={health?.environment || "-"} />
              <InfoRow label="Backend" value="localhost:8000" />
              <InfoRow label="Frontend" value="localhost:3032" />
            </div>
          </Card>

          {/* Algorithm Types */}
          <Card title="분석 유형">
            <div className="space-y-2">
              <AlgoType label="회귀분석" count={60} color="#00A1E0" />
              <AlgoType label="이진분류" count={17} color="#04844B" />
              <AlgoType label="다중분류" count={17} color="#FFB75D" />
              <AlgoType label="시계열분석" count={61} color="#16325C" />
            </div>
          </Card>
        </div>
      </div>
    </>
  );
}

function StatCard({
  icon,
  label,
  value,
  color,
  sub,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
  color: string;
  sub?: string;
}) {
  return (
    <div className="bg-white border border-gray-200 rounded-lg shadow-sm p-4">
      <div className="flex items-center gap-3 mb-2">
        <div
          className="w-9 h-9 rounded-lg flex items-center justify-center text-white"
          style={{ background: color }}
        >
          {icon}
        </div>
        <span className="text-xs font-semibold text-gray-600">{label}</span>
      </div>
      <p className="text-xl font-bold text-[#16325C]">{value}</p>
      {sub && <p className="text-xs text-[#54698D] mt-0.5">{sub}</p>}
    </div>
  );
}

function QuickAction({
  href,
  icon,
  label,
}: {
  href: string;
  icon: React.ReactNode;
  label: string;
}) {
  return (
    <Link
      href={href}
      className="flex items-center justify-between px-3 py-2.5 rounded-lg border border-gray-200 hover:border-[#00A1E0] hover:bg-[#00A1E0]/5 transition-colors text-sm text-[#16325C]"
    >
      <div className="flex items-center gap-2">
        {icon}
        <span>{label}</span>
      </div>
      <ArrowRight size={14} className="text-[#54698D]" />
    </Link>
  );
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between">
      <span className="text-[#54698D]">{label}</span>
      <span className="font-medium text-[#16325C]">{value}</span>
    </div>
  );
}

function AlgoType({
  label,
  count,
  color,
}: {
  label: string;
  count: number;
  color: string;
}) {
  return (
    <div className="flex items-center justify-between px-3 py-2 rounded-lg bg-gray-50">
      <span className="text-sm text-[#16325C]">{label}</span>
      <Badge label={`${count}개`} color={color} />
    </div>
  );
}
