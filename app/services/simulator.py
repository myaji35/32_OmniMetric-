"""
What-if Simulator
가상 시나리오 시뮬레이션 서비스
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from loguru import logger

from app.core.storage import TaskStorage


class WhatIfSimulator:
    """What-if 시뮬레이션 엔진"""

    def __init__(self) -> None:
        self.storage = TaskStorage()

    async def simulate(
        self,
        task_id: str,
        scenarios: List[Dict[str, float]],
    ) -> Dict[str, Any]:
        """
        What-if 시뮬레이션 실행

        Args:
            task_id: 원본 분석 작업 ID (모델 로드용)
            scenarios: 시나리오 리스트 [{"var_1": 10, "var_2": 20}, ...]

        Returns:
            시뮬레이션 결과
        """
        logger.info(f"What-if 시뮬레이션 시작: {task_id}, {len(scenarios)}개 시나리오")

        # 1. 저장된 리포트에서 모델 정보 조회
        report = await self.storage.get_report(task_id)
        if not report:
            raise ValueError(f"작업 {task_id}의 리포트를 찾을 수 없습니다.")

        # 2. 모델 계수로 예측 (선형 근사)
        coefficients = report.winner.coefficients
        results = []

        for idx, scenario in enumerate(scenarios):
            prediction = self._predict_from_coefficients(coefficients, scenario)
            results.append({
                "scenario_id": idx + 1,
                "input_values": scenario,
                "predicted_value": prediction,
                "model_used": report.winner.algorithm,
            })

        # 3. 시나리오 비교
        if len(results) > 1:
            best_scenario = max(results, key=lambda x: x["predicted_value"])
            worst_scenario = min(results, key=lambda x: x["predicted_value"])
        else:
            best_scenario = results[0] if results else None
            worst_scenario = results[0] if results else None

        return {
            "task_id": task_id,
            "total_scenarios": len(scenarios),
            "results": results,
            "best_scenario": best_scenario,
            "worst_scenario": worst_scenario,
            "model_info": {
                "algorithm": report.winner.algorithm,
                "r2_score": report.winner.r2_score,
                "formula": report.winner.formula,
            },
        }

    def _predict_from_coefficients(
        self,
        coefficients: Dict[str, float],
        input_values: Dict[str, float],
    ) -> float:
        """계수 기반 예측값 계산"""
        prediction = coefficients.get("intercept", 0.0)

        for feature, value in input_values.items():
            coef = coefficients.get(feature, 0.0)
            prediction += coef * value

        return float(prediction)
