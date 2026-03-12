"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Zap, ArrowRight } from "react-feather";
import Header from "@/components/layout/Header";
import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";

export default function ActionsIndexPage() {
  const router = useRouter();
  const [taskId, setTaskId] = useState("");

  const handleGo = () => {
    if (taskId.trim()) {
      router.push(`/actions/${taskId.trim()}`);
    }
  };

  return (
    <>
      <Header title="행동 시나리오" subtitle="IF-THEN 규칙 기반 의사결정 지원" />
      <div className="flex-1 flex items-center justify-center bg-[#F3F2F2]">
        <Card className="w-full max-w-md">
          <div className="text-center py-4">
            <div className="w-14 h-14 rounded-full bg-[#FFB75D]/10 flex items-center justify-center mx-auto mb-4">
              <Zap size={28} className="text-[#FFB75D]" />
            </div>
            <h2 className="text-lg font-semibold text-[#16325C] mb-2">
              행동 시나리오
            </h2>
            <p className="text-sm text-[#54698D] mb-6">
              분석 결과를 기반으로 IF-THEN 행동 규칙을 생성합니다.<br />
              우선순위별 카드로 의사결정을 지원합니다.
            </p>
            <div className="flex gap-2">
              <input
                className="flex-1 px-3 py-2.5 border border-gray-300 rounded-lg text-sm text-gray-900 placeholder-gray-400 focus:outline-none focus:border-[#00A1E0] focus:ring-1 focus:ring-[#00A1E0]"
                placeholder="Task ID 입력 (예: task_abc123)"
                value={taskId}
                onChange={(e) => setTaskId(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleGo()}
              />
              <Button onClick={handleGo} disabled={!taskId.trim()}>
                <ArrowRight size={16} />
              </Button>
            </div>
            <p className="text-xs text-[#54698D] mt-4">
              아직 분석을 실행하지 않았나요?{" "}
              <button
                onClick={() => router.push("/analyze")}
                className="text-[#00A1E0] hover:underline"
              >
                분석 시작하기
              </button>
            </p>
          </div>
        </Card>
      </div>
    </>
  );
}
