"""
Algorithm Base Classes
알고리즘 기본 인터페이스 및 추상 클래스
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import pandas as pd
import numpy as np
from loguru import logger

from app.core.evaluator import ModelEvaluator


class BaseAlgorithm(ABC):
    """알고리즘 베이스 클래스 (회귀분석용)"""

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def fit(self, X: pd.DataFrame, y: pd.Series) -> Any:
        """모델 학습"""
        pass

    @abstractmethod
    def predict(self, model: Any, X: pd.DataFrame) -> np.ndarray:
        """예측"""
        pass

    @abstractmethod
    def get_coefficients(self, model: Any, feature_names: list) -> Dict[str, float]:
        """모델 계수 추출"""
        pass

    def execute(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, Any]:
        """
        알고리즘 실행 (Train/Test Split 적용)

        Args:
            X: 독립 변수
            y: 종속 변수

        Returns:
            실행 결과 딕셔너리
        """
        try:
            # 1. Train/Test Split (80:20)
            X_train, X_test, y_train, y_test = ModelEvaluator.split_data(X, y)

            # 2. Train 데이터로 학습
            model = self.fit(X_train, y_train)

            # 3. Test 데이터로 평가 (과적합 방지)
            y_pred_test = self.predict(model, X_test)
            metrics = ModelEvaluator.evaluate_regression(
                y_test, y_pred_test, X_test.shape[1]
            )

            # 4. 전체 데이터로 재학습 (최종 배포 모델)
            model_full = self.fit(X, y)

            # 5. 계수 추출
            coefficients = self.get_coefficients(model_full, list(X.columns))

            return {
                "r2_score": metrics["r2_score"],
                "adj_r2_score": metrics["adj_r2_score"],
                "mae": metrics.get("mae"),
                "rmse": metrics.get("rmse"),
                "p_value": None,
                "model": model_full,
                "coefficients": coefficients,
            }

        except Exception as e:
            logger.error(f"{self.name} 실행 실패: {str(e)}")
            raise


class LinearAlgorithm(BaseAlgorithm):
    """선형 모델 공통 클래스"""

    def get_coefficients(self, model: Any, feature_names: list) -> Dict[str, float]:
        """선형 모델 계수 추출"""
        coefficients = {
            feature: float(coef)
            for feature, coef in zip(feature_names, model.coef_)
        }

        if hasattr(model, 'intercept_'):
            coefficients['intercept'] = float(model.intercept_)

        return coefficients


class TreeAlgorithm(BaseAlgorithm):
    """트리 기반 모델 공통 클래스"""

    def get_coefficients(self, model: Any, feature_names: list) -> Dict[str, float]:
        """트리 모델 특성 중요도 추출"""
        if hasattr(model, 'feature_importances_'):
            coefficients = {
                feature: float(importance)
                for feature, importance in zip(feature_names, model.feature_importances_)
            }
            coefficients['intercept'] = 0.0
            return coefficients

        return {feature: 0.0 for feature in feature_names}


class ClassificationAlgorithm(ABC):
    """분류 알고리즘 베이스 클래스"""

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def fit(self, X: pd.DataFrame, y: pd.Series) -> Any:
        """모델 학습"""
        pass

    @abstractmethod
    def predict(self, model: Any, X: pd.DataFrame) -> np.ndarray:
        """예측"""
        pass

    def predict_proba(self, model: Any, X: pd.DataFrame) -> Optional[np.ndarray]:
        """확률 예측 (지원하는 모델만)"""
        if hasattr(model, 'predict_proba'):
            return model.predict_proba(X)
        return None

    def get_coefficients(self, model: Any, feature_names: list) -> Dict[str, float]:
        """분류 모델 특성 중요도 추출"""
        if hasattr(model, 'feature_importances_'):
            return {
                feature: float(imp)
                for feature, imp in zip(feature_names, model.feature_importances_)
            }
        if hasattr(model, 'coef_'):
            coefs = model.coef_.ravel() if model.coef_.ndim > 1 else model.coef_
            return {
                feature: float(c)
                for feature, c in zip(feature_names, coefs)
            }
        return {feature: 0.0 for feature in feature_names}

    def execute(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        average: str = "binary",
    ) -> Dict[str, Any]:
        """
        분류 알고리즘 실행 (Train/Test Split 적용)

        Args:
            X: 독립 변수
            y: 종속 변수
            average: 평가 평균 방식

        Returns:
            실행 결과 딕셔너리
        """
        try:
            # 1. Train/Test Split
            X_train, X_test, y_train, y_test = ModelEvaluator.split_data(X, y)

            # 2. 학습
            model = self.fit(X_train, y_train)

            # 3. 평가
            y_pred = self.predict(model, X_test)
            y_prob = self.predict_proba(model, X_test)
            metrics = ModelEvaluator.evaluate_classification(
                y_test, y_pred, y_prob, average=average
            )

            # 4. 전체 데이터로 재학습
            model_full = self.fit(X, y)

            # 5. 계수 추출
            coefficients = self.get_coefficients(model_full, list(X.columns))

            # R2 호환 (정렬용): F1 점수를 r2_score로 매핑
            return {
                "r2_score": metrics["f1_score"],
                "adj_r2_score": None,
                "metrics": metrics,
                "p_value": None,
                "model": model_full,
                "coefficients": coefficients,
            }

        except Exception as e:
            logger.error(f"{self.name} 실행 실패: {str(e)}")
            raise


class TimeSeriesAlgorithm(ABC):
    """시계열 알고리즘 베이스 클래스"""

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def fit(self, y_train: pd.Series, **kwargs: Any) -> Any:
        """시계열 모델 학습"""
        pass

    @abstractmethod
    def predict(self, model: Any, steps: int) -> np.ndarray:
        """미래 예측"""
        pass

    def get_coefficients(self, model: Any, feature_names: list) -> Dict[str, float]:
        """시계열 모델 파라미터 추출"""
        return {}

    def execute(
        self,
        X: pd.DataFrame,
        y: pd.Series,
    ) -> Dict[str, Any]:
        """
        시계열 알고리즘 실행 (시간 기반 Split)

        Args:
            X: 독립 변수 (파생변수 포함)
            y: 종속 변수 (시계열)

        Returns:
            실행 결과 딕셔너리
        """
        try:
            # 시계열은 시간 순서 유지하며 Split (마지막 20%를 테스트)
            n = len(y)
            split_idx = int(n * 0.8)

            y_train = y.iloc[:split_idx]
            y_test = y.iloc[split_idx:]

            # 학습
            model = self.fit(y_train)

            # 예측
            steps = len(y_test)
            y_pred = self.predict(model, steps)

            # 평가
            from sklearn.metrics import r2_score, mean_absolute_error
            r2 = r2_score(y_test, y_pred[:len(y_test)])
            mae = mean_absolute_error(y_test, y_pred[:len(y_test)])

            # 전체 데이터로 재학습
            model_full = self.fit(y)

            return {
                "r2_score": float(r2),
                "adj_r2_score": None,
                "mae": float(mae),
                "p_value": None,
                "model": model_full,
                "coefficients": {},
            }

        except Exception as e:
            logger.error(f"{self.name} 실행 실패: {str(e)}")
            raise
