"""
MLOps Service
자가 보정 및 모델 재학습 파이프라인
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from loguru import logger

from app.core.config import settings
from app.core.storage import TaskStorage


class MLOpsEngine:
    """MLOps 자가 보정 엔진"""

    def __init__(self):
        self.error_threshold = settings.mlops_error_threshold
        self.min_r2_score = settings.mlops_min_r2_score
        self.auto_retrain = settings.mlops_auto_retrain
        self.retrain_cooldown = settings.mlops_retrain_cooldown
        self.storage = TaskStorage()

    async def monitor_model_performance(
        self,
        task_id: str,
        model: Any,
        X_new: pd.DataFrame,
        y_true: pd.Series
    ) -> Dict[str, Any]:
        """
        모델 성능 모니터링

        Args:
            task_id: 원본 작업 ID
            model: 배포된 모델
            X_new: 새로운 데이터
            y_true: 실제 값

        Returns:
            모니터링 결과
        """
        logger.info(f"📊 모델 성능 모니터링 시작: {task_id}")

        try:
            # 예측
            y_pred = model.predict(X_new)

            # 오차 계산
            error_metrics = self._calculate_error_metrics(y_true, y_pred)

            # 성능 저하 감지
            needs_retrain = self._check_retrain_trigger(error_metrics)

            # 결과 저장
            monitoring_result = {
                "task_id": task_id,
                "timestamp": datetime.now().isoformat(),
                "metrics": error_metrics,
                "needs_retrain": needs_retrain,
                "threshold_exceeded": error_metrics["mape"] > self.error_threshold,
                "action_taken": None
            }

            # 재학습 트리거
            if needs_retrain and self.auto_retrain:
                retrain_eligible = await self._check_retrain_cooldown(task_id)

                if retrain_eligible:
                    logger.warning(f"⚠️ 재학습 트리거: 오차율 {error_metrics['mape']:.2%} > 임계값 {self.error_threshold:.2%}")
                    monitoring_result["action_taken"] = "retrain_scheduled"
                    # Phase 4에서 실제 재학습 로직 구현
                else:
                    logger.info(f"재학습 쿨다운 중: {task_id}")
                    monitoring_result["action_taken"] = "cooldown"

            logger.info(f"✅ 모니터링 완료: MAPE={error_metrics['mape']:.4f}")
            return monitoring_result

        except Exception as e:
            logger.error(f"❌ 모니터링 실패: {str(e)}")
            raise

    def _calculate_error_metrics(
        self,
        y_true: pd.Series,
        y_pred: np.ndarray
    ) -> Dict[str, float]:
        """
        오차 지표 계산

        Args:
            y_true: 실제 값
            y_pred: 예측 값

        Returns:
            오차 지표 딕셔너리
        """
        from sklearn.metrics import (
            mean_absolute_error,
            mean_squared_error,
            r2_score
        )

        mae = mean_absolute_error(y_true, y_pred)
        mse = mean_squared_error(y_true, y_pred)
        rmse = np.sqrt(mse)
        r2 = r2_score(y_true, y_pred)

        # MAPE (Mean Absolute Percentage Error)
        # 0으로 나누기 방지
        mask = y_true != 0
        if mask.sum() > 0:
            mape = np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask]))
        else:
            mape = float('inf')

        return {
            "mae": float(mae),
            "mse": float(mse),
            "rmse": float(rmse),
            "r2_score": float(r2),
            "mape": float(mape)
        }

    def _check_retrain_trigger(self, error_metrics: Dict[str, float]) -> bool:
        """
        재학습 필요 여부 판단

        Args:
            error_metrics: 오차 지표

        Returns:
            재학습 필요 여부
        """
        # 조건 1: MAPE가 임계값 초과
        mape_exceeded = error_metrics["mape"] > self.error_threshold

        # 조건 2: R² 점수가 최소 요구사항 미달
        r2_below_threshold = error_metrics["r2_score"] < self.min_r2_score

        return mape_exceeded or r2_below_threshold

    async def _check_retrain_cooldown(self, task_id: str) -> bool:
        """
        재학습 쿨다운 확인

        Args:
            task_id: 작업 ID

        Returns:
            재학습 가능 여부
        """
        if not self.storage.redis_client:
            await self.storage.connect()

        # 마지막 재학습 시간 조회
        last_retrain_key = f"task:{task_id}:last_retrain"
        last_retrain = await self.storage.redis_client.get(last_retrain_key)

        if not last_retrain:
            return True

        # 쿨다운 시간 계산
        last_retrain_time = datetime.fromisoformat(last_retrain)
        elapsed = (datetime.now() - last_retrain_time).total_seconds()

        return elapsed >= self.retrain_cooldown

    async def trigger_retrain(
        self,
        task_id: str,
        X_new: pd.DataFrame,
        y_new: pd.Series
    ) -> str:
        """
        재학습 트리거

        Args:
            task_id: 원본 작업 ID
            X_new: 새로운 학습 데이터
            y_new: 새로운 타겟 데이터

        Returns:
            새로운 작업 ID
        """
        logger.info(f"🔄 재학습 시작: {task_id}")

        # 새로운 작업 ID 생성
        from uuid import uuid4
        new_task_id = f"{task_id}_retrain_{uuid4().hex[:8]}"

        # 재학습 시간 기록
        if not self.storage.redis_client:
            await self.storage.connect()

        last_retrain_key = f"task:{task_id}:last_retrain"
        await self.storage.redis_client.set(
            last_retrain_key,
            datetime.now().isoformat(),
            ex=self.retrain_cooldown * 2  # 쿨다운의 2배 동안 보관
        )

        logger.info(f"✅ 재학습 작업 생성: {new_task_id}")

        # Phase 4에서 실제 토너먼트 재실행 로직 구현
        return new_task_id

    def get_drift_analysis(
        self,
        X_train: pd.DataFrame,
        X_new: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        데이터 드리프트 분석

        Args:
            X_train: 학습 데이터
            X_new: 새로운 데이터

        Returns:
            드리프트 분석 결과
        """
        logger.info("📈 데이터 드리프트 분석 시작")

        drift_report = {
            "features_with_drift": [],
            "drift_scores": {},
            "summary": ""
        }

        try:
            for column in X_train.columns:
                # 분포 비교 (간단한 통계적 차이)
                train_mean = X_train[column].mean()
                train_std = X_train[column].std()
                new_mean = X_new[column].mean()
                new_std = X_new[column].std()

                # 표준화된 차이 계산
                if train_std > 0:
                    mean_drift = abs(new_mean - train_mean) / train_std
                    drift_report["drift_scores"][column] = float(mean_drift)

                    # 드리프트 임계값 (2 표준편차)
                    if mean_drift > 2.0:
                        drift_report["features_with_drift"].append(column)

            # 요약
            drift_count = len(drift_report["features_with_drift"])
            total_features = len(X_train.columns)

            drift_report["summary"] = (
                f"{total_features}개 특성 중 {drift_count}개에서 "
                f"유의미한 데이터 드리프트 감지됨"
            )

            logger.info(f"✅ 드리프트 분석 완료: {drift_count}/{total_features} 특성")

        except Exception as e:
            logger.error(f"❌ 드리프트 분석 실패: {str(e)}")

        return drift_report

    async def update_threshold(
        self,
        error_threshold: Optional[float] = None,
        min_r2_score: Optional[float] = None
    ) -> Dict[str, float]:
        """
        임계값 동적 업데이트

        Args:
            error_threshold: 새로운 오차 임계값
            min_r2_score: 새로운 최소 R² 점수

        Returns:
            업데이트된 임계값
        """
        if error_threshold is not None:
            self.error_threshold = error_threshold
            logger.info(f"오차 임계값 업데이트: {error_threshold:.2%}")

        if min_r2_score is not None:
            self.min_r2_score = min_r2_score
            logger.info(f"최소 R² 점수 업데이트: {min_r2_score:.4f}")

        return {
            "error_threshold": self.error_threshold,
            "min_r2_score": self.min_r2_score
        }
