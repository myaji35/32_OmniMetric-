"""
Tournament Engine
60+ 알고리즘 토너먼트 메인 엔진
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List
from datetime import datetime
from loguru import logger

from app.core.parallel import ParallelTournament
from app.models.algorithms.registry import AlgorithmRegistry
from app.core.storage import TaskStorage
from app.services.xai import XAIEngine
from app.services.webhook import get_webhook_service
from app.models.schemas import (
    AnalyzeRequest,
    ReportResponse,
    AlgorithmResult,
    WinnerModel,
    NaturalLanguageReport,
    XAIInsights
)


class TournamentEngine:
    """
    알고리즘 토너먼트 메인 엔진
    데이터 전처리부터 최종 리포트 생성까지 전 과정 관리
    """

    def __init__(self):
        self.parallel_tournament = ParallelTournament()
        self.algorithm_registry = AlgorithmRegistry()
        self.storage = TaskStorage()
        self.xai_engine = XAIEngine()
        self.webhook_service = get_webhook_service()

    def prepare_data(
        self,
        request: AnalyzeRequest
    ) -> tuple[pd.DataFrame, pd.Series]:
        """
        데이터 전처리

        Args:
            request: 분석 요청 데이터

        Returns:
            (X, y) 튜플 - 독립변수 DataFrame, 종속변수 Series
        """
        logger.info("📊 데이터 전처리 시작")

        # JSON 데이터를 DataFrame으로 변환
        df = pd.DataFrame(request.data)
        logger.info(f"데이터 형태: {df.shape} (행: {df.shape[0]}, 열: {df.shape[1]})")

        # 종속 변수 분리
        if request.target_column not in df.columns:
            raise ValueError(f"타겟 컬럼 '{request.target_column}'을 찾을 수 없습니다.")

        y = df[request.target_column]
        X = df.drop(columns=[request.target_column])

        # 기본 전처리
        # 1. 결측치 처리
        X = X.fillna(X.mean(numeric_only=True))
        y = y.fillna(y.mean() if pd.api.types.is_numeric_dtype(y) else y.mode()[0])

        # 2. 범주형 변수 인코딩 (간단한 Label Encoding)
        for col in X.select_dtypes(include=['object']).columns:
            X[col] = pd.Categorical(X[col]).codes

        logger.info(f"✅ 전처리 완료: X={X.shape}, y={y.shape}")
        logger.info(f"   특성: {list(X.columns)}")

        return X, y

    def extract_formula(
        self,
        winner: Dict[str, Any],
        feature_names: List[str]
    ) -> str:
        """
        수학적 공식 생성

        Args:
            winner: 승자 알고리즘 결과
            feature_names: 특성 이름 리스트

        Returns:
            수학 공식 문자열
        """
        coefficients = winner.get("coefficients", {})

        if not coefficients:
            return f"{winner['algorithm_name']} 모델 (공식 추출 불가)"

        # 선형 모델 형태로 공식 생성
        terms = []
        intercept = coefficients.get("intercept", 0)

        for feature in feature_names:
            coef = coefficients.get(feature, 0)
            if abs(coef) > 1e-6:  # 매우 작은 계수는 제외
                sign = "+" if coef >= 0 else ""
                terms.append(f"{sign}{coef:.4f}*{feature}")

        formula = " ".join(terms)
        if intercept != 0:
            formula += f" + {intercept:.4f}"

        return f"Y = {formula}"

    def calculate_feature_importance(
        self,
        winner: Dict[str, Any],
        feature_names: List[str]
    ) -> Dict[str, float]:
        """
        변수 중요도 계산 (백분율)

        Args:
            winner: 승자 알고리즘 결과
            feature_names: 특성 이름 리스트

        Returns:
            {특성명: 중요도(%)} 딕셔너리
        """
        coefficients = winner.get("coefficients", {})

        if not coefficients:
            return {feature: 0.0 for feature in feature_names}

        # 절댓값 기준으로 중요도 계산
        abs_coefs = {
            feature: abs(coefficients.get(feature, 0))
            for feature in feature_names
        }

        total = sum(abs_coefs.values())
        if total == 0:
            return {feature: 0.0 for feature in feature_names}

        importance = {
            feature: (value / total) * 100
            for feature, value in abs_coefs.items()
        }

        # 중요도 순으로 정렬
        sorted_importance = dict(
            sorted(importance.items(), key=lambda x: x[1], reverse=True)
        )

        return sorted_importance

    def generate_nlg_report(
        self,
        winner: Dict[str, Any],
        feature_importance: Dict[str, float],
        top_algorithms: List[Dict[str, Any]]
    ) -> NaturalLanguageReport:
        """
        자연어 리포트 생성

        Args:
            winner: 승자 알고리즘
            feature_importance: 변수 중요도
            top_algorithms: 상위 알고리즘 리스트

        Returns:
            자연어 리포트 객체
        """
        # 요약
        summary = (
            f"총 {len(top_algorithms)}개 알고리즘 중 '{winner['algorithm_name']}'이(가) "
            f"최고 성능(R²={winner['r2_score']:.4f})을 달성했습니다."
        )

        # 핵심 발견사항
        key_findings = [
            f"최적 모델: {winner['algorithm_name']}",
            f"설명력(R²): {winner['r2_score']:.4f} ({winner['r2_score']*100:.2f}%)",
            f"실행 시간: {winner['execution_time']:.2f}초"
        ]

        if winner.get("adj_r2_score"):
            key_findings.append(f"조정된 R²: {winner['adj_r2_score']:.4f}")

        # 변수별 영향 설명
        variable_impacts = []
        for feature, importance in list(feature_importance.items())[:5]:  # 상위 5개
            coef = winner.get("coefficients", {}).get(feature, 0)
            direction = "증가" if coef > 0 else "감소"
            variable_impacts.append(
                f"'{feature}' 변수는 전체 영향력의 {importance:.2f}%를 차지하며, "
                f"값이 증가할 때 결과값을 {direction}시킵니다."
            )

        # 선정 사유
        selection_reason = (
            f"{winner['algorithm_name']}은(는) {len(top_algorithms)}개 후보 중 "
            f"가장 높은 R² 점수({winner['r2_score']:.4f})를 기록했습니다. "
        )

        if len(top_algorithms) > 1:
            second_best = top_algorithms[1]
            gap = winner['r2_score'] - second_best['r2_score']
            selection_reason += (
                f"2위 알고리즘({second_best['algorithm_name']}, "
                f"R²={second_best['r2_score']:.4f})보다 "
                f"{gap:.4f}만큼 우수한 성능을 보였습니다."
            )

        return NaturalLanguageReport(
            summary=summary,
            key_findings=key_findings,
            variable_impacts=variable_impacts,
            selection_reason=selection_reason
        )

    async def run_tournament(
        self,
        task_id: str,
        request: AnalyzeRequest
    ) -> None:
        """
        토너먼트 실행 (비동기 백그라운드 작업)

        Args:
            task_id: 작업 ID
            request: 분석 요청
        """
        try:
            logger.info(f"🚀 작업 {task_id} 시작")
            start_time = datetime.now()

            # 상태 업데이트: processing
            await self.storage.update_task_status(task_id, "processing", 10)

            # 1. 데이터 전처리
            X, y = self.prepare_data(request)
            await self.storage.update_task_status(task_id, "processing", 20)

            # 2. 알고리즘 로드
            algorithms = self.algorithm_registry.get_all_algorithms(request.task_type)
            logger.info(f"로드된 알고리즘: {len(algorithms)}개")
            await self.storage.update_task_status(task_id, "processing", 30)

            # 3. 병렬 토너먼트 실행
            results = self.parallel_tournament.run_tournament(algorithms, X, y)
            await self.storage.update_task_status(task_id, "processing", 70)

            # 4. 승자 선정
            winner = self.parallel_tournament.get_winner(results)
            top_5 = self.parallel_tournament.get_top_performers(results, top_n=5)

            # 5. 공식 및 중요도 추출
            formula = self.extract_formula(winner, list(X.columns))
            feature_importance = self.calculate_feature_importance(winner, list(X.columns))
            await self.storage.update_task_status(task_id, "processing", 75)

            # 6. XAI 분석 (선택적)
            xai_insights = None
            if request.enable_xai:
                logger.info("🔍 XAI 분석 시작")
                xai_result = self.xai_engine.explain_model(
                    model=winner.get("model"),
                    X=X,
                    y=y,
                    algorithm_name=winner["algorithm_name"]
                )

                if xai_result.get("shap_values") or xai_result.get("lime_explanation"):
                    xai_insights = XAIInsights(
                        shap_values=xai_result.get("shap_values"),
                        lime_explanation=xai_result.get("lime_explanation"),
                        top_features=xai_result.get("top_features", [])
                    )
                await self.storage.update_task_status(task_id, "processing", 85)

            # 7. 자연어 리포트 생성
            nlg_report = self.generate_nlg_report(winner, feature_importance, top_5)

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
                        execution_time=algo["execution_time"]
                    )
                    for algo in top_5
                ],
                winner=WinnerModel(
                    algorithm=winner["algorithm_name"],
                    r2_score=winner["r2_score"],
                    adj_r2_score=winner.get("adj_r2_score"),
                    formula=formula,
                    coefficients=winner.get("coefficients", {}),
                    feature_importance=feature_importance
                ),
                xai_insights=xai_insights,
                report=nlg_report,
                completed_at=datetime.now(),
                data_shape=(X.shape[0], X.shape[1])
            )

            await self.storage.save_report(task_id, report)
            await self.storage.update_task_status(task_id, "completed", 100)

            # 9. Webhook 알림 전송 (선택적)
            if request.webhook_url:
                logger.info(f"📤 Webhook 전송: {request.webhook_url}")
                await self.webhook_service.send_completion_notification(
                    task_id=task_id,
                    webhook_url=request.webhook_url,
                    report_summary=report.model_dump()
                )

            logger.info(f"✅ 작업 {task_id} 완료")

        except Exception as e:
            logger.error(f"❌ 작업 {task_id} 실패: {str(e)}", exc_info=True)
            await self.storage.update_task_status(task_id, "failed", 0)
            await self.storage.save_error(task_id, str(e))

            # Webhook 오류 알림
            if request.webhook_url:
                await self.webhook_service.send_error_notification(
                    task_id=task_id,
                    webhook_url=request.webhook_url,
                    error_message=str(e)
                )
