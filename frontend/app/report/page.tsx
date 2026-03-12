"use client";

import Header from "@/components/layout/Header";
import Card from "@/components/ui/Card";
import { FileText } from "react-feather";

export default function ReportIndexPage() {
  return (
    <>
      <Header title="분석 결과" subtitle="Task ID로 접근하세요" />
      <div className="flex-1 flex items-center justify-center bg-[#F3F2F2]">
        <Card>
          <div className="text-center py-8">
            <FileText size={32} className="mx-auto text-[#54698D] mb-3" />
            <p className="text-sm text-[#16325C] font-medium mb-1">분석 결과 조회</p>
            <p className="text-xs text-[#54698D]">
              분석 실행 페이지에서 분석을 시작하거나,<br />
              URL에 Task ID를 입력하세요: /report/[task_id]
            </p>
          </div>
        </Card>
      </div>
    </>
  );
}
