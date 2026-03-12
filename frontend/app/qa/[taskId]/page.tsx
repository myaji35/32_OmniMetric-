"use client";

import { useState, useRef, useEffect } from "react";
import { useParams } from "next/navigation";
import { Send, MessageCircle, User, Cpu } from "react-feather";
import Header from "@/components/layout/Header";
import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";

interface ChatMsg {
  role: "user" | "ai";
  content: string;
}

const SUGGESTED_QUESTIONS = [
  "매출에 가장 큰 영향을 미치는 변수는?",
  "모델의 신뢰도는 어느 정도인가요?",
  "debt를 줄이면 결과가 어떻게 변하나요?",
  "선택된 알고리즘의 장단점은?",
  "데이터에서 이상치가 있나요?",
];

export default function QAPage() {
  const { taskId } = useParams<{ taskId: string }>();
  const [messages, setMessages] = useState<ChatMsg[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async (question?: string) => {
    const q = question || input.trim();
    if (!q) return;
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: q }]);
    setLoading(true);
    try {
      const res = await fetch(`http://localhost:8000/v1/qa/${taskId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: q }),
      });
      const data = await res.json();
      setMessages((prev) => [...prev, { role: "ai", content: data.answer || "답변을 생성할 수 없습니다." }]);
    } catch {
      setMessages((prev) => [...prev, { role: "ai", content: "오류가 발생했습니다. 다시 시도해주세요." }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Header title="AI Q&A" subtitle={`Task: ${taskId}`} />
      <div className="flex-1 flex flex-col bg-[#F3F2F2] overflow-hidden">
        {/* Suggested Questions */}
        {messages.length === 0 && (
          <div className="p-6 pb-0">
            <Card title="추천 질문">
              <div className="flex flex-wrap gap-2">
                {SUGGESTED_QUESTIONS.map((q) => (
                  <button
                    key={q}
                    onClick={() => sendMessage(q)}
                    className="px-3 py-2 rounded-lg border border-gray-200 text-sm text-[#16325C] hover:border-[#00A1E0] hover:bg-[#00A1E0]/5 transition-colors"
                  >
                    {q}
                  </button>
                ))}
              </div>
            </Card>
          </div>
        )}

        {/* Chat Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.map((msg, i) => (
            <div key={i} className={`flex gap-3 ${msg.role === "user" ? "justify-end" : ""}`}>
              {msg.role === "ai" && (
                <div className="w-8 h-8 rounded-full bg-[#00A1E0] flex items-center justify-center flex-shrink-0">
                  <Cpu size={14} className="text-white" />
                </div>
              )}
              <div
                className={`max-w-[70%] rounded-lg px-4 py-3 text-sm leading-relaxed ${
                  msg.role === "user"
                    ? "bg-[#16325C] text-white"
                    : "bg-white border border-gray-200 text-[#16325C]"
                }`}
              >
                {msg.content}
              </div>
              {msg.role === "user" && (
                <div className="w-8 h-8 rounded-full bg-[#54698D] flex items-center justify-center flex-shrink-0">
                  <User size={14} className="text-white" />
                </div>
              )}
            </div>
          ))}
          {loading && (
            <div className="flex gap-3">
              <div className="w-8 h-8 rounded-full bg-[#00A1E0] flex items-center justify-center flex-shrink-0">
                <Cpu size={14} className="text-white" />
              </div>
              <div className="bg-white border border-gray-200 rounded-lg px-4 py-3 text-sm text-[#54698D]">
                답변 생성 중...
              </div>
            </div>
          )}
          <div ref={chatEndRef} />
        </div>

        {/* Input */}
        <div className="p-4 bg-white border-t border-gray-200">
          <div className="flex gap-2">
            <input
              className="flex-1 px-3 py-2.5 border border-gray-300 rounded-lg text-sm text-gray-900 placeholder-gray-400 focus:outline-none focus:border-[#00A1E0] focus:ring-1 focus:ring-[#00A1E0]"
              placeholder="질문을 입력하세요..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && !loading && sendMessage()}
              disabled={loading}
            />
            <Button onClick={() => sendMessage()} disabled={loading || !input.trim()}>
              <Send size={16} />
            </Button>
          </div>
        </div>
      </div>
    </>
  );
}
