"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { MessageCircle, ArrowRight } from "react-feather";
import Header from "@/components/layout/Header";
import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";

export default function QAIndexPage() {
  const router = useRouter();
  const [taskId, setTaskId] = useState("");

  const handleGo = () => {
    if (taskId.trim()) {
      router.push(`/qa/${taskId.trim()}`);
    }
  };

  return (
    <>
      <Header title="AI Q&A" subtitle="분석 결과 기반 자연어 질의응답" />
      <div className="flex-1 flex items-center justify-center bg-[#F3F2F2]">
        <Card className="w-full max-w-md">
          <div className="text-center py-4">
            <div className="w-14 h-14 rounded-full bg-[#04844B]/10 flex items-center justify-center mx-auto mb-4">
              <MessageCircle size={28} className="text-[#04844B]" />
            </div>
            <h2 className="text-lg font-semibold text-[#16325C] mb-2">
              AI Q&A
            </h2>
            <p className="text-sm text-[#54698D] mb-6">
              분석 결과에 대해 자연어로 질문하세요.<br />
              &quot;매출에 가장 큰 영향을 미치는 변수는?&quot; 등 자유 질문 가능
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
