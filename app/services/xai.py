"""
XAI (Explainable AI) Service
SHAP 및 LIME 기반 모델 해석
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from loguru import logger

# SHAP와 LIME 선택적 임포트
try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False
    logger.warning("⚠️ SHAP을 사용할 수 없습니다. XAI 기능이 제한됩니다.")

try:
    from lime import lime_tabular
    LIME_AVAILABLE = True
except ImportError:
    LIME_AVAILABLE = False
    logger.warning("⚠️ LIME을 사용할 수 없습니다. XAI 기능이 제한됩니다.")

from app.core.config import settings


class XAIEngine:
    """XAI 통합 엔진"""

    def __init__(self):
        self.enable_shap = settings.xai_enable_shap and SHAP_AVAILABLE
        self.enable_lime = settings.xai_enable_lime and LIME_AVAILABLE
        self.max_features = settings.xai_max_features

        if not SHAP_AVAILABLE and not LIME_AVAILABLE:
            logger.warning("⚠️ SHAP와 LIME 모두 사용할 수 없습니다. XAI 기능이 비활성화됩니다.")

    def explain_model(
        self,
        model: Any,
        X: pd.DataFrame,
        y: pd.Series,
        algorithm_name: str
    ) -> Dict[str, Any]:
        """
        모델 설명 생성

        Args:
            model: 학습된 모델
            X: 독립 변수
            y: 종속 변수
            algorithm_name: 알고리즘 이름

        Returns:
            XAI 통찰 딕셔너리
        """
        logger.info(f"🔍 XAI 분석 시작: {algorithm_name}")

        insights = {
            "shap_values": None,
            "lime_explanation": None,
            "top_features": [],
            "feature_interactions": {}
        }

        try:
            # SHAP 분석
            if self.enable_shap:
                shap_result = self._compute_shap_values(model, X, algorithm_name)
                if shap_result:
                    insights["shap_values"] = shap_result["values"]
                    insights["top_features"] = shap_result["top_features"]
                    insights["feature_interactions"] = shap_result.get("interactions", {})

            # LIME 분석
            if self.enable_lime:
                lime_result = self._compute_lime_explanation(model, X, algorithm_name)
                if lime_result:
                    insights["lime_explanation"] = lime_result

            logger.info(f"✅ XAI 분석 완료: {algorithm_name}")

        except Exception as e:
            logger.error(f"❌ XAI 분석 실패: {algorithm_name} - {str(e)}")

        return insights

    def _compute_shap_values(
        self,
        model: Any,
        X: pd.DataFrame,
        algorithm_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        SHAP 값 계산

        Args:
            model: 학습된 모델
            X: 독립 변수
            algorithm_name: 알고리즘 이름

        Returns:
            SHAP 분석 결과
        """
        if not SHAP_AVAILABLE:
            return None

        try:
            logger.info(f"  SHAP 분석 중: {algorithm_name}")

            # 모델 유형에 따라 적절한 Explainer 선택
            explainer = None

            # Tree-based models
            if algorithm_name in ["RandomForest", "XGBoost", "LightGBM", "CatBoost",
                                  "GradientBoosting", "DecisionTree", "ExtraTrees",
                                  "AdaBoost", "HistGradientBoosting"]:
                try:
                    explainer = shap.TreeExplainer(model)
                except Exception:
                    explainer = shap.Explainer(model.predict, X.sample(min(100, len(X))))

            # Linear models
            elif algorithm_name in ["OLS", "Ridge", "Lasso", "ElasticNet",
                                    "BayesianRidge", "ARD", "Huber"]:
                try:
                    explainer = shap.LinearExplainer(model, X)
                except Exception:
                    explainer = shap.Explainer(model.predict, X.sample(min(100, len(X))))

            # Others - use KernelExplainer (slower)
            else:
                # 샘플링하여 속도 향상
                sample_size = min(100, len(X))
                background = X.sample(sample_size, random_state=42)
                explainer = shap.KernelExplainer(model.predict, background)

            # SHAP 값 계산
            sample_for_shap = X.sample(min(200, len(X)), random_state=42)
            shap_values = explainer.shap_values(sample_for_shap)

            # SHAP 값이 3차원인 경우 (다중 출력) 첫 번째 출력만 사용
            if isinstance(shap_values, list):
                shap_values = shap_values[0]

            # 평균 절댓값 기준 특성 중요도 계산
            if len(shap_values.shape) > 1:
                mean_abs_shap = np.abs(shap_values).mean(axis=0)
            else:
                mean_abs_shap = np.abs(shap_values)

            # 특성별 SHAP 값
            feature_shap = {
                feature: float(value)
                for feature, value in zip(X.columns, mean_abs_shap)
            }

            # 상위 N개 특성
            sorted_features = sorted(
                feature_shap.items(),
                key=lambda x: abs(x[1]),
                reverse=True
            )
            top_features = [
                feature for feature, _ in sorted_features[:self.max_features]
            ]

            logger.info(f"  ✅ SHAP 완료: 상위 {len(top_features)}개 특성 추출")

            return {
                "values": feature_shap,
                "top_features": top_features,
                "interactions": {}  # Phase 4에서 구현 가능
            }

        except Exception as e:
            logger.warning(f"  ⚠️ SHAP 분석 스킵: {algorithm_name} - {str(e)}")
            return None

    def _compute_lime_explanation(
        self,
        model: Any,
        X: pd.DataFrame,
        algorithm_name: str
    ) -> Optional[str]:
        """
        LIME 설명 생성

        Args:
            model: 학습된 모델
            X: 독립 변수
            algorithm_name: 알고리즘 이름

        Returns:
            자연어 LIME 설명
        """
        if not LIME_AVAILABLE:
            return None

        try:
            logger.info(f"  LIME 분석 중: {algorithm_name}")

            # LIME Explainer 생성
            explainer = lime_tabular.LimeTabularExplainer(
                training_data=X.values,
                feature_names=list(X.columns),
                mode='regression',
                random_state=42
            )

            # 대표 샘플 선택 (중간값)
            median_idx = len(X) // 2
            sample = X.iloc[median_idx].values

            # 설명 생성
            explanation = explainer.explain_instance(
                data_row=sample,
                predict_fn=model.predict,
                num_features=min(self.max_features, len(X.columns))
            )

            # 자연어 설명 생성
            feature_weights = explanation.as_list()
            explanations = []

            for feature_info, weight in feature_weights[:5]:  # 상위 5개
                # feature_info 형식: "feature_name <= 10.5" 또는 "feature_name > 5.2"
                if weight > 0:
                    direction = "증가"
                else:
                    direction = "감소"

                explanations.append(
                    f"{feature_info} 조건에서 예측값을 {abs(weight):.4f}만큼 {direction}시킴"
                )

            lime_text = "; ".join(explanations)
            logger.info(f"  ✅ LIME 완료")

            return lime_text

        except Exception as e:
            logger.warning(f"  ⚠️ LIME 분석 스킵: {algorithm_name} - {str(e)}")
            return None

    def generate_xai_report(
        self,
        insights: Dict[str, Any],
        algorithm_name: str
    ) -> Dict[str, Any]:
        """
        XAI 분석 결과를 리포트 형태로 변환

        Args:
            insights: XAI 통찰
            algorithm_name: 알고리즘 이름

        Returns:
            구조화된 XAI 리포트
        """
        report = {
            "algorithm": algorithm_name,
            "interpretation_method": []
        }

        if insights.get("shap_values"):
            report["interpretation_method"].append("SHAP")
            report["shap_top_features"] = insights["top_features"]
            report["shap_values"] = insights["shap_values"]

        if insights.get("lime_explanation"):
            report["interpretation_method"].append("LIME")
            report["lime_explanation"] = insights["lime_explanation"]

        if not report["interpretation_method"]:
            report["interpretation_method"] = ["기본 계수 분석"]

        return report
