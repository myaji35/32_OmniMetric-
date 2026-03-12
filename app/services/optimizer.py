"""
Goal Optimizer
목표 달성 최적화 서비스 (제약조건 기반)
"""
import numpy as np
from typing import Dict, Any, List, Optional
from scipy.optimize import minimize
from loguru import logger

from app.core.storage import TaskStorage


class GoalOptimizer:
    """목표 달성 최적화 엔진"""

    def __init__(self) -> None:
        self.storage = TaskStorage()

    async def optimize(
        self,
        task_id: str,
        target_value: float,
        constraints: Dict[str, Dict[str, float]],
        maximize: bool = True,
    ) -> Dict[str, Any]:
        """
        목표 달성을 위한 최적 변수 조합 탐색

        Args:
            task_id: 원본 분석 작업 ID
            target_value: 목표 Y 값
            constraints: {"var_1": {"min": 0, "max": 100}, ...}
            maximize: True=최대화, False=목표값 근사

        Returns:
            최적화 결과
        """
        logger.info(f"최적화 시작: task={task_id}, target={target_value}")

        # 1. 저장된 리포트에서 모델 정보
        report = await self.storage.get_report(task_id)
        if not report:
            raise ValueError(f"작업 {task_id}의 리포트를 찾을 수 없습니다.")

        coefficients = report.winner.coefficients
        feature_names = [k for k in coefficients if k != "intercept"]

        # 2. 제약조건 설정
        bounds = []
        for feature in feature_names:
            if feature in constraints:
                bounds.append((
                    constraints[feature].get("min", -1e6),
                    constraints[feature].get("max", 1e6),
                ))
            else:
                bounds.append((-1e6, 1e6))

        # 3. 목적함수 정의
        intercept = coefficients.get("intercept", 0.0)
        coef_values = [coefficients.get(f, 0.0) for f in feature_names]

        if maximize:
            # 최대화: 음수 반환하여 minimize로 최대화
            def objective(x: np.ndarray) -> float:
                return -(np.dot(coef_values, x) + intercept)
        else:
            # 목표값 근사: 목표와의 차이 최소화
            def objective(x: np.ndarray) -> float:
                pred = np.dot(coef_values, x) + intercept
                return (pred - target_value) ** 2

        # 4. 초기값 (제약조건 중간값)
        x0 = np.array([
            (b[0] + b[1]) / 2 if abs(b[0]) < 1e5 and abs(b[1]) < 1e5 else 0.0
            for b in bounds
        ])

        # 5. 최적화 실행
        result = minimize(
            objective,
            x0,
            method="L-BFGS-B",
            bounds=bounds,
            options={"maxiter": 1000},
        )

        # 6. 결과 정리
        optimal_values = {
            feature: float(val) for feature, val in zip(feature_names, result.x)
        }
        predicted_y = float(np.dot(coef_values, result.x) + intercept)

        return {
            "task_id": task_id,
            "target_value": target_value,
            "maximize": maximize,
            "optimal_variables": optimal_values,
            "predicted_outcome": predicted_y,
            "optimization_success": bool(result.success),
            "optimization_message": result.message if hasattr(result, "message") else "",
            "model_info": {
                "algorithm": report.winner.algorithm,
                "r2_score": report.winner.r2_score,
            },
            "constraints_applied": constraints,
        }
