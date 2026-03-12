"""
Action Scenario Converter
분석 결과를 즉시 실행 가능한 행동 시나리오(IF-THEN 규칙)로 변환
"""
import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
from loguru import logger
import httpx

from app.core.storage import TaskStorage


# 시나리오 이력 저장 경로
SCENARIO_STORE_PATH = Path(
    os.environ.get("OMNIMETRIC_SCENARIO_STORE", "data/scenarios.json")
)


class ActionScenarioConverter:
    """행동 시나리오 변환 엔진"""

    def __init__(self) -> None:
        self.storage = TaskStorage()
        self._history: Dict[str, List[Dict[str, Any]]] = {}
        self._load_history()

    def _load_history(self) -> None:
        """시나리오 이력 로드"""
        if SCENARIO_STORE_PATH.exists():
            try:
                with open(SCENARIO_STORE_PATH, "r", encoding="utf-8") as f:
                    self._history = json.load(f)
            except (json.JSONDecodeError, OSError):
                self._history = {}

    def _save_history(self) -> None:
        """시나리오 이력 저장"""
        SCENARIO_STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(SCENARIO_STORE_PATH, "w", encoding="utf-8") as f:
            json.dump(self._history, f, ensure_ascii=False, indent=2)

    def get_history(self, task_id: str) -> List[Dict[str, Any]]:
        """시나리오 이력 조회"""
        return self._history.get(task_id, [])

    async def send_webhook(
        self,
        webhook_url: str,
        scenarios: Dict[str, Any],
    ) -> bool:
        """
        행동 시나리오를 외부 Webhook으로 전달

        Args:
            webhook_url: Webhook URL
            scenarios: 시나리오 데이터

        Returns:
            전송 성공 여부
        """
        logger.info(f"행동 시나리오 Webhook 전송: {webhook_url}")
        payload = {
            "event": "action_scenarios_generated",
            "task_id": scenarios.get("task_id"),
            "total_scenarios": scenarios.get("total_scenarios"),
            "top_scenarios": scenarios.get("scenarios", [])[:5],
            "generated_at": scenarios.get("generated_at"),
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    webhook_url,
                    json=payload,
                    headers={
                        "Content-Type": "application/json",
                        "X-OmniMetric-Event": "action_scenarios_generated",
                    },
                )
                success = response.status_code in [200, 201, 202, 204]
                if success:
                    logger.info(f"시나리오 Webhook 전송 성공: {response.status_code}")
                else:
                    logger.warning(f"시나리오 Webhook 응답 오류: {response.status_code}")
                return success
        except Exception as e:
            logger.error(f"시나리오 Webhook 전송 실패: {e}")
            return False

    async def generate_scenarios(
        self,
        task_id: str,
        thresholds: Dict[str, float] | None = None,
        webhook_url: Optional[str] = None,
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

        result = {
            "task_id": task_id,
            "model": report.winner.algorithm,
            "total_scenarios": len(scenarios),
            "scenarios": scenarios,
            "generated_at": datetime.now().isoformat(),
        }

        # 4. 이력 저장
        if task_id not in self._history:
            self._history[task_id] = []
        self._history[task_id].append({
            "generated_at": result["generated_at"],
            "total_scenarios": result["total_scenarios"],
            "top_rule": scenarios[0]["rule_id"] if scenarios else None,
        })
        self._save_history()

        # 5. Webhook 전달 (URL 지정 시)
        if webhook_url:
            await self.send_webhook(webhook_url, result)

        return result

    def _calculate_priority(self, importance: float, abs_coefficient: float) -> float:
        """우선순위 산정 (Impact x Probability 근사)"""
        # importance: 영향도 (0~100), abs_coefficient: 계수 절대값
        return round(importance * min(abs_coefficient, 10.0) / 10.0, 2)
