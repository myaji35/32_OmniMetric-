"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Plus, RefreshCw, CheckCircle, XCircle } from "react-feather";
import Header from "@/components/layout/Header";
import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import Badge from "@/components/ui/Badge";

interface ConnectorItem {
  connector_id: string;
  tenant_name: string;
  status: string;
  created_at: string;
  scopes: string[];
  api_key?: string;
}

export default function ConnectorsPage() {
  const [connectors, setConnectors] = useState<ConnectorItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [form, setForm] = useState({
    tenant_name: "",
    callback_url: "",
    scopes: ["read"],
    ip_whitelist: "",
  });
  const [created, setCreated] = useState<ConnectorItem | null>(null);

  const fetchList = () => {
    setLoading(true);
    fetch("http://localhost:8000/v1/connectors")
      .then((r) => r.json())
      .then((data) => setConnectors(Array.isArray(data) ? data : []))
      .catch(() => setConnectors([]))
      .finally(() => setLoading(false));
  };

  useEffect(() => { fetchList(); }, []);

  const handleCreate = async () => {
    try {
      const body = {
        tenant_name: form.tenant_name,
        callback_url: form.callback_url,
        scopes: form.scopes,
        ip_whitelist: form.ip_whitelist
          ? form.ip_whitelist.split(",").map((s) => s.trim())
          : undefined,
      };
      const res = await fetch("http://localhost:8000/v1/connectors", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      const data = await res.json();
      setCreated(data);
      setShowCreate(false);
      setForm({ tenant_name: "", callback_url: "", scopes: ["read"], ip_whitelist: "" });
      fetchList();
    } catch {
      alert("생성 실패");
    }
  };

  return (
    <>
      <Header
        title="B2B 커넥터 관리"
        subtitle="고객사 연동 및 API Key 관리"
        actions={
          <Button size="sm" onClick={() => setShowCreate(true)}>
            <span className="flex items-center gap-1.5">
              <Plus size={14} /> 고객사 등록
            </span>
          </Button>
        }
      />
      <div className="flex-1 overflow-y-auto p-6 bg-[#F3F2F2]">
        {/* Created API Key Alert */}
        {created?.api_key && (
          <div className="mb-4 p-4 bg-[#04844B]/10 border border-[#04844B]/30 rounded-lg">
            <p className="text-sm font-semibold text-[#04844B] mb-1">
              API Key가 발행되었습니다 (이 화면을 벗어나면 다시 볼 수 없습니다)
            </p>
            <code className="text-sm bg-white px-3 py-1.5 rounded border border-gray-200 block mt-2 select-all">
              {created.api_key}
            </code>
            <Button size="sm" variant="secondary" className="mt-2" onClick={() => setCreated(null)}>
              확인
            </Button>
          </div>
        )}

        {/* Create Modal */}
        {showCreate && (
          <Card title="고객사 연동 등록" className="mb-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-gray-600 mb-1.5">고객사 이름</label>
                <input
                  className="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm text-gray-900 placeholder-gray-400 focus:outline-none focus:border-[#00A1E0] focus:ring-1 focus:ring-[#00A1E0]"
                  placeholder="예: 누리팜"
                  value={form.tenant_name}
                  onChange={(e) => setForm({ ...form, tenant_name: e.target.value })}
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-gray-600 mb-1.5">콜백 URL</label>
                <input
                  className="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm text-gray-900 placeholder-gray-400 focus:outline-none focus:border-[#00A1E0] focus:ring-1 focus:ring-[#00A1E0]"
                  placeholder="https://example.com/webhook"
                  value={form.callback_url}
                  onChange={(e) => setForm({ ...form, callback_url: e.target.value })}
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-gray-600 mb-1.5">권한 범위</label>
                <select
                  className="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm text-gray-900 bg-white focus:outline-none focus:border-[#00A1E0] focus:ring-1 focus:ring-[#00A1E0]"
                  value={form.scopes[0]}
                  onChange={(e) => setForm({ ...form, scopes: [e.target.value] })}
                >
                  <option value="read">read</option>
                  <option value="write">read, write</option>
                  <option value="admin">admin</option>
                </select>
              </div>
              <div>
                <label className="block text-xs font-semibold text-gray-600 mb-1.5">IP 화이트리스트 (쉼표 구분)</label>
                <input
                  className="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm text-gray-900 placeholder-gray-400 focus:outline-none focus:border-[#00A1E0] focus:ring-1 focus:ring-[#00A1E0]"
                  placeholder="10.0.1.0/24, 192.168.1.100"
                  value={form.ip_whitelist}
                  onChange={(e) => setForm({ ...form, ip_whitelist: e.target.value })}
                />
              </div>
            </div>
            <div className="flex gap-2 mt-4">
              <Button onClick={handleCreate}>등록하기</Button>
              <Button variant="secondary" onClick={() => setShowCreate(false)}>취소</Button>
            </div>
          </Card>
        )}

        {/* Connector Grid */}
        {loading ? (
          <p className="text-sm text-[#54698D]">로딩 중...</p>
        ) : connectors.length === 0 ? (
          <Card>
            <div className="text-center py-8">
              <p className="text-[#54698D] text-sm mb-3">등록된 커넥터가 없습니다</p>
              <Button onClick={() => setShowCreate(true)}>
                <span className="flex items-center gap-1.5">
                  <Plus size={14} /> 첫 고객사 등록하기
                </span>
              </Button>
            </div>
          </Card>
        ) : (
          <div className="grid grid-cols-2 gap-4">
            {connectors.map((c) => (
              <Link key={c.connector_id} href={`/connectors/${c.connector_id}`}>
                <div className="bg-white border border-gray-200 rounded-lg shadow-sm p-4 hover:border-[#00A1E0] transition-colors cursor-pointer">
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="font-semibold text-[#16325C] text-sm">{c.tenant_name}</h4>
                    <Badge
                      label={c.status}
                      color={c.status === "active" ? "#04844B" : "#C23934"}
                    />
                  </div>
                  <div className="text-xs text-[#54698D] space-y-1">
                    <p>ID: {c.connector_id}</p>
                    <p>Scopes: {c.scopes?.join(", ") || "read"}</p>
                    <p>생성: {c.created_at ? new Date(c.created_at).toLocaleDateString("ko") : "-"}</p>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </>
  );
}
