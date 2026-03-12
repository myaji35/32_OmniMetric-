"""
Time Series Algorithms (61종)
시계열 분석 전용 알고리즘

카테고리:
- 통계 기반 (ARIMA 계열): 15종
- 지수 평활법 (ETS 계열): 10종
- 회귀 기반 시계열: 12종
- 트리/앙상블 기반 시계열: 12종
- 딥러닝/신경망 기반: 7종
- 분해/필터 기반: 5종
"""
from typing import Any, Dict, List

import numpy as np
import pandas as pd
from loguru import logger

from app.models.algorithms.base import TimeSeriesAlgorithm


# ──────────────────────────────────────────────
# 1. 통계 기반 (ARIMA 계열) - 15종
# ──────────────────────────────────────────────


class ARIMAModel(TimeSeriesAlgorithm):
    """ARIMA(1,1,1) 기본"""

    def __init__(self, order: tuple = (1, 1, 1), name: str = "ARIMA(1,1,1)"):
        super().__init__(name)
        self.order = order

    def fit(self, y_train: pd.Series, **kwargs: Any) -> Any:
        from statsmodels.tsa.arima.model import ARIMA

        model = ARIMA(y_train.values, order=self.order)
        return model.fit()

    def predict(self, model: Any, steps: int) -> np.ndarray:
        forecast = model.forecast(steps=steps)
        return np.array(forecast)


class ARIMA_011(ARIMAModel):
    def __init__(self) -> None:
        super().__init__(order=(0, 1, 1), name="ARIMA(0,1,1)")


class ARIMA_110(ARIMAModel):
    def __init__(self) -> None:
        super().__init__(order=(1, 1, 0), name="ARIMA(1,1,0)")


class ARIMA_212(ARIMAModel):
    def __init__(self) -> None:
        super().__init__(order=(2, 1, 2), name="ARIMA(2,1,2)")


class ARIMA_310(ARIMAModel):
    def __init__(self) -> None:
        super().__init__(order=(3, 1, 0), name="ARIMA(3,1,0)")


class ARIMA_013(ARIMAModel):
    def __init__(self) -> None:
        super().__init__(order=(0, 1, 3), name="ARIMA(0,1,3)")


class ARIMA_211(ARIMAModel):
    def __init__(self) -> None:
        super().__init__(order=(2, 1, 1), name="ARIMA(2,1,1)")


class ARIMA_112(ARIMAModel):
    def __init__(self) -> None:
        super().__init__(order=(1, 1, 2), name="ARIMA(1,1,2)")


class ARIMA_010(ARIMAModel):
    """Random Walk"""

    def __init__(self) -> None:
        super().__init__(order=(0, 1, 0), name="RandomWalk(0,1,0)")


class ARIMA_002(ARIMAModel):
    """MA(2)"""

    def __init__(self) -> None:
        super().__init__(order=(0, 0, 2), name="MA(2)")


class AutoARIMA(TimeSeriesAlgorithm):
    """Auto ARIMA (pmdarima) - 자동 차수 선택"""

    def __init__(self) -> None:
        super().__init__("AutoARIMA")

    def fit(self, y_train: pd.Series, **kwargs: Any) -> Any:
        try:
            from pmdarima import auto_arima

            model = auto_arima(
                y_train.values,
                seasonal=False,
                stepwise=True,
                suppress_warnings=True,
                max_p=5,
                max_q=5,
                max_d=2,
            )
            return model
        except ImportError:
            # pmdarima 미설치 시 fallback
            from statsmodels.tsa.arima.model import ARIMA

            model = ARIMA(y_train.values, order=(1, 1, 1))
            return model.fit()

    def predict(self, model: Any, steps: int) -> np.ndarray:
        if hasattr(model, "predict"):
            forecast = model.predict(n_periods=steps)
            return np.array(forecast)
        return model.forecast(steps=steps)


