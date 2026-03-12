"use client";

import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { Play, CheckCircle, XCircle, Loader } from "react-feather";
import Header from "@/components/layout/Header";
import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";

export default function AnalyzePage() {
  const router = useRouter();
  const [taskType, setTaskType] = useState<string>("regression");
  const [enableXai, setEnableXai] = useState(true);
  const [webhookUrl, setWebhookUrl] = useState("");
  const [dataText, setDataText] = useState("");
  const [targetColumn, setTargetColumn] = useState("");
  const [taskId, setTaskId] = useState<string | null>(null);
  const [status, setStatus] = useState<string | null>(null);
  const [progress, setProgress] = useState<number | null>(null);
  const [message, setMessage] = useState("");
  const [running, setRunning] = useState(false);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const taskTypes = [
    { value: "regression", label: "회귀분석", count: 60 },
    { value: "classification", label: "이진분류", count: 17 },
    { value: "multiclass", label: "다중분류", count: 17 },
    { value: "timeseries", label: "시계열분석", count: 61 },
  ];

  const handleStart = async () => {
    if (!dataText.trim() || !targetColumn.trim()) {
      alert("데이터(JSON 배열)와 타겟 컬럼을 입력하세요");
      return;
    }
    setRunning(true);
    try {
      let data: Record<string, unknown>[];
      try {
        data = JSON.parse(dataText);
      } catch {
        alert("JSON 형식이 올바르지 않습니다");
        setRunning(false);
        return;
      }
      const res = await fetch("http://localhost:8000/v1/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          data,
          target_column: targetColumn,
          task_type: taskType,
          enable_xai: enableXai,
          ...(webhookUrl ? { webhook_url: webhookUrl } : {}),
        }),
      });
      const result = await res.json();
      setTaskId(result.task_id);
      setStatus(result.status);
      setMessage(result.message);
      startPolling(result.task_id);
    } catch {
      alert("분석 시작 실패");
      setRunning(false);
    }
  };

  const startPolling = (tid: string) => {
    pollRef.current = setInterval(async () => {
      try {
        const res = await fetch(`http://localhost:8000/v1/status/${tid}`);
        const s = await res.json();
        setStatus(s.status);
        setProgress(s.progress);
        setMessage(s.message);
        if (s.status === "completed" || s.status === "failed") {
          if (pollRef.current) clearInterval(pollRef.current);
          setRunning(false);
        }
      } catch {
        // ignore poll error
      }
    }, 3000);
  };

  useEffect(() => {
    return () => {
      if (pollRef.current) clearInterval(pollRef.current);
    };
  }, []);

  return (
    <>
      <Header title="분석 실행" subtitle="알고리즘 토너먼트 시작" />
      <div className="flex-1 overflow-y-auto p-6 bg-[#F3F2F2] space-y-4">
        {/* Settings */}
        <Card title="분석 설정">
          <div className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-gray-600 mb-1.5">타겟 컬럼 (Y)</label>
              <input
                className="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm text-gray-900 placeholder-gray-400 focus:outline-none focus:border-[#00A1E0] focus:ring-1 focus:ring-[#00A1E0]"
                placeholder="예: target"
                value={targetColumn}
                onChange={(e) => setTargetColumn(e.target.value)}
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-gray-600 mb-1.5">분석 유형</label>
              <div className="grid grid-cols-4 gap-2">
                {taskTypes.map((t) => (
                  <button
                    key={t.value}
                    onClick={() => setTaskType(t.value)}
                    className={`px-3 py-3 rounded-lg border text-sm text-center transition-colors ${
                      taskType === t.value
                        ? "border-[#00A1E0] bg-[#00A1E0]/10 text-[#00A1E0] font-medium"
                        : "border-gray-200 text-[#54698D] hover:border-gray-300"
                    }`}
                  >
                    <span className="block">{t.label}</span>
                    <span className="block text-xs mt-0.5">{t.count}개 알고리즘</span>
                  </button>
                ))}
              </div>
            </div>
            <div className="flex items-center gap-3">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={enableXai}
                  onChange={(e) => setEnableXai(e.target.checked)}
                  className="rounded border-gray-300"
                />
                <span className="text-sm text-[#16325C]">XAI 분석 활성화 (SHAP/LIME)</span>
              </label>
            </div>
            <div>
              <label className="block text-xs font-semibold text-gray-600 mb-1.5">데이터 (JSON 배열)</label>
              <textarea
                className="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm text-gray-900 placeholder-gray-400 focus:outline-none focus:border-[#00A1E0] focus:ring-1 focus:ring-[#00A1E0] h-40 font-mono"
                placeholder='[{"age": 25, "income": 50000, "target": 1}, ...]'
                value={dataText}
                onChange={(e) => setDataText(e.target.value)}
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-gray-600 mb-1.5">Webhook URL (선택)</label>
              <input
                className="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm text-gray-900 placeholder-gray-400 focus:outline-none focus:border-[#00A1E0] focus:ring-1 focus:ring-[#00A1E0]"
                placeholder="https://example.com/webhook"
                value={webhookUrl}
                onChange={(e) => setWebhookUrl(e.target.value)}
              />
            </div>
            <Button onClick={handleStart} disabled={running}>
              <span className="flex items-center gap-1.5">
                <Play size={14} /> {running ? "분석 진행 중..." : "분석 시작"}
              </span>
            </Button>
          </div>
        </Card>

        {/* Progress */}
        {taskId && (
          <Card title="진행 상태">
            <div className="space-y-3">
              <div className="flex items-center gap-3">
                <span className="text-xs font-semibold text-gray-600">Task ID:</span>
                <code className="text-sm bg-gray-50 px-2 py-0.5 rounded">{taskId}</code>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-xs font-semibold text-gray-600">Status:</span>
                <span className="flex items-center gap-1.5 text-sm">
                  {status === "completed" && <CheckCircle size={14} className="text-[#04844B]" />}
                  {status === "failed" && <XCircle size={14} className="text-[#C23934]" />}
                  {(status === "processing" || status === "pending") && <Loader size={14} className="text-[#00A1E0] animate-spin" />}
                  {status}
                </span>
              </div>
              {progress !== null && (
                <div>
                  <div className="w-full bg-gray-200 rounded-full h-3">
                    <div
                      className="bg-[#00A1E0] h-3 rounded-full transition-all duration-500"
                      style={{ width: `${progress}%` }}
                    />
                  </div>
                  <p className="text-xs text-[#54698D] mt-1">{progress}% 완료</p>
                </div>
              )}
              {message && <p className="text-sm text-[#54698D]">{message}</p>}
              {status === "completed" && (
                <Button onClick={() => router.push(`/report/${taskId}`)}>
                  <span className="flex items-center gap-1.5">결과 보기 →</span>
                </Button>
              )}
            </div>
          </Card>
        )}
      </div>
    </>
  );
}
