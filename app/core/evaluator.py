"""
Model Evaluator
Train/Test Split 및 모델 평가 모듈
"""
import numpy as np
import pandas as pd
from typing import Dict, Any, Optional, Tuple
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import (
    r2_score,
    mean_absolute_error,
    mean_squared_error,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
)
from loguru import logger


class ModelEvaluator:
    """Train/Test Split 및 모델 평가"""

    @staticmethod
    def split_data(
        X: pd.DataFrame,
        y: pd.Series,
        test_size: float = 0.2,
        random_state: int = 42,
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
        """
        데이터를 Train/Test로 분할

        Args:
            X: 독립 변수
            y: 종속 변수
            test_size: 테스트셋 비율 (기본 20%)
            random_state: 랜덤 시드

        Returns:
            (X_train, X_test, y_train, y_test)
        """
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )
        logger.info(
            f"데이터 분할: Train={len(X_train)}, Test={len(X_test)} "
            f"(비율: {1 - test_size:.0%}/{test_size:.0%})"
        )
        return X_train, X_test, y_train, y_test

    @staticmethod
    def evaluate_regression(
        y_true: pd.Series,
        y_pred: np.ndarray,
        n_features: int,
    ) -> Dict[str, Any]:
        """
        회귀 모델 평가

        Args:
            y_true: 실제값
            y_pred: 예측값
            n_features: 특성 수

        Returns:
            평가 지표 딕셔너리
        """
        n = len(y_true)
        r2 = r2_score(y_true, y_pred)
        adj_r2 = 1 - (1 - r2) * (n - 1) / (n - n_features - 1) if n > n_features + 1 else None
        mae = mean_absolute_error(y_true, y_pred)
        mse = mean_squared_error(y_true, y_pred)
        rmse = np.sqrt(mse)

        return {
            "r2_score": float(r2),
            "adj_r2_score": float(adj_r2) if adj_r2 is not None else None,
            "mae": float(mae),
            "mse": float(mse),
            "rmse": float(rmse),
        }

    @staticmethod
    def evaluate_classification(
        y_true: pd.Series,
        y_pred: np.ndarray,
        y_prob: Optional[np.ndarray] = None,
        average: str = "binary",
    ) -> Dict[str, Any]:
        """
        분류 모델 평가

        Args:
            y_true: 실제값
            y_pred: 예측값
            y_prob: 예측 확률 (AUC-ROC용)
            average: 평균 방식 ('binary', 'macro', 'micro', 'weighted')

        Returns:
            평가 지표 딕셔너리
        """
        metrics: Dict[str, Any] = {
            "accuracy": float(accuracy_score(y_true, y_pred)),
            "precision": float(precision_score(y_true, y_pred, average=average, zero_division=0)),
            "recall": float(recall_score(y_true, y_pred, average=average, zero_division=0)),
            "f1_score": float(f1_score(y_true, y_pred, average=average, zero_division=0)),
        }

        # AUC-ROC (확률 예측이 있는 경우)
        if y_prob is not None:
            try:
                if average == "binary":
                    prob = y_prob[:, 1] if y_prob.ndim > 1 else y_prob
                    metrics["auc_roc"] = float(roc_auc_score(y_true, prob))
                else:
                    metrics["auc_roc"] = float(
                        roc_auc_score(y_true, y_prob, multi_class="ovr", average=average)
                    )
            except (ValueError, IndexError):
                metrics["auc_roc"] = None
        else:
            metrics["auc_roc"] = None

        # Confusion Matrix
        cm = confusion_matrix(y_true, y_pred)
        metrics["confusion_matrix"] = cm.tolist()

        return metrics

    @staticmethod
    def cross_validate(
        model: Any,
        X: pd.DataFrame,
        y: pd.Series,
        cv: int = 5,
        scoring: str = "r2",
    ) -> Dict[str, Any]:
        """
        K-Fold Cross Validation

        Args:
            model: sklearn 호환 모델
            X: 독립 변수
            y: 종속 변수
            cv: Fold 수
            scoring: 평가 지표

        Returns:
            CV 결과 딕셔너리
        """
        try:
            scores = cross_val_score(model, X, y, cv=cv, scoring=scoring)
            return {
                "cv_scores": scores.tolist(),
                "cv_mean": float(scores.mean()),
                "cv_std": float(scores.std()),
                "cv_folds": cv,
            }
        except Exception as e:
            logger.warning(f"Cross Validation 실패: {e}")
            return {
                "cv_scores": [],
                "cv_mean": None,
                "cv_std": None,
                "cv_folds": cv,
            }