class SARIMAXModel(TimeSeriesAlgorithm):
    """SARIMAX - 계절성 + 외생변수"""

    def __init__(
        self,
        order: tuple = (1, 1, 1),
        seasonal_order: tuple = (1, 1, 1, 12),
        name: str = "SARIMAX(1,1,1)(1,1,1,12)",
    ):
        super().__init__(name)
        self.order = order
        self.seasonal_order = seasonal_order

    def fit(self, y_train: pd.Series, **kwargs: Any) -> Any:
        from statsmodels.tsa.statespace.sarimax import SARIMAX

        model = SARIMAX(
            y_train.values,
            order=self.order,
            seasonal_order=self.seasonal_order,
            enforce_stationarity=False,
            enforce_invertibility=False,
        )
        return model.fit(disp=False)

    def predict(self, model: Any, steps: int) -> np.ndarray:
        forecast = model.forecast(steps=steps)
        return np.array(forecast)


class SARIMAX_Monthly(SARIMAXModel):
    def __init__(self) -> None:
        super().__init__(
            order=(1, 1, 1),
            seasonal_order=(0, 1, 1, 12),
            name="SARIMAX_Monthly",
        )


class SARIMAX_Weekly(SARIMAXModel):
    def __init__(self) -> None:
        super().__init__(
            order=(1, 1, 1),
            seasonal_order=(1, 0, 1, 7),
            name="SARIMAX_Weekly",
        )


class SARIMAX_Quarterly(SARIMAXModel):
    def __init__(self) -> None:
        super().__init__(
            order=(1, 1, 0),
            seasonal_order=(1, 1, 0, 4),
            name="SARIMAX_Quarterly",
        )


# ──────────────────────────────────────────────
# 2. 지수 평활법 (ETS 계열) - 10종
# ──────────────────────────────────────────────


class SimpleExponentialSmoothing(TimeSeriesAlgorithm):
    """단순 지수 평활법"""

    def __init__(self) -> None:
        super().__init__("SimpleExpSmoothing")

    def fit(self, y_train: pd.Series, **kwargs: Any) -> Any:
        from statsmodels.tsa.holtwinters import SimpleExpSmoothing as SES

        model = SES(y_train.values)
        return model.fit(optimized=True)

    def predict(self, model: Any, steps: int) -> np.ndarray:
        return np.array(model.forecast(steps))


class HoltLinear(TimeSeriesAlgorithm):
    """Holt 선형 추세 모델"""

    def __init__(self) -> None:
        super().__init__("HoltLinear")

    def fit(self, y_train: pd.Series, **kwargs: Any) -> Any:
        from statsmodels.tsa.holtwinters import ExponentialSmoothing

        model = ExponentialSmoothing(y_train.values, trend="add", seasonal=None)
        return model.fit(optimized=True)

    def predict(self, model: Any, steps: int) -> np.ndarray:
        return np.array(model.forecast(steps))


class HoltDamped(TimeSeriesAlgorithm):
    """Holt 감쇠 추세 모델"""

    def __init__(self) -> None:
        super().__init__("HoltDamped")

    def fit(self, y_train: pd.Series, **kwargs: Any) -> Any:
        from statsmodels.tsa.holtwinters import ExponentialSmoothing

        model = ExponentialSmoothing(
            y_train.values, trend="add", damped_trend=True, seasonal=None
        )
        return model.fit(optimized=True)

    def predict(self, model: Any, steps: int) -> np.ndarray:
        return np.array(model.forecast(steps))


