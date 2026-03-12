"""
Multi-class Classification Algorithms (17종)
다중분류 알고리즘 (3개 이상 클래스)
분류 알고리즘을 multi_class=OvR 모드로 확장
"""
import pandas as pd
import numpy as np
from typing import Any

from app.models.algorithms.base import ClassificationAlgorithm
from app.models.algorithms.classification.classifiers import (
    LogisticRegressionClf,
    SVMClassifier,
    SVMLinearClf,
    SVMPolyClf,
    RandomForestClf,
    ExtraTreesClf,
    GradientBoostingClf,
    XGBClassifierAlgo,
    LGBMClassifierAlgo,
    KNeighborsClf,
    DecisionTreeClf,
    AdaBoostClf,
    BaggingClf,
    MLPClf,
    GaussianNBClf,
    HistGradientBoostingClf,
    RidgeClf,
    XGBOOST_AVAILABLE,
    LGBM_AVAILABLE,
)


class MultiClassWrapper(ClassificationAlgorithm):
    """다중분류 래퍼 - 기존 분류 알고리즘을 multi_class 모드로 실행"""

    def __init__(self, base_classifier: ClassificationAlgorithm) -> None:
        super().__init__(f"MC_{base_classifier.name}")
        self._base = base_classifier

    def fit(self, X: pd.DataFrame, y: pd.Series) -> Any:
        return self._base.fit(X, y)

    def predict(self, model: Any, X: pd.DataFrame) -> np.ndarray:
        return self._base.predict(model, X)

    def predict_proba(self, model: Any, X: pd.DataFrame) -> Any:
        return self._base.predict_proba(model, X)

    def get_coefficients(self, model: Any, feature_names: list) -> dict:
        return self._base.get_coefficients(model, feature_names)

    def execute(self, X: pd.DataFrame, y: pd.Series) -> dict:
        """다중분류 실행 (macro average 사용)"""
        return super().execute(X, y, average="macro")


def get_all_multiclass_classifiers() -> list:
    """전체 다중분류 알고리즘 인스턴스 반환"""
    base_classifiers = [
        LogisticRegressionClf(),
        SVMClassifier(),
        SVMLinearClf(),
        SVMPolyClf(),
        RandomForestClf(),
        ExtraTreesClf(),
        GradientBoostingClf(),
        KNeighborsClf(),
        DecisionTreeClf(),
        AdaBoostClf(),
        BaggingClf(),
        MLPClf(),
        GaussianNBClf(),
        HistGradientBoostingClf(),
        RidgeClf(),
    ]

    if XGBOOST_AVAILABLE:
        base_classifiers.append(XGBClassifierAlgo())
    if LGBM_AVAILABLE:
        base_classifiers.append(LGBMClassifierAlgo())

    return [MultiClassWrapper(clf) for clf in base_classifiers]
