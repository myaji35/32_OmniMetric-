"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { Zap, Clock, Plus } from "react-feather";
import Header from "@/components/layout/Header";
import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import Badge from "@/components/ui/Badge";

interface ActionRule {
  priority: number;
  condition: string;
  action: string;
  impact: string;
  confidence: number;
}

interface HistoryEntry {
  timestamp: string;
  scenario_count: number;
  webhook_sent: boolean;
}

export default function ActionsPage() {
  const { taskId } = useParams<{ taskId: string }>();
  const [rules, setRules] = useState<ActionRule[]>([]);
  const [history, setHistory] = useState<HistoryEntry[]>([]);
  const [webhookUrl, setWebhookUrl] = useState("");
  const [loading, setLoading] = useState(false);

  const fetchActions = async () => {
    try {
      const res = await fetch(`http://localhost:8000/v1/actions/${taskId}`);
      const data = await res.json();
      setRules(data.scenarios || []);
    } catch {
      // no existing actions
    }
  };

  const fetchHistory = async () => {
    try {
      const res = await fetch(`http://localhost:8000/v1/actions/${taskId}/history`);
      const data = await res.json();
      setHistory(data.history || []);
    } catch {
      // no history
    }
  };

  useEffect(() => {
    fetchActions();
    fetchHistory();
  }, [taskId]);

  const generateScenarios = async () => {
    setLoading(true);
    try {
      const res = await fetch(`http://localhost:8000/v1/actions/${taskId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...(webhookUrl ? { webhook_url: webhookUrl } : {}),
        }),
      });
      const data = await res.json();
      setRules(data.scenarios || []);
      fetchHistory();
    } catch {
      alert("시나리오 생성 실패");
    } finally {
      setLoading(false);
    }
  };

  const priorityColors = ["#C23934", "#FFB75D", "#00A1E0", "#04844B", "#54698D"];

  return (
    <>
      <Header
        title="행동 시나리오"
        subtitle={`Task: ${taskId}`}
        actions={
          <Button size="sm" onClick={generateScenarios} disabled={loading}>
            <span className="flex items-center gap-1.5">
              <Plus size={14} /> {loading ? "생성 중..." : "시나리오 생성"}
            </span>
          </Button>
        }
      />
      <div className="flex-1 overflow-y-auto p-6 bg-[#F3F2F2] space-y-4">
        {/* Webhook Config */}
        <Card title="Webhook 설정">
          <div className="flex gap-2">
            <input
              className="flex-1 px-3 py-2.5 border border-gray-300 rounded-lg text-sm text-gray-900 placeholder-gray-400 focus:outline-none focus:border-[#00A1E0] focus:ring-1 focus:ring-[#00A1E0]"
              placeholder="https://example.com/webhook (선택사항)"
              value={webhookUrl}
              onChange={(e) => setWebhookUrl(e.target.value)}
            />
          </div>
        </Card>

        {/* IF-THEN Cards */}
        {rules.length > 0 ? (
          <div className="space-y-3">
            {rules.map((rule, i) => (
              <Card key={i}>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <Badge
                        label={`Priority ${rule.priority}`}
                        color={priorityColors[Math.min(rule.priority - 1, 4)]}
                      />
                      <span className="text-xs text-[#54698D]">
                        신뢰도: {(rule.confidence * 100).toFixed(0)}%
                      </span>
                    </div>
                    <div className="space-y-1 text-sm">
                      <p>
                        <span className="font-semibold text-[#00A1E0]">IF</span>{" "}
                        <span className="text-[#16325C]">{rule.condition}</span>
                      </p>
                      <p>
                        <span className="font-semibold text-[#04844B]">THEN</span>{" "}
                        <span className="text-[#16325C]">{rule.action}</span>
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-xs text-[#54698D]">영향</p>
                    <p className="text-sm font-semibold text-[#16325C]">{rule.impact}</p>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        ) : (
          <Card>
            <div className="text-center py-8">
              <Zap size={32} className="mx-auto text-[#54698D] mb-3" />
              <p className="text-sm text-[#54698D]">아직 생성된 시나리오가 없습니다</p>
              <p className="text-xs text-[#54698D] mt-1">상단 버튼을 클릭하여 생성하세요</p>
            </div>
          </Card>
        )}

        {/* History */}
        {history.length > 0 && (
          <Card title="이력" actions={<Clock size={16} className="text-[#54698D]" />}>
            <div className="space-y-2">
              {history.map((h, i) => (
                <div key={i} className="flex items-center justify-between px-3 py-2 bg-gray-50 rounded-lg text-sm">
                  <span className="text-[#16325C]">
                    {new Date(h.timestamp).toLocaleString("ko")}
                  </span>
                  <span className="text-[#54698D]">
                    {h.scenario_count}건 생성
                    {h.webhook_sent && " + Webhook"}
                  </span>
                </div>
              ))}
            </div>
          </Card>
        )}
      </div>
    </>
  );
}
