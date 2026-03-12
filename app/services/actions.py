"""
Action Scenario Converter
분석 결과를 즉시 실행 가능한 행동 시나리오(IF-THEN 규칙)로 변환
"""
from typing import Dict, Any, List
from datetime import datetime
from loguru import logger

from app.core.storage import TaskStorage


class ActionScenarioConverter:
    """행동 시나리오 변환 엔진"""

    def __init__(self) -> None:
        self.storage = TaskStorage()

    async def generate_scenarios(
        self,
        task_id: str,
        thresholds: Dict[str, float] | None = None,
    ) -> Dict[str, Any]:
        """
        분석 결과를 행동 시나리오로 변환

        Args:
            task_id: 원본 분석 작업 ID
            thresholds: 사용자 지정 임계값 {"variable": threshold_value}

        Returns:
            행동 시나리오 목록
        """
        logger.info(f"행동 시나리오 생성: {task_id}")

        # 1. 리포트 조회
        report = await self.storage.get_report(task_id)
        if not report:
            raise ValueError(f"작업 {task_id}의 리포트를 찾을 수 없습니다.")

        # 2. 변수 중요도 기반 시나리오 생성
        scenarios = []
        feature_importance = report.winner.feature_importance
        coefficients = report.winner.coefficients

        for feature, importance in feature_importance.items():
            if importance < 1.0:  # 1% 미만 영향력은 무시
                continue

            coef = coefficients.get(feature, 0.0)
            direction = "증가" if coef > 0 else "감소"
            action_direction = "증가" if coef > 0 else "감소"

            # IF-THEN 규칙 생성
            scenario = {
                "rule_id": f"RULE_{feature.upper()}",
                "condition": f"IF {feature}이(가) 10% {direction}하면",
                "action": f"THEN 목표값이 약 {abs(coef * 0.1):.4f}만큼 {action_direction}",
                "impact_score": round(importance, 2),
                "priority": self._calculate_priority(importance, abs(coef)),
                "variable": feature,
                "coefficient": coef,
                "importance_pct": importance,
                "created_at": datetime.now().isoformat(),
            }

            # 사용자 임계값 적용
            if thresholds and feature in thresholds:
                threshold = thresholds[feature]
                scenario["threshold"] = threshold
                scenario["trigger_condition"] = (
                    f"{feature} > {threshold}" if coef > 0
                    else f"{feature} < {threshold}"
                )

            scenarios.append(scenario)

        # 3. 우선순위 순 정렬
        scenarios.sort(key=lambda x: x["priority"], reverse=True)

        return {
            "task_id": task_id,
            "model": report.winner.algorithm,
            "total_scenarios": len(scenarios),
            "scenarios": scenarios,
            "generated_at": datetime.now().isoformat(),
        }

    def _calculate_priority(self, importance: float, abs_coefficient: float) -> float:
        """우선순위 산정 (Impact x Probability 근사)"""
        # importance: 영향도 (0~100), abs_coefficient: 계수 절대값
        return round(importance * min(abs_coefficient, 10.0) / 10.0, 2)
