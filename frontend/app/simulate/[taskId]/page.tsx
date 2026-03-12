"use client";

import { useState } from "react";
import { useParams } from "next/navigation";
import { Sliders, Play, RotateCcw } from "react-feather";
import Header from "@/components/layout/Header";
import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";

interface Scenario {
  variables: Record<string, number>;
  predicted?: number;
}

export default function SimulatePage() {
  const { taskId } = useParams<{ taskId: string }>();
  const [variables, setVariables] = useState<Record<string, number>>({});
  const [varInput, setVarInput] = useState("");
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [baseline, setBaseline] = useState<number | null>(null);

  const addVariable = () => {
    if (!varInput.trim()) return;
    setVariables({ ...variables, [varInput.trim()]: 0 });
    setVarInput("");
  };

  const runSimulation = async () => {
    try {
      const res = await fetch("http://localhost:8000/v1/simulate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          task_id: taskId,
          scenarios: [variables],
        }),
      });
      const data = await res.json();
      const pred = data.predictions?.[0]?.predicted_value;
      if (scenarios.length === 0 && pred != null) setBaseline(pred);
      setScenarios([...scenarios, { variables: { ...variables }, predicted: pred }]);
    } catch {
      alert("시뮬레이션 실패");
    }
  };

  return (
    <>
      <Header title="What-if 시뮬레이션" subtitle={`Task: ${taskId}`} />
      <div className="flex-1 overflow-y-auto p-6 bg-[#F3F2F2] space-y-4">
        {/* Variable Controls */}
        <Card title="변수 조절" actions={<Sliders size={16} className="text-[#54698D]" />}>
          <div className="flex gap-2 mb-4">
            <input
              className="flex-1 px-3 py-2.5 border border-gray-300 rounded-lg text-sm text-gray-900 placeholder-gray-400 focus:outline-none focus:border-[#00A1E0] focus:ring-1 focus:ring-[#00A1E0]"
              placeholder="변수명 입력 (예: income)"
              value={varInput}
              onChange={(e) => setVarInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && addVariable()}
            />
            <Button onClick={addVariable} variant="secondary">추가</Button>
          </div>
          <div className="space-y-4">
            {Object.entries(variables).map(([name, value]) => (
              <div key={name} className="flex items-center gap-4">
                <span className="w-24 text-sm font-medium text-[#16325C]">{name}</span>
                <input
                  type="range"
                  min={-100}
                  max={100}
                  value={value}
                  onChange={(e) =>
                    setVariables({ ...variables, [name]: Number(e.target.value) })
                  }
                  className="flex-1"
                />
                <input
                  type="number"
                  value={value}
                  onChange={(e) =>
                    setVariables({ ...variables, [name]: Number(e.target.value) })
                  }
                  className="w-24 px-3 py-2 border border-gray-300 rounded-lg text-sm text-gray-900 text-right focus:outline-none focus:border-[#00A1E0] focus:ring-1 focus:ring-[#00A1E0]"
                />
              </div>
            ))}
          </div>
          {Object.keys(variables).length > 0 && (
            <div className="flex gap-2 mt-4">
              <Button onClick={runSimulation}>
                <span className="flex items-center gap-1.5"><Play size={14} /> 시뮬레이션 실행</span>
              </Button>
              <Button
                variant="secondary"
                onClick={() => {
                  const reset = { ...variables };
                  Object.keys(reset).forEach((k) => (reset[k] = 0));
                  setVariables(reset);
                }}
              >
                <span className="flex items-center gap-1.5"><RotateCcw size={14} /> 리셋</span>
              </Button>
            </div>
          )}
        </Card>

        {/* Scenario Compare */}
        {scenarios.length > 0 && (
          <Card title="시나리오 비교">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="bg-gray-50">
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase">변수</th>
                    {scenarios.map((_, i) => (
                      <th key={i} className="px-4 py-3 text-right text-xs font-semibold text-gray-500 uppercase">
                        시나리오 {i + 1}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {Object.keys(variables).map((name) => (
                    <tr key={name} className="border-t border-gray-100">
                      <td className="px-4 py-2 font-medium text-[#16325C]">{name}</td>
                      {scenarios.map((s, i) => (
                        <td key={i} className="px-4 py-2 text-right font-mono">{s.variables[name] ?? 0}</td>
                      ))}
                    </tr>
                  ))}
                  <tr className="border-t-2 border-gray-300 bg-[#00A1E0]/5">
                    <td className="px-4 py-3 font-semibold text-[#16325C]">예측 Y</td>
                    {scenarios.map((s, i) => (
                      <td key={i} className="px-4 py-3 text-right font-mono font-bold text-[#00A1E0]">
                        {s.predicted?.toFixed(4) ?? "-"}
                      </td>
                    ))}
                  </tr>
                  {baseline != null && (
                    <tr className="border-t border-gray-100">
                      <td className="px-4 py-2 text-[#54698D]">변화율</td>
                      {scenarios.map((s, i) => (
                        <td key={i} className="px-4 py-2 text-right font-mono text-xs">
                          {s.predicted != null && baseline
                            ? `${(((s.predicted - baseline) / baseline) * 100).toFixed(1)}%`
                            : "-"}
                        </td>
                      ))}
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </Card>
        )}
      </div>
    </>
  );
}
