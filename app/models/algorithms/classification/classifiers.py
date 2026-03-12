"""
Classification Algorithms (17종)
이진 분류 알고리즘
"""
import pandas as pd
import numpy as np
from typing import Any

from sklearn.linear_model import LogisticRegression, RidgeClassifier, SGDClassifier
from sklearn.svm import SVC, LinearSVC
from sklearn.ensemble import (
    RandomForestClassifier,
    ExtraTreesClassifier,
    GradientBoostingClassifier,
    AdaBoostClassifier,
    BaggingClassifier,
    HistGradientBoostingClassifier,
)
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.naive_bayes import GaussianNB

from app.models.algorithms.base import ClassificationAlgorithm

# 선택적 임포트
try:
    from xgboost import XGBClassifier
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False

try:
    from lightgbm import LGBMClassifier
    LGBM_AVAILABLE = True
except ImportError:
    LGBM_AVAILABLE = False

try:
    from catboost import CatBoostClassifier
    CATBOOST_AVAILABLE = True
except ImportError:
    CATBOOST_AVAILABLE = False


class LogisticRegressionClf(ClassificationAlgorithm):
    def __init__(self) -> None:
        super().__init__("LogisticRegression")

    def fit(self, X: pd.DataFrame, y: pd.Series) -> Any:
        model = LogisticRegression(max_iter=1000, random_state=42)
        return model.fit(X, y)

    def predict(self, model: Any, X: pd.DataFrame) -> np.ndarray:
        return model.predict(X)


class SVMClassifier(ClassificationAlgorithm):
    def __init__(self) -> None:
        super().__init__("SVM_RBF")

    def fit(self, X: pd.DataFrame, y: pd.Series) -> Any:
        model = SVC(kernel="rbf", probability=True, random_state=42)
        return model.fit(X, y)

    def predict(self, model: Any, X: pd.DataFrame) -> np.ndarray:
        return model.predict(X)


class SVMLinearClf(ClassificationAlgorithm):
    def __init__(self) -> None:
        super().__init__("SVM_Linear")

    def fit(self, X: pd.DataFrame, y: pd.Series) -> Any:
        model = SVC(kernel="linear", probability=True, random_state=42)
        return model.fit(X, y)

    def predict(self, model: Any, X: pd.DataFrame) -> np.ndarray:
        return model.predict(X)


class SVMPolyClf(ClassificationAlgorithm):
    def __init__(self) -> None:
        super().__init__("SVM_Poly")

    def fit(self, X: pd.DataFrame, y: pd.Series) -> Any:
        model = SVC(kernel="poly", probability=True, random_state=42)
        return model.fit(X, y)

    def predict(self, model: Any, X: pd.DataFrame) -> np.ndarray:
        return model.predict(X)


class RandomForestClf(ClassificationAlgorithm):
    def __init__(self) -> None:
        super().__init__("RandomForest_Clf")

    def fit(self, X: pd.DataFrame, y: pd.Series) -> Any:
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        return model.fit(X, y)

    def predict(self, model: Any, X: pd.DataFrame) -> np.ndarray:
        return model.predict(X)


class ExtraTreesClf(ClassificationAlgorithm):
    def __init__(self) -> None:
        super().__init__("ExtraTrees_Clf")

    def fit(self, X: pd.DataFrame, y: pd.Series) -> Any:
        model = ExtraTreesClassifier(n_estimators=100, random_state=42)
        return model.fit(X, y)

    def predict(self, model: Any, X: pd.DataFrame) -> np.ndarray:
        return model.predict(X)


class GradientBoostingClf(ClassificationAlgorithm):
    def __init__(self) -> None:
        super().__init__("GradientBoosting_Clf")

    def fit(self, X: pd.DataFrame, y: pd.Series) -> Any:
        model = GradientBoostingClassifier(n_estimators=100, random_state=42)
        return model.fit(X, y)

    def predict(self, model: Any, X: pd.DataFrame) -> np.ndarray:
        return model.predict(X)


class XGBClassifierAlgo(ClassificationAlgorithm):
    def __init__(self) -> None:
        super().__init__("XGBoost_Clf")

    def fit(self, X: pd.DataFrame, y: pd.Series) -> Any:
        if not XGBOOST_AVAILABLE:
            raise ImportError("XGBoost 미설치")
        model = XGBClassifier(n_estimators=100, random_state=42, verbosity=0)
        return model.fit(X, y)

    def predict(self, model: Any, X: pd.DataFrame) -> np.ndarray:
        return model.predict(X)


