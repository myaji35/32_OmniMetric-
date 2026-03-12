"""
Tournament Engine (Orchestrator)
토너먼트 오케스트레이터 - 전체 분석 파이프라인 조율
(SRP 리팩토링: prepare_data -> DataPreprocessor, NLG -> NLGReportGenerator)
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List
from datetime import datetime
from loguru import logger

from app.core.parallel import ParallelTournament
from app.core.preprocessor import DataPreprocessor
from app.models.algorithms.registry import AlgorithmRegistry
from app.core.storage import TaskStorage
from app.services.xai import XAIEngine
from app.services.nlg import NLGReportGenerator
from app.services.webhook import get_webhook_service
from app.security.ssrf_guard import validate_webhook_url
from app.security.input_validator import validate_analyze_input
from app.models.schemas import (
    AnalyzeRequest,
    ReportResponse,
    AlgorithmResult,
    WinnerModel,
    NaturalLanguageReport,
    XAIInsights,
)


class TournamentEngine:
    """
    알고리즘 토너먼트 오케스트레이터
    데이터 전처리부터 최종 리포트 생성까지 전 과정 조율
    """

    def __init__(self) -> None:
        self.parallel_tournament = ParallelTournament()
        self.algorithm_registry = AlgorithmRegistry()
        self.storage = TaskStorage()
        self.xai_engine = XAIEngine()
        self.webhook_service = get_webhook_service()
        self.preprocessor = DataPreprocessor()
        self.nlg = NLGReportGenerator()

    def prepare_data(
        self,
        request: AnalyzeRequest,
    ) -> tuple[pd.DataFrame, pd.Series]:
        """데이터 전처리 (하위 호환성 유지)"""
        return self.preprocessor.prepare_data(request)

    async def run_tournament(
        self,
        task_id: str,
        request: AnalyzeRequest,
    ) -> None:
        """
        토너먼트 실행 (비동기 백그라운드 작업)

        Args:
            task_id: 작업 ID
            request: 분석 요청
        """
        try:
            logger.info(f"작업 {task_id} 시작")

            # 0. 입력 검증
            validate_analyze_input(request.data)
            if request.webhook_url:
                validate_webhook_url(request.webhook_url)

            # 상태 업데이트: processing
            await self.storage.update_task_status(task_id, "processing", 10)

            # 1. 데이터 전처리
            X, y = self.preprocessor.prepare_data(request)
            await self.storage.update_task_status(task_id, "processing", 20)

            # 2. 알고리즘 로드
            algorithms = self.algorithm_registry.get_all_algorithms(request.task_type)
            logger.info(f"로드된 알고리즘: {len(algorithms)}개 ({request.task_type})")
            await self.storage.update_task_status(task_id, "processing", 30)

            # 3. 병렬 토너먼트 실행
            results = self.parallel_tournament.run_tournament(algorithms, X, y)
            await self.storage.update_task_status(task_id, "processing", 70)

            # 4. 승자 선정
            winner = self.parallel_tournament.get_winner(results)
            top_5 = self.parallel_tournament.get_top_performers(results, top_n=5)

            # 5. 공식 및 중요도 추출
            formula = self.nlg.extract_formula(winner, list(X.columns))
            feature_importance = self.nlg.calculate_feature_importance(
                winner, list(X.columns)
            )
            await self.storage.update_task_status(task_id, "processing", 75)

            # 6. XAI 분석 (선택적)
            xai_insights = None
            if request.enable_xai:
                logger.info("XAI 분석 시작")
                xai_result = self.xai_engine.explain_model(
                    model=winner.get("model"),
                    X=X,
                    y=y,
                    algorithm_name=winner["algorithm_name"],
                )

                if xai_result.get("shap_values") or xai_result.get("lime_explanation"):
                    xai_insights = XAIInsights(
                        shap_values=xai_result.get("shap_values"),
                        lime_explanation=xai_result.get("lime_explanation"),
                        top_features=xai_result.get("top_features", []),
                    )
                await self.storage.update_task_status(task_id, "processing", 85)

            # 7. 자연어 리포트 생성
            nlg_report = self.nlg.generate_report(
                winner, feature_importance, top_5, request.task_type
            )

            # 8. 최종 결과 저장
            report = ReportResponse(
                task_id=task_id,
                status="completed",
                total_algorithms_tested=len(results),
                tournament_duration=winner["execution_time"],
                top_5_algorithms=[
                    AlgorithmResult(
                        name=algo["algorithm_name"],
                        r2_score=algo["r2_score"],
                        adj_r2_score=algo.get("adj_r2_score"),
                        p_value=algo.get("p_value"),
                        execution_time=algo["execution_time"],
                    )
                    for algo in top_5
                ],
                winner=WinnerModel(
                    algorithm=winner["algorithm_name"],
                    r2_score=winner["r2_score"],
                    adj_r2_score=winner.get("adj_r2_score"),
                    formula=formula,
                    coefficients=winner.get("coefficients", {}),
                    feature_importance=feature_importance,
                ),
                xai_insights=xai_insights,
                report=nlg_report,
                completed_at=datetime.now(),
                data_shape=(X.shape[0], X.shape[1]),
            )

            await self.storage.save_report(task_id, report)
            await self.storage.update_task_status(task_id, "completed", 100)

            # 9. Webhook 알림 전송
            if request.webhook_url:
                logger.info(f"Webhook 전송: {request.webhook_url}")
                await self.webhook_service.send_completion_notification(
                    task_id=task_id,
                    webhook_url=request.webhook_url,
                    report_summary=report.model_dump(),
                )

            logger.info(f"작업 {task_id} 완료")

        except Exception as e:
            logger.error(f"작업 {task_id} 실패: {str(e)}", exc_info=True)
            await self.storage.update_task_status(task_id, "failed", 0)
            await self.storage.save_error(task_id, str(e))

            if request.webhook_url:
                await self.webhook_service.send_error_notification(
                    task_id=task_id,
                    webhook_url=request.webhook_url,
                    error_message=str(e),
                )
