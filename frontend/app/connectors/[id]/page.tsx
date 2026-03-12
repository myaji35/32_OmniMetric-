"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { ArrowLeft, RefreshCw, Trash2, Database, Key, Shield } from "react-feather";
import Header from "@/components/layout/Header";
import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import Badge from "@/components/ui/Badge";

export default function ConnectorDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [detail, setDetail] = useState<Record<string, unknown> | null>(null);
  const [verifyKey, setVerifyKey] = useState("");
  const [verifyResult, setVerifyResult] = useState<{ valid: boolean; message: string } | null>(null);
  const [schema, setSchema] = useState<Record<string, unknown> | null>(null);
  const [syncResult, setSyncResult] = useState<string | null>(null);

  useEffect(() => {
    fetch(`http://localhost:8000/v1/connectors/${id}`)
      .then((r) => r.json())
      .then(setDetail)
      .catch(() => setDetail(null));
  }, [id]);

  const handleVerify = async () => {
    const res = await fetch(`http://localhost:8000/v1/connectors/${id}/verify`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ api_key: verifyKey }),
    });
    setVerifyResult(await res.json());
  };

  const handleRenew = async () => {
    if (!confirm("API Key를 갱신하시겠습니까? 기존 키는 폐기됩니다.")) return;
    const res = await fetch(`http://localhost:8000/v1/connectors/${id}/renew`, { method: "POST" });
    const data = await res.json();
    alert(`새 API Key: ${data.new_api_key || data.message}`);
  };

  const handleSync = async () => {
    const res = await fetch(`http://localhost:8000/v1/connectors/${id}/sync`, { method: "POST" });
    const data = await res.json();
    setSyncResult(data.message || "동기화 완료");
  };

  const handleSchema = async () => {
    const res = await fetch(`http://localhost:8000/v1/connectors/${id}/schema`);
    setSchema(await res.json());
  };

  const handleDelete = async () => {
    if (!confirm("이 커넥터를 해제하시겠습니까?")) return;
    await fetch(`http://localhost:8000/v1/connectors/${id}`, { method: "DELETE" });
    router.push("/connectors");
  };

  return (
    <>
      <Header
        title={`커넥터 상세`}
        subtitle={id}
        actions={
          <div className="flex gap-2">
            <Button size="sm" onClick={handleRenew}>
              <span className="flex items-center gap-1"><Key size={12} /> 갱신</span>
            </Button>
            <Button size="sm" variant="danger" onClick={handleDelete}>
              <span className="flex items-center gap-1"><Trash2 size={12} /> 해제</span>
            </Button>
          </div>
        }
      />
      <div className="flex-1 overflow-y-auto p-6 bg-[#F3F2F2]">
        <button
          onClick={() => router.push("/connectors")}
          className="flex items-center gap-1 text-sm text-[#54698D] hover:text-[#00A1E0] mb-4"
        >
          <ArrowLeft size={14} /> 목록으로
        </button>

        {detail ? (
          <div className="space-y-4">
            {/* Basic Info */}
            <Card title="기본 정보">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <InfoRow label="Tenant" value={String(detail.tenant_name || "-")} />
                <InfoRow label="ID" value={String(detail.connector_id || id)} />
                <InfoRow label="Status" value={String(detail.status || "-")} />
                <InfoRow label="Scopes" value={Array.isArray(detail.scopes) ? detail.scopes.join(", ") : "-"} />
                <InfoRow label="Callback" value={String(detail.callback_url || "-")} />
                <InfoRow label="IP Whitelist" value={Array.isArray(detail.ip_whitelist) ? detail.ip_whitelist.join(", ") : "없음"} />
              </div>
            </Card>

            {/* Verify Key */}
            <Card title="API Key 검증" actions={<Shield size={16} className="text-[#54698D]" />}>
              <div className="flex gap-2">
                <input
                  className="flex-1 px-3 py-2.5 border border-gray-300 rounded-lg text-sm text-gray-900 placeholder-gray-400 focus:outline-none focus:border-[#00A1E0] focus:ring-1 focus:ring-[#00A1E0]"
                  placeholder="API Key 입력..."
                  value={verifyKey}
                  onChange={(e) => setVerifyKey(e.target.value)}
                />
                <Button onClick={handleVerify}>검증하기</Button>
              </div>
              {verifyResult && (
                <div className={`mt-3 p-3 rounded-lg text-sm ${verifyResult.valid ? "bg-[#04844B]/10 text-[#04844B]" : "bg-[#C23934]/10 text-[#C23934]"}`}>
                  {verifyResult.message}
                </div>
              )}
            </Card>

            {/* Data Sync */}
            <Card
              title="데이터 수집"
              actions={
                <Button size="sm" variant="secondary" onClick={handleSync}>
                  <span className="flex items-center gap-1"><RefreshCw size={12} /> 동기화</span>
                </Button>
              }
            >
              {syncResult ? (
                <p className="text-sm text-[#04844B]">{syncResult}</p>
              ) : (
                <p className="text-sm text-[#54698D]">수동 동기화를 실행하세요.</p>
              )}
            </Card>

            {/* Schema */}
            <Card
              title="스키마 탐색"
              actions={
                <Button size="sm" variant="secondary" onClick={handleSchema}>
                  <span className="flex items-center gap-1"><Database size={12} /> 탐색</span>
                </Button>
              }
            >
              {schema ? (
                <div className="overflow-x-auto">
                  <pre className="text-xs bg-gray-50 p-3 rounded-lg overflow-auto">
                    {JSON.stringify(schema, null, 2)}
                  </pre>
                </div>
              ) : (
                <p className="text-sm text-[#54698D]">스키마 탐색 버튼을 클릭하세요.</p>
              )}
            </Card>
          </div>
        ) : (
          <p className="text-sm text-[#54698D]">로딩 중...</p>
        )}
      </div>
    </>
  );
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <span className="text-xs font-semibold text-gray-600">{label}</span>
      <p className="text-[#16325C] mt-0.5">{value}</p>
    </div>
  );
}
