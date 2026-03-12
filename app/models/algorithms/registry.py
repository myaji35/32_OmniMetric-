"""
Algorithm Registry
모든 알고리즘을 등록하고 관리하는 레지스트리 (4대 분석유형 지원)
"""
from typing import List, Tuple, Callable, Literal
from loguru import logger

# Linear Models (10개)
from app.models.algorithms.linear_models import (
    OLSRegression, RidgeRegression, LassoRegression, ElasticNetRegression,
    BayesianRidgeRegression, ARDRegression, HuberRegression,
    RANSACRegression, TheilSenRegression, PassiveAggressiveRegression
)

# Tree Models (15개)
from app.models.algorithms.tree_models import (
    DecisionTree, RandomForest, ExtraTrees, GradientBoosting,
    XGBoost, LightGBM, CatBoost, AdaBoost, Bagging, HistGradientBoosting,
    DecisionTreeDepth5, RandomForest50, RandomForest200, XGBoostDeep, LightGBMFast
)

# Non-Linear Models (20개)
from app.models.algorithms.nonlinear_models import (
    SupportVectorRegression, SVRLinear, SVRPoly, NuSVRegression,
    KNearestNeighbors, KNN10, NeuralNetwork, MLPDeep,
    PolynomialRegression2, PolynomialRegression3,
    KernelRidgeRBF, KernelRidgePoly,
    SVRSigmoid, KNN3, KNN15, MLPWide, MLPSmall,
    PolynomialRegression4, KernelRidgeLinear, KernelRidgeSigmoid
)

# Ensemble Models (15개)
from app.models.algorithms.ensemble_models import (
    VotingEnsemble, StackingEnsemble, PLSRegression1, PLSRegression3, PCARidge,
    StackingDeep, VotingWeighted,
    RidgeAlpha01, RidgeAlpha10, LassoAlpha01, LassoAlpha10,
    ElasticNetAlpha01, ElasticNetAlpha10, ElasticNetL1Heavy, ElasticNetL2Heavy
)

# Classification (17종)
from app.models.algorithms.classification.classifiers import get_all_classifiers

# Multi-class (17종)
from app.models.algorithms.multiclass.multiclass_classifiers import (
    get_all_multiclass_classifiers,
)

# Time Series (61종)
from app.models.algorithms.timeseries.ts_models import get_all_timeseries_algorithms