class LGBMClassifierAlgo(ClassificationAlgorithm):
    def __init__(self) -> None:
        super().__init__("LightGBM_Clf")

    def fit(self, X: pd.DataFrame, y: pd.Series) -> Any:
        if not LGBM_AVAILABLE:
            raise ImportError("LightGBM 미설치")
        model = LGBMClassifier(n_estimators=100, random_state=42, verbose=-1)
        return model.fit(X, y)

    def predict(self, model: Any, X: pd.DataFrame) -> np.ndarray:
        return model.predict(X)


class KNeighborsClf(ClassificationAlgorithm):
    def __init__(self) -> None:
        super().__init__("KNN_Clf")

    def fit(self, X: pd.DataFrame, y: pd.Series) -> Any:
        model = KNeighborsClassifier(n_neighbors=5)
        return model.fit(X, y)

    def predict(self, model: Any, X: pd.DataFrame) -> np.ndarray:
        return model.predict(X)


class DecisionTreeClf(ClassificationAlgorithm):
    def __init__(self) -> None:
        super().__init__("DecisionTree_Clf")

    def fit(self, X: pd.DataFrame, y: pd.Series) -> Any:
        model = DecisionTreeClassifier(random_state=42)
        return model.fit(X, y)

    def predict(self, model: Any, X: pd.DataFrame) -> np.ndarray:
        return model.predict(X)


class AdaBoostClf(ClassificationAlgorithm):
    def __init__(self) -> None:
        super().__init__("AdaBoost_Clf")

    def fit(self, X: pd.DataFrame, y: pd.Series) -> Any:
        model = AdaBoostClassifier(n_estimators=100, random_state=42)
        return model.fit(X, y)

    def predict(self, model: Any, X: pd.DataFrame) -> np.ndarray:
        return model.predict(X)


class BaggingClf(ClassificationAlgorithm):
    def __init__(self) -> None:
        super().__init__("Bagging_Clf")

    def fit(self, X: pd.DataFrame, y: pd.Series) -> Any:
        model = BaggingClassifier(n_estimators=100, random_state=42)
        return model.fit(X, y)

    def predict(self, model: Any, X: pd.DataFrame) -> np.ndarray:
        return model.predict(X)


class MLPClf(ClassificationAlgorithm):
    def __init__(self) -> None:
        super().__init__("MLP_Clf")

    def fit(self, X: pd.DataFrame, y: pd.Series) -> Any:
        model = MLPClassifier(hidden_layer_sizes=(100, 50), max_iter=500, random_state=42)
        return model.fit(X, y)

    def predict(self, model: Any, X: pd.DataFrame) -> np.ndarray:
        return model.predict(X)


class GaussianNBClf(ClassificationAlgorithm):
    def __init__(self) -> None:
        super().__init__("GaussianNB")

    def fit(self, X: pd.DataFrame, y: pd.Series) -> Any:
        model = GaussianNB()
        return model.fit(X, y)

    def predict(self, model: Any, X: pd.DataFrame) -> np.ndarray:
        return model.predict(X)


class HistGradientBoostingClf(ClassificationAlgorithm):
    def __init__(self) -> None:
        super().__init__("HistGBM_Clf")

    def fit(self, X: pd.DataFrame, y: pd.Series) -> Any:
        model = HistGradientBoostingClassifier(max_iter=100, random_state=42)
        return model.fit(X, y)

    def predict(self, model: Any, X: pd.DataFrame) -> np.ndarray:
        return model.predict(X)


class RidgeClf(ClassificationAlgorithm):
    def __init__(self) -> None:
        super().__init__("Ridge_Clf")

    def fit(self, X: pd.DataFrame, y: pd.Series) -> Any:
        model = RidgeClassifier(alpha=1.0)
        return model.fit(X, y)

    def predict(self, model: Any, X: pd.DataFrame) -> np.ndarray:
        return model.predict(X)


def get_all_classifiers() -> list:
    """전체 분류 알고리즘 인스턴스 반환"""
    classifiers = [
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
        classifiers.append(XGBClassifierAlgo())
    if LGBM_AVAILABLE:
        classifiers.append(LGBMClassifierAlgo())

    return classifiers
