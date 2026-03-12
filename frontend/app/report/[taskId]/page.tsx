"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { Award, Hash, BarChart2, List, Eye, FileText, ArrowRight } from "react-feather";
import Header from "@/components/layout/Header";
import Card from "@/components/ui/Card";
import Badge from "@/components/ui/Badge";
import Button from "@/components/ui/Button";

interface AlgoResult {
  name: string;
  r2_score: number;
  adj_r2_score: number | null;
  p_value: number | null;
  execution_time: number;
}

interface Winner {
  algorithm: string;
  r2_score: number;
  adj_r2_score: number | null;
  formula: string;
  coefficients: Record<string, number>;
  feature_importance: Record<string, number>;
}

interface XAI {
  shap_values: Record<string, number> | null;
  lime_explanation: string | null;
  top_features: string[];
}

interface NLG {
  summary: string;
  key_findings: string[];
  variable_impacts: string[];
  selection_reason: string;
}

interface Report {
  task_id: string;
  status: string;
  total_algorithms_tested: number;
  tournament_duration: number;
  top_5_algorithms: AlgoResult[];
  winner: Winner;
  xai_insights: XAI | null;
  report: NLG;
  data_shape: [number, number];
}

export default function ReportPage() {
  const { taskId } = useParams<{ taskId: string }>();
  const router = useRouter();
  const [report, setReport] = useState<Report | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch(`http://localhost:8000/v1/report/${taskId}`)
      .then((r) => {
        if (!r.ok) throw new Error("리포트를 불러올 수 없습니다");
        return r.json();
      })
      .then(setReport)
      .catch((e) => setError(e.message));
  }, [taskId]);

  if (error) {
    return (
      <>
        <Header title="분석 결과" subtitle={taskId} />
        <div className="flex-1 flex items-center justify-center bg-[#F3F2F2]">
          <Card><p className="text-[#C23934] text-sm">{error}</p></Card>
        </div>
      </>
    );
  }

  if (!report) {
    return (
      <>
        <Header title="분석 결과" subtitle={taskId} />
        <div className="flex-1 flex items-center justify-center bg-[#F3F2F2]">
          <p className="text-[#54698D] text-sm">로딩 중...</p>
        </div>
      </>
    );
  }

  const { winner, xai_insights, report: nlg, top_5_algorithms } = report;
  const importance = Object.entries(winner.feature_importance).sort(
    ([, a], [, b]) => Math.abs(b) - Math.abs(a)
  );
  const maxImportance = Math.max(...importance.map(([, v]) => Math.abs(v)));
  const coefficients = Object.entries(winner.coefficients);

  return (
    <>
      <Header title="분석 결과 & 근거" subtitle={`Task: ${taskId}`} />
      <div className="flex-1 overflow-y-auto p-6 bg-[#F3F2F2] space-y-4">
        {/* Winner Card */}
        <div className="bg-gradient-to-r from-[#16325C] to-[#00A1E0] rounded-lg p-6 text-white">
          <div className="flex items-center gap-3 mb-3">
            <Award size={24} className="text-[#FFB75D]" />
            <h2 className="text-xl font-bold">승자 알고리즘</h2>
          </div>
          <p className="text-2xl font-bold mb-2">{winner.algorithm}</p>
          <div className="flex gap-6 text-sm">
            <div>
              <span className="text-white/65">R²</span>
              <p className="text-lg font-bold">{winner.r2_score.toFixed(4)}</p>
            </div>
            {winner.adj_r2_score != null && (
              <div>
                <span className="text-white/65">Adj. R²</span>
                <p className="text-lg font-bold">{winner.adj_r2_score.toFixed(4)}</p>
              </div>
            )}
            <div>
              <span className="text-white/65">테스트 알고리즘</span>
              <p className="text-lg font-bold">{report.total_algorithms_tested}개</p>
            </div>
            <div>
              <span className="text-white/65">소요 시간</span>
              <p className="text-lg font-bold">{report.tournament_duration.toFixed(1)}s</p>
            </div>
            <div>
              <span className="text-white/65">데이터</span>
              <p className="text-lg font-bold">{report.data_shape[0]}행 x {report.data_shape[1]}열</p>
            </div>
          </div>
        </div>

        {/* Formula */}
        <Card title="수학적 공식" actions={<Hash size={16} className="text-[#54698D]" />}>
          <div className="bg-gray-50 rounded-lg p-4 mb-4 font-mono text-sm text-[#16325C] overflow-x-auto">
            {winner.formula}
          </div>
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-50">
                <th className="px-4 py-2 text-left text-xs font-semibold text-gray-500 uppercase">변수</th>
                <th className="px-4 py-2 text-right text-xs font-semibold text-gray-500 uppercase">계수</th>
                <th className="px-4 py-2 text-center text-xs font-semibold text-gray-500 uppercase">방향</th>
              </tr>
            </thead>
            <tbody>
              {coefficients.map(([name, value]) => (
                <tr key={name} className="border-t border-gray-100">
                  <td className="px-4 py-2 font-medium text-[#16325C]">{name}</td>
                  <td className="px-4 py-2 text-right font-mono">
                    {value >= 0 ? "+" : ""}{value.toFixed(4)}
                  </td>
                  <td className="px-4 py-2 text-center">
                    {name === "intercept" ? (
                      <span className="text-[#54698D]">절편</span>
                    ) : value >= 0 ? (
                      <Badge label="양(+)" color="#04844B" />
                    ) : (
                      <Badge label="음(-)" color="#C23934" />
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>

        {/* Feature Importance */}
        <Card title="변수 기여도" actions={<BarChart2 size={16} className="text-[#54698D]" />}>
          <div className="space-y-3">
            {importance.map(([name, value]) => {
              const pct = Math.abs(value);
              const width = (pct / maxImportance) * 100;
              const isPositive = value >= 0;
              return (
                <div key={name} className="flex items-center gap-3">
                  <span className="w-24 text-sm text-[#16325C] font-medium truncate">{name}</span>
                  <div className="flex-1 h-7 bg-gray-100 rounded-lg overflow-hidden relative">
                    <div
                      className="h-full rounded-lg transition-all duration-500"
                      style={{
                        width: `${width}%`,
                        background: isPositive ? "#00A1E0" : "#C23934",
                      }}
                    />
                  </div>
                  <span className="w-16 text-right text-sm font-mono">
                    {pct.toFixed(1)}%
                  </span>
                  <Badge
                    label={isPositive ? "+" : "-"}
                    color={isPositive ? "#04844B" : "#C23934"}
                  />
                </div>
              );
            })}
          </div>
        </Card>

        {/* Tournament Ranking */}
        <Card title="알고리즘 토너먼트 랭킹" actions={<List size={16} className="text-[#54698D]" />}>
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-50">
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase">#</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase">알고리즘</th>
                <th className="px-4 py-3 text-right text-xs font-semibold text-gray-500 uppercase">R²</th>
                <th className="px-4 py-3 text-right text-xs font-semibold text-gray-500 uppercase">Adj. R²</th>
                <th className="px-4 py-3 text-right text-xs font-semibold text-gray-500 uppercase">P-value</th>
                <th className="px-4 py-3 text-right text-xs font-semibold text-gray-500 uppercase">시간</th>
              </tr>
            </thead>
            <tbody>
              {top_5_algorithms.map((algo, i) => (
                <tr key={algo.name} className={`border-t border-gray-100 ${i === 0 ? "bg-[#00A1E0]/5" : ""}`}>
                  <td className="px-4 py-3 font-medium">
                    {i === 0 ? <Award size={16} className="text-[#FFB75D]" /> : i + 1}
                  </td>
                  <td className="px-4 py-3 font-medium text-[#16325C]">{algo.name}</td>
                  <td className="px-4 py-3 text-right font-mono">{algo.r2_score.toFixed(4)}</td>
                  <td className="px-4 py-3 text-right font-mono">{algo.adj_r2_score?.toFixed(4) ?? "-"}</td>
                  <td className="px-4 py-3 text-right font-mono">
                    {algo.p_value !== null ? (algo.p_value < 0.001 ? "<0.001" : algo.p_value.toFixed(3)) : "-"}
                  </td>
                  <td className="px-4 py-3 text-right text-[#54698D]">{algo.execution_time.toFixed(2)}s</td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>

        {/* XAI Insights */}
        {xai_insights && (
          <Card title="XAI 해석 (SHAP/LIME)" actions={<Eye size={16} className="text-[#54698D]" />}>
            {xai_insights.top_features?.length > 0 && (
              <div className="mb-4">
                <p className="text-xs font-semibold text-gray-600 mb-2">상위 영향 변수</p>
                <div className="flex gap-2 flex-wrap">
                  {xai_insights.top_features.map((f) => (
                    <Badge key={f} label={f} color="#00A1E0" />
                  ))}
                </div>
              </div>
            )}
            {xai_insights.shap_values && (
              <div className="mb-4">
                <p className="text-xs font-semibold text-gray-600 mb-2">SHAP Values</p>
                <div className="space-y-2">
                  {Object.entries(xai_insights.shap_values)
                    .sort(([, a], [, b]) => Math.abs(b) - Math.abs(a))
                    .map(([name, value]) => (
                      <div key={name} className="flex items-center gap-3 text-sm">
                        <span className="w-24 text-[#16325C] font-medium">{name}</span>
                        <div className="flex-1 h-5 bg-gray-100 rounded overflow-hidden">
                          <div
                            className="h-full rounded"
                            style={{
                              width: `${Math.min(Math.abs(value) * 200, 100)}%`,
                              background: value >= 0 ? "#00A1E0" : "#C23934",
                            }}
                          />
                        </div>
                        <span className="font-mono text-xs w-14 text-right">
                          {value >= 0 ? "+" : ""}{value.toFixed(3)}
                        </span>
                      </div>
                    ))}
                </div>
              </div>
            )}
            {xai_insights.lime_explanation && (
              <div className="bg-gray-50 rounded-lg p-4 text-sm text-[#16325C]">
                <p className="text-xs font-semibold text-gray-600 mb-1">LIME 설명</p>
                {xai_insights.lime_explanation}
              </div>
            )}
          </Card>
        )}

        {/* NLG Report */}
        <Card title="Sim4Brief 자연어 리포트" actions={<FileText size={16} className="text-[#54698D]" />}>
          <div className="space-y-4 text-sm text-[#16325C]">
            <div>
              <p className="text-xs font-semibold text-gray-600 mb-1">분석 요약</p>
              <p className="leading-relaxed">{nlg.summary}</p>
            </div>
            <div>
              <p className="text-xs font-semibold text-gray-600 mb-1">핵심 발견</p>
              <ul className="list-disc pl-5 space-y-1">
                {nlg.key_findings.map((f, i) => (
                  <li key={i}>{f}</li>
                ))}
              </ul>
            </div>
            <div>
              <p className="text-xs font-semibold text-gray-600 mb-1">변수별 영향</p>
              <ul className="list-disc pl-5 space-y-1">
                {nlg.variable_impacts.map((v, i) => (
                  <li key={i}>{v}</li>
                ))}
              </ul>
            </div>
            <div className="bg-[#00A1E0]/5 border border-[#00A1E0]/20 rounded-lg p-4">
              <p className="text-xs font-semibold text-[#00A1E0] mb-1">모델 선정 사유</p>
              <p className="leading-relaxed">{nlg.selection_reason}</p>
            </div>
          </div>
        </Card>

        {/* Action Buttons */}
        <div className="flex gap-3 justify-end">
          <Button variant="secondary" onClick={() => router.push(`/simulate/${taskId}`)}>
            <span className="flex items-center gap-1.5">시뮬레이션 <ArrowRight size={14} /></span>
          </Button>
          <Button variant="secondary" onClick={() => router.push(`/actions/${taskId}`)}>
            <span className="flex items-center gap-1.5">행동 시나리오 <ArrowRight size={14} /></span>
          </Button>
          <Button onClick={() => router.push(`/qa/${taskId}`)}>
            <span className="flex items-center gap-1.5">AI Q&A <ArrowRight size={14} /></span>
          </Button>
        </div>
      </div>
    </>
  );
}