class AlgorithmRegistry:
    """
    알고리즘 레지스트리
    4대 분석유형별 알고리즘 관리 (regression/classification/multiclass/timeseries)
    """

    def __init__(self) -> None:
        self._regression_algorithms = self._initialize_regression()
        self._classification_algorithms = self._initialize_classification()
        self._multiclass_algorithms = self._initialize_multiclass()
        self._timeseries_algorithms = self._initialize_timeseries()

        total = (
            len(self._regression_algorithms)
            + len(self._classification_algorithms)
            + len(self._multiclass_algorithms)
            + len(self._timeseries_algorithms)
        )
        logger.info(f"알고리즘 레지스트리 초기화: 총 {total}개")

    def _initialize_regression(self) -> List[Tuple[str, Callable]]:
        """회귀분석 알고리즘 초기화"""
        algorithms = []

        linear_models = [
            OLSRegression(), RidgeRegression(), LassoRegression(),
            ElasticNetRegression(), BayesianRidgeRegression(), ARDRegression(),
            HuberRegression(), RANSACRegression(), TheilSenRegression(),
            PassiveAggressiveRegression(),
        ]

        tree_models = [
            DecisionTree(), RandomForest(), ExtraTrees(), GradientBoosting(),
            XGBoost(), LightGBM(), AdaBoost(), Bagging(), HistGradientBoosting(),
            DecisionTreeDepth5(), RandomForest50(), RandomForest200(),
            XGBoostDeep(), LightGBMFast(),
        ]

        if CatBoost is not None:
            tree_models.append(CatBoost())

        nonlinear_models = [
            SupportVectorRegression(), SVRLinear(), SVRPoly(), NuSVRegression(),
            KNearestNeighbors(), KNN10(), NeuralNetwork(), MLPDeep(),
            PolynomialRegression2(), PolynomialRegression3(),
            KernelRidgeRBF(), KernelRidgePoly(), SVRSigmoid(),
            KNN3(), KNN15(), MLPWide(), MLPSmall(),
            PolynomialRegression4(), KernelRidgeLinear(), KernelRidgeSigmoid(),
        ]

        ensemble_models = [
            VotingEnsemble(), StackingEnsemble(), PLSRegression1(),
            PLSRegression3(), PCARidge(), StackingDeep(), VotingWeighted(),
            RidgeAlpha01(), RidgeAlpha10(), LassoAlpha01(), LassoAlpha10(),
            ElasticNetAlpha01(), ElasticNetAlpha10(), ElasticNetL1Heavy(),
            ElasticNetL2Heavy(),
        ]

        for model in linear_models + tree_models + nonlinear_models + ensemble_models:
            algorithms.append((model.name, model.execute))

        logger.info(
            f"  Regression: Linear={len(linear_models)}, Tree={len(tree_models)}, "
            f"NonLinear={len(nonlinear_models)}, Ensemble={len(ensemble_models)}"
        )
        return algorithms

    def _initialize_classification(self) -> List[Tuple[str, Callable]]:
        """분류분석 알고리즘 초기화"""
        classifiers = get_all_classifiers()
        algorithms = [(clf.name, clf.execute) for clf in classifiers]
        logger.info(f"  Classification: {len(algorithms)}개")
        return algorithms

    def _initialize_multiclass(self) -> List[Tuple[str, Callable]]:
        """다중분류분석 알고리즘 초기화"""
        mc_classifiers = get_all_multiclass_classifiers()
        algorithms = [(clf.name, clf.execute) for clf in mc_classifiers]
        logger.info(f"  Multiclass: {len(algorithms)}개")
        return algorithms

    def _initialize_timeseries(self) -> List[Tuple[str, Callable]]:
        """시계열분석 알고리즘 초기화"""
        ts_algorithms = get_all_timeseries_algorithms()
        algorithms = [(ts.name, ts.execute) for ts in ts_algorithms]
        logger.info(f"  TimeSeries: {len(algorithms)}개")
        return algorithms

    def get_all_algorithms(
        self,
        task_type: str = "regression",
    ) -> List[Tuple[str, Callable]]:
        """
        분석유형별 알고리즘 반환

        Args:
            task_type: 분석 유형

        Returns:
            (알고리즘_이름, 실행_함수) 튜플 리스트
        """
        if task_type == "classification":
            return self._classification_algorithms
        elif task_type == "multiclass":
            return self._multiclass_algorithms
        elif task_type == "timeseries":
            return self._timeseries_algorithms
        else:
            return self._regression_algorithms

    def get_algorithm_by_name(self, name: str) -> Callable:
        """이름으로 특정 알고리즘 검색"""
        all_algos = (
            self._regression_algorithms
            + self._classification_algorithms
            + self._multiclass_algorithms
            + self._timeseries_algorithms
        )
        for algo_name, algo_func in all_algos:
            if algo_name == name:
                return algo_func
        raise ValueError(f"알고리즘 '{name}'을 찾을 수 없습니다.")

    def get_algorithm_count(self) -> int:
        """등록된 알고리즘 총 개수"""
        return len(self._regression_algorithms)

    def get_total_count(self) -> int:
        """전체 알고리즘 수"""
        return (
            len(self._regression_algorithms)
            + len(self._classification_algorithms)
            + len(self._multiclass_algorithms)
            + len(self._timeseries_algorithms)
        )

    def get_algorithm_names(self) -> List[str]:
        """모든 알고리즘 이름 리스트"""
        return [name for name, _ in self._regression_algorithms]