class HoltWintersAdditive(TimeSeriesAlgorithm):
    """Holt-Winters 가법 모델"""

    def __init__(self, seasonal_periods: int = 12) -> None:
        super().__init__("HoltWinters_Add")
        self.seasonal_periods = seasonal_periods

    def fit(self, y_train: pd.Series, **kwargs: Any) -> Any:
        from statsmodels.tsa.holtwinters import ExponentialSmoothing

        sp = min(self.seasonal_periods, len(y_train) // 2)
        if sp < 2:
            sp = 2
        model = ExponentialSmoothing(
            y_train.values, trend="add", seasonal="add", seasonal_periods=sp
        )
        return model.fit(optimized=True)

    def predict(self, model: Any, steps: int) -> np.ndarray:
        return np.array(model.forecast(steps))


class HoltWintersMultiplicative(TimeSeriesAlgorithm):
    """Holt-Winters 승법 모델"""

    def __init__(self, seasonal_periods: int = 12) -> None:
        super().__init__("HoltWinters_Mul")
        self.seasonal_periods = seasonal_periods

    def fit(self, y_train: pd.Series, **kwargs: Any) -> Any:
        from statsmodels.tsa.holtwinters import ExponentialSmoothing

        sp = min(self.seasonal_periods, len(y_train) // 2)
        if sp < 2:
            sp = 2
        # 승법 모델은 양수값 필요
        y_vals = y_train.values.copy()
        if (y_vals <= 0).any():
            y_vals = y_vals - y_vals.min() + 1.0
        model = ExponentialSmoothing(
            y_vals, trend="mul", seasonal="mul", seasonal_periods=sp
        )
        return model.fit(optimized=True)

    def predict(self, model: Any, steps: int) -> np.ndarray:
        return np.array(model.forecast(steps))


class HoltWintersDamped(TimeSeriesAlgorithm):
    """Holt-Winters 감쇠 추세"""

    def __init__(self, seasonal_periods: int = 12) -> None:
        super().__init__("HoltWinters_Damped")
        self.seasonal_periods = seasonal_periods

    def fit(self, y_train: pd.Series, **kwargs: Any) -> Any:
        from statsmodels.tsa.holtwinters import ExponentialSmoothing

        sp = min(self.seasonal_periods, len(y_train) // 2)
        if sp < 2:
            sp = 2
        model = ExponentialSmoothing(
            y_train.values,
            trend="add",
            damped_trend=True,
            seasonal="add",
            seasonal_periods=sp,
        )
        return model.fit(optimized=True)

    def predict(self, model: Any, steps: int) -> np.ndarray:
        return np.array(model.forecast(steps))


class ETSModel(TimeSeriesAlgorithm):
    """ETS (Error-Trend-Seasonality) 모델"""

    def __init__(
        self,
        error: str = "add",
        trend: str = "add",
        seasonal: str = "add",
        name: str = "ETS(A,A,A)",
    ) -> None:
        super().__init__(name)
        self.error = error
        self.trend = trend
        self.seasonal = seasonal

    def fit(self, y_train: pd.Series, **kwargs: Any) -> Any:
        from statsmodels.tsa.exponential_smoothing.ets import ETSModel as SM_ETS

        sp = min(12, len(y_train) // 2)
        if sp < 2:
            sp = 2
        model = SM_ETS(
            y_train.values,
            error=self.error,
            trend=self.trend,
            seasonal=self.seasonal,
            seasonal_periods=sp,
        )
        return model.fit(disp=False)

    def predict(self, model: Any, steps: int) -> np.ndarray:
        forecast = model.forecast(steps=steps)
        return np.array(forecast)


class ETS_ANN(ETSModel):
    """ETS(A,N,N) - 단순 지수 평활"""

    def __init__(self) -> None:
        super().__init__(error="add", trend=None, seasonal=None, name="ETS(A,N,N)")

    def fit(self, y_train: pd.Series, **kwargs: Any) -> Any:
        from statsmodels.tsa.exponential_smoothing.ets import ETSModel as SM_ETS

        model = SM_ETS(y_train.values, error="add", trend="add", seasonal=None)
        return model.fit(disp=False)


class ETS_MAN(ETSModel):
    """ETS(M,A,N) - 승법 오차 + 가법 추세"""

    def __init__(self) -> None:
        super().__init__(error="mul", trend="add", seasonal=None, name="ETS(M,A,N)")

    def fit(self, y_train: pd.Series, **kwargs: Any) -> Any:
        from statsmodels.tsa.exponential_smoothing.ets import ETSModel as SM_ETS

        y_vals = y_train.values.copy()
        if (y_vals <= 0).any():
            y_vals = y_vals - y_vals.min() + 1.0
        model = SM_ETS(y_vals, error="mul", trend="add", seasonal=None)
        return model.fit(disp=False)


# ──────────────────────────────────────────────
# 3. 회귀 기반 시계열 - 12종
# ──────────────────────────────────────────────


class _RegressionTSBase(TimeSeriesAlgorithm):
    """회귀 기반 시계열: lag features + sklearn 모델"""

    def __init__(self, name: str, n_lags: int = 5) -> None:
        super().__init__(name)
        self.n_lags = n_lags

    def _create_lag_features(self, y: np.ndarray) -> tuple:
        """lag feature 생성"""
        X_list, y_list = [], []
        for i in range(self.n_lags, len(y)):
            X_list.append(y[i - self.n_lags : i])
            y_list.append(y[i])
        return np.array(X_list), np.array(y_list)

    def _get_model(self) -> Any:
        raise NotImplementedError

    def fit(self, y_train: pd.Series, **kwargs: Any) -> Any:
        y_vals = y_train.values
        X_lag, y_lag = self._create_lag_features(y_vals)
        model = self._get_model()
        model.fit(X_lag, y_lag)
        return {"model": model, "last_values": y_vals[-self.n_lags :]}

    def predict(self, model: Any, steps: int) -> np.ndarray:
        mdl = model["model"]
        last = model["last_values"].copy()
        preds = []
        for _ in range(steps):
            x = last[-self.n_lags :].reshape(1, -1)
            pred = mdl.predict(x)[0]
            preds.append(pred)
            last = np.append(last, pred)
        return np.array(preds)


class LinearTS(_RegressionTSBase):
    def __init__(self) -> None:
        super().__init__("LinearRegression_TS", n_lags=5)

    def _get_model(self) -> Any:
        from sklearn.linear_model import LinearRegression

        return LinearRegression()


class RidgeTS(_RegressionTSBase):
    def __init__(self) -> None:
        super().__init__("Ridge_TS", n_lags=5)

    def _get_model(self) -> Any:
        from sklearn.linear_model import Ridge

        return Ridge(alpha=1.0)


class LassoTS(_RegressionTSBase):
    def __init__(self) -> None:
        super().__init__("Lasso_TS", n_lags=5)

    def _get_model(self) -> Any:
        from sklearn.linear_model import Lasso

        return Lasso(alpha=0.1, max_iter=10000)


class ElasticNetTS(_RegressionTSBase):
    def __init__(self) -> None:
        super().__init__("ElasticNet_TS", n_lags=5)

    def _get_model(self) -> Any:
        from sklearn.linear_model import ElasticNet

        return ElasticNet(alpha=0.1, l1_ratio=0.5, max_iter=10000)


class SVMTS(_RegressionTSBase):
    def __init__(self) -> None:
        super().__init__("SVR_TS", n_lags=5)

    def _get_model(self) -> Any:
        from sklearn.svm import SVR

        return SVR(kernel="rbf", C=1.0)


class KNNTS(_RegressionTSBase):
    def __init__(self) -> None:
        super().__init__("KNN_TS", n_lags=5)

    def _get_model(self) -> Any:
        from sklearn.neighbors import KNeighborsRegressor

        return KNeighborsRegressor(n_neighbors=5)


class BayesianRidgeTS(_RegressionTSBase):
    def __init__(self) -> None:
        super().__init__("BayesianRidge_TS", n_lags=5)

    def _get_model(self) -> Any:
        from sklearn.linear_model import BayesianRidge

        return BayesianRidge()


class HuberTS(_RegressionTSBase):
    def __init__(self) -> None:
        super().__init__("Huber_TS", n_lags=5)

    def _get_model(self) -> Any:
        from sklearn.linear_model import HuberRegressor

        return HuberRegressor(max_iter=200)


class LinearTS_Lag10(_RegressionTSBase):
    def __init__(self) -> None:
        super().__init__("LinearRegression_TS_Lag10", n_lags=10)

    def _get_model(self) -> Any:
        from sklearn.linear_model import LinearRegression

        return LinearRegression()


class RidgeTS_Lag10(_RegressionTSBase):
    def __init__(self) -> None:
        super().__init__("Ridge_TS_Lag10", n_lags=10)

    def _get_model(self) -> Any:
        from sklearn.linear_model import Ridge

        return Ridge(alpha=1.0)


class SVMTS_Linear(_RegressionTSBase):
    def __init__(self) -> None:
        super().__init__("SVR_Linear_TS", n_lags=5)

    def _get_model(self) -> Any:
        from sklearn.svm import SVR

        return SVR(kernel="linear", C=1.0)


class SVMTS_Poly(_RegressionTSBase):
    def __init__(self) -> None:
        super().__init__("SVR_Poly_TS", n_lags=5)

    def _get_model(self) -> Any:
        from sklearn.svm import SVR

        return SVR(kernel="poly", degree=3, C=1.0)


# ──────────────────────────────────────────────
# 4. 트리/앙상블 기반 시계열 - 12종
# ──────────────────────────────────────────────


class RandomForestTS(_RegressionTSBase):
    def __init__(self) -> None:
        super().__init__("RandomForest_TS", n_lags=10)

    def _get_model(self) -> Any:
        from sklearn.ensemble import RandomForestRegressor

        return RandomForestRegressor(n_estimators=100, random_state=42)


class ExtraTreesTS(_RegressionTSBase):
    def __init__(self) -> None:
        super().__init__("ExtraTrees_TS", n_lags=10)

    def _get_model(self) -> Any:
        from sklearn.ensemble import ExtraTreesRegressor

        return ExtraTreesRegressor(n_estimators=100, random_state=42)


class GradientBoostTS(_RegressionTSBase):
    def __init__(self) -> None:
        super().__init__("GradientBoosting_TS", n_lags=10)

    def _get_model(self) -> Any:
        from sklearn.ensemble import GradientBoostingRegressor

        return GradientBoostingRegressor(n_estimators=100, random_state=42)


class XGBoostTS(_RegressionTSBase):
    def __init__(self) -> None:
        super().__init__("XGBoost_TS", n_lags=10)

    def _get_model(self) -> Any:
        from xgboost import XGBRegressor

        return XGBRegressor(
            n_estimators=100, random_state=42, verbosity=0, n_jobs=1
        )


class LightGBMTS(_RegressionTSBase):
    def __init__(self) -> None:
        super().__init__("LightGBM_TS", n_lags=10)

    def _get_model(self) -> Any:
        from lightgbm import LGBMRegressor

        return LGBMRegressor(n_estimators=100, random_state=42, verbose=-1, n_jobs=1)


class AdaBoostTS(_RegressionTSBase):
    def __init__(self) -> None:
        super().__init__("AdaBoost_TS", n_lags=10)

    def _get_model(self) -> Any:
        from sklearn.ensemble import AdaBoostRegressor

        return AdaBoostRegressor(n_estimators=100, random_state=42)


class BaggingTS(_RegressionTSBase):
    def __init__(self) -> None:
        super().__init__("Bagging_TS", n_lags=10)

    def _get_model(self) -> Any:
        from sklearn.ensemble import BaggingRegressor

        return BaggingRegressor(n_estimators=50, random_state=42)


class DecisionTreeTS(_RegressionTSBase):
    def __init__(self) -> None:
        super().__init__("DecisionTree_TS", n_lags=10)

    def _get_model(self) -> Any:
        from sklearn.tree import DecisionTreeRegressor

        return DecisionTreeRegressor(max_depth=10, random_state=42)


class HistGBMTS(_RegressionTSBase):
    def __init__(self) -> None:
        super().__init__("HistGBM_TS", n_lags=10)

    def _get_model(self) -> Any:
        from sklearn.ensemble import HistGradientBoostingRegressor

        return HistGradientBoostingRegressor(max_iter=100, random_state=42)


class RandomForestTS_Lag20(_RegressionTSBase):
    def __init__(self) -> None:
        super().__init__("RandomForest_TS_Lag20", n_lags=20)

    def _get_model(self) -> Any:
        from sklearn.ensemble import RandomForestRegressor

        return RandomForestRegressor(n_estimators=200, random_state=42)


class XGBoostTS_Deep(_RegressionTSBase):
    def __init__(self) -> None:
        super().__init__("XGBoost_TS_Deep", n_lags=10)

    def _get_model(self) -> Any:
        from xgboost import XGBRegressor

        return XGBRegressor(
            n_estimators=200,
            max_depth=8,
            random_state=42,
            verbosity=0,
            n_jobs=1,
        )


class LightGBMTS_Fast(_RegressionTSBase):
    def __init__(self) -> None:
        super().__init__("LightGBM_TS_Fast", n_lags=5)

    def _get_model(self) -> Any:
        from lightgbm import LGBMRegressor

        return LGBMRegressor(
            n_estimators=50, num_leaves=15, random_state=42, verbose=-1, n_jobs=1
        )


# ──────────────────────────────────────────────
# 5. 딥러닝/신경망 기반 - 7종
# ──────────────────────────────────────────────


class MLPTS(_RegressionTSBase):
    def __init__(self) -> None:
        super().__init__("MLP_TS", n_lags=10)

    def _get_model(self) -> Any:
        from sklearn.neural_network import MLPRegressor

        return MLPRegressor(
            hidden_layer_sizes=(100, 50), max_iter=500, random_state=42
        )


class MLPTS_Deep(_RegressionTSBase):
    def __init__(self) -> None:
        super().__init__("MLP_TS_Deep", n_lags=10)

    def _get_model(self) -> Any:
        from sklearn.neural_network import MLPRegressor

        return MLPRegressor(
            hidden_layer_sizes=(200, 100, 50), max_iter=500, random_state=42
        )


class MLPTS_Wide(_RegressionTSBase):
    def __init__(self) -> None:
        super().__init__("MLP_TS_Wide", n_lags=10)

    def _get_model(self) -> Any:
        from sklearn.neural_network import MLPRegressor

        return MLPRegressor(
            hidden_layer_sizes=(500,), max_iter=500, random_state=42
        )


class MLPTS_Small(_RegressionTSBase):
    def __init__(self) -> None:
        super().__init__("MLP_TS_Small", n_lags=5)

    def _get_model(self) -> Any:
        from sklearn.neural_network import MLPRegressor

        return MLPRegressor(
            hidden_layer_sizes=(50,), max_iter=300, random_state=42
        )


class MLPTS_Lag20(_RegressionTSBase):
    def __init__(self) -> None:
        super().__init__("MLP_TS_Lag20", n_lags=20)

    def _get_model(self) -> Any:
        from sklearn.neural_network import MLPRegressor

        return MLPRegressor(
            hidden_layer_sizes=(100, 50), max_iter=500, random_state=42
        )


class MLPTS_Relu(_RegressionTSBase):
    def __init__(self) -> None:
        super().__init__("MLP_TS_ReLU", n_lags=10)

    def _get_model(self) -> Any:
        from sklearn.neural_network import MLPRegressor

        return MLPRegressor(
            hidden_layer_sizes=(100, 50),
            activation="relu",
            max_iter=500,
            random_state=42,
        )


class MLPTS_Tanh(_RegressionTSBase):
    def __init__(self) -> None:
        super().__init__("MLP_TS_Tanh", n_lags=10)

    def _get_model(self) -> Any:
        from sklearn.neural_network import MLPRegressor

        return MLPRegressor(
            hidden_layer_sizes=(100, 50),
            activation="tanh",
            max_iter=500,
            random_state=42,
        )


# ──────────────────────────────────────────────
# 6. 분해/필터 기반 - 5종
# ──────────────────────────────────────────────


class ThetaModel(TimeSeriesAlgorithm):
    """Theta Method"""

    def __init__(self) -> None:
        super().__init__("ThetaMethod")

    def fit(self, y_train: pd.Series, **kwargs: Any) -> Any:
        try:
            from statsmodels.tsa.forecasting.theta import ThetaModel as TM

            model = TM(y_train.values)
            return model.fit(disp=False)
        except Exception:
            from statsmodels.tsa.holtwinters import SimpleExpSmoothing

            model = SimpleExpSmoothing(y_train.values)
            return model.fit(optimized=True)

    def predict(self, model: Any, steps: int) -> np.ndarray:
        if hasattr(model, "forecast"):
            return np.array(model.forecast(steps))
        return np.array(model.forecast(steps))


class NaiveSeasonalModel(TimeSeriesAlgorithm):
    """Naive Seasonal (Seasonal period 반복)"""

    def __init__(self, period: int = 12) -> None:
        super().__init__("NaiveSeasonal")
        self.period = period

    def fit(self, y_train: pd.Series, **kwargs: Any) -> Any:
        return y_train.values

    def predict(self, model: Any, steps: int) -> np.ndarray:
        period = min(self.period, len(model))
        last_season = model[-period:]
        repeats = (steps // period) + 1
        return np.tile(last_season, repeats)[:steps]


class NaiveMeanModel(TimeSeriesAlgorithm):
    """Naive Mean (평균으로 예측)"""

    def __init__(self) -> None:
        super().__init__("NaiveMean")

    def fit(self, y_train: pd.Series, **kwargs: Any) -> Any:
        return float(y_train.mean())

    def predict(self, model: Any, steps: int) -> np.ndarray:
        return np.full(steps, model)


class NaiveDriftModel(TimeSeriesAlgorithm):
    """Naive Drift (선형 추세 연장)"""

    def __init__(self) -> None:
        super().__init__("NaiveDrift")

    def fit(self, y_train: pd.Series, **kwargs: Any) -> Any:
        vals = y_train.values
        n = len(vals)
        slope = (vals[-1] - vals[0]) / max(n - 1, 1)
        return {"last_value": vals[-1], "slope": slope}

    def predict(self, model: Any, steps: int) -> np.ndarray:
        return np.array(
            [model["last_value"] + model["slope"] * (i + 1) for i in range(steps)]
        )


class MovingAverageModel(TimeSeriesAlgorithm):
    """Moving Average Forecast"""

    def __init__(self, window: int = 7) -> None:
        super().__init__(f"MovingAvg_{window}")
        self.window = window

    def fit(self, y_train: pd.Series, **kwargs: Any) -> Any:
        return y_train.values

    def predict(self, model: Any, steps: int) -> np.ndarray:
        window = min(self.window, len(model))
        last_window = model[-window:]
        preds = []
        current = list(last_window)
        for _ in range(steps):
            pred = np.mean(current[-window:])
            preds.append(pred)
            current.append(pred)
        return np.array(preds)


# ──────────────────────────────────────────────
# 알고리즘 수집 함수
# ──────────────────────────────────────────────


def get_all_timeseries_algorithms() -> List[TimeSeriesAlgorithm]:
    """
    시계열 분석 전용 알고리즘 61종 반환

    Returns:
        TimeSeriesAlgorithm 인스턴스 리스트
    """
    algorithms: List[TimeSeriesAlgorithm] = []

    # 1. 통계 기반 ARIMA 계열 (15종)
    arima_models: List[TimeSeriesAlgorithm] = [
        ARIMAModel(),          # ARIMA(1,1,1)
        ARIMA_011(),           # ARIMA(0,1,1)
        ARIMA_110(),           # ARIMA(1,1,0)
        ARIMA_212(),           # ARIMA(2,1,2)
        ARIMA_310(),           # ARIMA(3,1,0)
        ARIMA_013(),           # ARIMA(0,1,3)
        ARIMA_211(),           # ARIMA(2,1,1)
        ARIMA_112(),           # ARIMA(1,1,2)
        ARIMA_010(),           # Random Walk
        ARIMA_002(),           # MA(2)
        AutoARIMA(),           # Auto ARIMA
        SARIMAXModel(),        # SARIMAX(1,1,1)(1,1,1,12)
        SARIMAX_Monthly(),     # SARIMAX Monthly
        SARIMAX_Weekly(),      # SARIMAX Weekly
        SARIMAX_Quarterly(),   # SARIMAX Quarterly
    ]

    # 2. 지수 평활법 ETS 계열 (10종)
    ets_models: List[TimeSeriesAlgorithm] = [
        SimpleExponentialSmoothing(),
        HoltLinear(),
        HoltDamped(),
        HoltWintersAdditive(),
        HoltWintersMultiplicative(),
        HoltWintersDamped(),
        ETSModel(),            # ETS(A,A,A)
        ETS_ANN(),             # ETS(A,N,N)
        ETS_MAN(),             # ETS(M,A,N)
        ThetaModel(),          # Theta Method
    ]

    # 3. 회귀 기반 시계열 (12종)
    regression_ts: List[TimeSeriesAlgorithm] = [
        LinearTS(),
        RidgeTS(),
        LassoTS(),
        ElasticNetTS(),
        SVMTS(),
        KNNTS(),
        BayesianRidgeTS(),
        HuberTS(),
        LinearTS_Lag10(),
        RidgeTS_Lag10(),
        SVMTS_Linear(),
        SVMTS_Poly(),
    ]

    # 4. 트리/앙상블 기반 (12종)
    tree_ts: List[TimeSeriesAlgorithm] = [
        RandomForestTS(),
        ExtraTreesTS(),
        GradientBoostTS(),
        XGBoostTS(),
        LightGBMTS(),
        AdaBoostTS(),
        BaggingTS(),
        DecisionTreeTS(),
        HistGBMTS(),
        RandomForestTS_Lag20(),
        XGBoostTS_Deep(),
        LightGBMTS_Fast(),
    ]

    # 5. 신경망 기반 (7종)
    nn_ts: List[TimeSeriesAlgorithm] = [
        MLPTS(),
        MLPTS_Deep(),
        MLPTS_Wide(),
        MLPTS_Small(),
        MLPTS_Lag20(),
        MLPTS_Relu(),
        MLPTS_Tanh(),
    ]

    # 6. 분해/필터 기반 (5종) - ThetaModel은 ETS에 포함
    decompose_ts: List[TimeSeriesAlgorithm] = [
        NaiveSeasonalModel(),
        NaiveMeanModel(),
        NaiveDriftModel(),
        MovingAverageModel(window=7),
        MovingAverageModel(window=14),
    ]

    algorithms.extend(arima_models)       # 15
    algorithms.extend(ets_models)         # 10
    algorithms.extend(regression_ts)      # 12
    algorithms.extend(tree_ts)            # 12
    algorithms.extend(nn_ts)              # 7
    algorithms.extend(decompose_ts)       # 5
    # Total: 61

    logger.info(
        f"시계열 알고리즘 초기화: ARIMA={len(arima_models)}, "
        f"ETS={len(ets_models)}, Regression={len(regression_ts)}, "
        f"Tree={len(tree_ts)}, NN={len(nn_ts)}, "
        f"Decompose={len(decompose_ts)} = {len(algorithms)}종"
    )

    return algorithms
