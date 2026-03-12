"""
Feature Engineering for Time Series
시계열 데이터에서 500+ 파생변수 자동 생성

파생변수 카테고리:
- Lag Features (1~30): 30개
- Rolling Statistics (mean/std/min/max/median x window 3,5,7,14,21,30): 30개
- Expanding Statistics: 5개
- Differencing (1차, 2차, pct_change): 3개
- Calendar Features (day_of_week, month, quarter 등): ~20개
- Cyclical Encoding (sin/cos): 6개
- Interaction Features (lag x rolling): ~60개
- Polynomial Features (lag^2, lag^3): ~60개
- Exponential Weighted Mean: 5개
- 통계 파생 (skew, kurtosis, entropy): ~15개
- Ratio Features: ~20개
- 추세/모멘텀 지표: ~30개
- 기술적 지표(금융): ~20개
총 ~500개+
"""
import warnings
from typing import Optional

import numpy as np
import pandas as pd
from loguru import logger

warnings.filterwarnings("ignore", category=RuntimeWarning)


class FeatureEngineer:
    """시계열 데이터 자동 파생변수 생성 엔진"""

    # 롤링 윈도우 크기
    WINDOWS = [3, 5, 7, 14, 21, 30]
    # Lag 범위
    MAX_LAG = 30
    # EWM spans
    EWM_SPANS = [3, 7, 14, 21, 30]

    @staticmethod
    def generate_all_features(
        df: pd.DataFrame,
        target_column: str,
        date_column: Optional[str] = None,
        max_features: int = 500,
    ) -> pd.DataFrame:
        """
        시계열 데이터에서 파생변수 자동 생성

        Args:
            df: 원본 데이터프레임
            target_column: 타겟 컬럼명
            date_column: 날짜 컬럼명 (없으면 index 사용)
            max_features: 최대 파생변수 수

        Returns:
            파생변수가 추가된 데이터프레임
        """
        result = df.copy()
        y = df[target_column]
        feature_count = 0

        logger.info(f"파생변수 생성 시작: target={target_column}, rows={len(df)}")

        # 1. Lag Features (30개)
        feature_count = FeatureEngineer._add_lag_features(result, y, target_column)
        logger.debug(f"  Lag features: {feature_count}개")

        # 2. Rolling Statistics (30개)
        count = FeatureEngineer._add_rolling_features(result, y, target_column)
        feature_count += count
        logger.debug(f"  Rolling features: {count}개")

        # 3. Expanding Statistics (5개)
        count = FeatureEngineer._add_expanding_features(result, y, target_column)
        feature_count += count

        # 4. Differencing (3개)
        count = FeatureEngineer._add_diff_features(result, y, target_column)
        feature_count += count

        # 5. Calendar Features (날짜 있을 때)
        if date_column and date_column in df.columns:
            count = FeatureEngineer._add_calendar_features(
                result, df[date_column]
            )
            feature_count += count
            logger.debug(f"  Calendar features: {count}개")
        else:
            # 인덱스 기반 위치 피처
            count = FeatureEngineer._add_index_features(result)
            feature_count += count

        # 6. EWM Features (5개)
        count = FeatureEngineer._add_ewm_features(result, y, target_column)
        feature_count += count

        # 7. Interaction Features (lag x rolling)
        count = FeatureEngineer._add_interaction_features(result, target_column)
        feature_count += count

        # 8. Polynomial Features (lag^2, lag^3)
        count = FeatureEngineer._add_polynomial_features(result, target_column)
        feature_count += count

        # 9. Statistical Features
        count = FeatureEngineer._add_statistical_features(result, y, target_column)
        feature_count += count

        # 10. Ratio Features
        count = FeatureEngineer._add_ratio_features(result, y, target_column)
        feature_count += count

        # 11. Momentum/Trend Features
        count = FeatureEngineer._add_momentum_features(result, y, target_column)
        feature_count += count

        # 12. Technical Indicators
        count = FeatureEngineer._add_technical_features(result, y, target_column)
        feature_count += count

        # NaN 처리: 파생변수 초기 구간은 NaN이 불가피
        result = result.bfill().fillna(0)

        # 최대 피처 수 제한
        feature_cols = [
            c for c in result.columns if c != target_column and c != date_column
        ]
        if len(feature_cols) > max_features:
            # 분산 기반으로 상위 max_features 선택
            variances = result[feature_cols].var()
            top_features = variances.nlargest(max_features).index.tolist()
            keep_cols = [target_column] + top_features
            if date_column and date_column in result.columns:
                keep_cols.insert(0, date_column)
            result = result[keep_cols]
            logger.info(f"  피처 수 제한: {len(feature_cols)} -> {max_features}")

        total = len([c for c in result.columns if c != target_column and c != date_column])
        logger.info(f"파생변수 생성 완료: {total}개 피처")

        return result

    # ─── 1. Lag Features ─────────────────────────

    @staticmethod
    def _add_lag_features(
        df: pd.DataFrame, y: pd.Series, target: str
    ) -> int:
        count = 0
        for lag in range(1, FeatureEngineer.MAX_LAG + 1):
            df[f"{target}_lag_{lag}"] = y.shift(lag)
            count += 1
        return count

    # ─── 2. Rolling Statistics ───────────────────

    @staticmethod
    def _add_rolling_features(
        df: pd.DataFrame, y: pd.Series, target: str
    ) -> int:
        count = 0
        for w in FeatureEngineer.WINDOWS:
            rolling = y.rolling(window=w, min_periods=1)
            df[f"{target}_rolling_mean_{w}"] = rolling.mean()
            df[f"{target}_rolling_std_{w}"] = rolling.std()
            df[f"{target}_rolling_min_{w}"] = rolling.min()
            df[f"{target}_rolling_max_{w}"] = rolling.max()
            df[f"{target}_rolling_median_{w}"] = rolling.median()
            count += 5
        return count

    # ─── 3. Expanding Statistics ─────────────────

    @staticmethod
    def _add_expanding_features(
        df: pd.DataFrame, y: pd.Series, target: str
    ) -> int:
        expanding = y.expanding(min_periods=1)
        df[f"{target}_expanding_mean"] = expanding.mean()
        df[f"{target}_expanding_std"] = expanding.std()
        df[f"{target}_expanding_min"] = expanding.min()
        df[f"{target}_expanding_max"] = expanding.max()
        df[f"{target}_expanding_median"] = expanding.median()
        return 5

    # ─── 4. Differencing ────────────────────────

    @staticmethod
    def _add_diff_features(
        df: pd.DataFrame, y: pd.Series, target: str
    ) -> int:
        df[f"{target}_diff_1"] = y.diff(1)
        df[f"{target}_diff_2"] = y.diff(2)
        df[f"{target}_pct_change"] = y.pct_change()
        return 3

    # ─── 5. Calendar Features ───────────────────

    @staticmethod
    def _add_calendar_features(
        df: pd.DataFrame, date_col: pd.Series
    ) -> int:
        dt = pd.to_datetime(date_col, errors="coerce")
        count = 0

        df["year"] = dt.dt.year
        df["month"] = dt.dt.month
        df["day"] = dt.dt.day
        df["day_of_week"] = dt.dt.dayofweek
        df["day_of_year"] = dt.dt.dayofyear
        df["week_of_year"] = dt.dt.isocalendar().week.astype(int).values
        df["quarter"] = dt.dt.quarter
        df["is_weekend"] = (dt.dt.dayofweek >= 5).astype(int)
        df["is_month_start"] = dt.dt.is_month_start.astype(int)
        df["is_month_end"] = dt.dt.is_month_end.astype(int)
        df["is_quarter_start"] = dt.dt.is_quarter_start.astype(int)
        df["is_quarter_end"] = dt.dt.is_quarter_end.astype(int)
        df["is_year_start"] = dt.dt.is_year_start.astype(int)
        df["is_year_end"] = dt.dt.is_year_end.astype(int)
        count += 14

        # Cyclical Encoding
        df["month_sin"] = np.sin(2 * np.pi * dt.dt.month / 12)
        df["month_cos"] = np.cos(2 * np.pi * dt.dt.month / 12)
        df["dow_sin"] = np.sin(2 * np.pi * dt.dt.dayofweek / 7)
        df["dow_cos"] = np.cos(2 * np.pi * dt.dt.dayofweek / 7)
        df["doy_sin"] = np.sin(2 * np.pi * dt.dt.dayofyear / 365)
        df["doy_cos"] = np.cos(2 * np.pi * dt.dt.dayofyear / 365)
        count += 6

        # Hour features (시간 데이터가 있을 때)
        if dt.dt.hour.sum() > 0:
            df["hour"] = dt.dt.hour
            df["minute"] = dt.dt.minute
            df["hour_sin"] = np.sin(2 * np.pi * dt.dt.hour / 24)
            df["hour_cos"] = np.cos(2 * np.pi * dt.dt.hour / 24)
            count += 4

        return count

    @staticmethod
    def _add_index_features(df: pd.DataFrame) -> int:
        """날짜 컬럼이 없을 때 인덱스 기반 피처"""
        n = len(df)
        df["position"] = np.arange(n)
        df["position_norm"] = np.arange(n) / max(n - 1, 1)
        df["position_sin"] = np.sin(2 * np.pi * np.arange(n) / max(n, 1))
        df["position_cos"] = np.cos(2 * np.pi * np.arange(n) / max(n, 1))
        return 4

    # ─── 6. EWM Features ────────────────────────

    @staticmethod
    def _add_ewm_features(
        df: pd.DataFrame, y: pd.Series, target: str
    ) -> int:
        count = 0
        for span in FeatureEngineer.EWM_SPANS:
            df[f"{target}_ewm_{span}"] = y.ewm(span=span, min_periods=1).mean()
            count += 1
        return count

    # ─── 7. Interaction Features ────────────────

    @staticmethod
    def _add_interaction_features(df: pd.DataFrame, target: str) -> int:
        count = 0
        lags = [1, 3, 5, 7, 14]
        windows = [3, 7, 14]

        for lag in lags:
            lag_col = f"{target}_lag_{lag}"
            if lag_col not in df.columns:
                continue
            for w in windows:
                mean_col = f"{target}_rolling_mean_{w}"
                if mean_col not in df.columns:
                    continue
                # lag * rolling_mean
                df[f"{target}_lag{lag}_x_rmean{w}"] = df[lag_col] * df[mean_col]
                count += 1
                # lag - rolling_mean (deviation)
                df[f"{target}_lag{lag}_dev_rmean{w}"] = df[lag_col] - df[mean_col]
                count += 1
                # lag / rolling_mean (ratio)
                with np.errstate(divide="ignore", invalid="ignore"):
                    ratio = df[lag_col] / df[mean_col].replace(0, np.nan)
                df[f"{target}_lag{lag}_ratio_rmean{w}"] = ratio
                count += 1

        return count

    # ─── 8. Polynomial Features ─────────────────

    @staticmethod
    def _add_polynomial_features(df: pd.DataFrame, target: str) -> int:
        count = 0
        lags = [1, 2, 3, 5, 7, 10, 14, 21, 30]

        for lag in lags:
            lag_col = f"{target}_lag_{lag}"
            if lag_col not in df.columns:
                continue
            # 제곱
            df[f"{target}_lag{lag}_sq"] = df[lag_col] ** 2
            count += 1
            # 세제곱
            df[f"{target}_lag{lag}_cb"] = df[lag_col] ** 3
            count += 1
            # 제곱근 (양수만)
            df[f"{target}_lag{lag}_sqrt"] = np.sqrt(np.abs(df[lag_col]))
            count += 1
            # 로그 (양수만)
            df[f"{target}_lag{lag}_log"] = np.log1p(np.abs(df[lag_col]))
            count += 1

        return count

    # ─── 9. Statistical Features ────────────────

    @staticmethod
    def _add_statistical_features(
        df: pd.DataFrame, y: pd.Series, target: str
    ) -> int:
        count = 0
        for w in [7, 14, 30]:
            rolling = y.rolling(window=w, min_periods=1)

            # Skewness
            df[f"{target}_skew_{w}"] = rolling.skew()
            count += 1

            # Kurtosis
            df[f"{target}_kurt_{w}"] = rolling.kurt()
            count += 1

            # Range
            df[f"{target}_range_{w}"] = rolling.max() - rolling.min()
            count += 1

            # IQR (근사)
            q75 = rolling.quantile(0.75)
            q25 = rolling.quantile(0.25)
            df[f"{target}_iqr_{w}"] = q75 - q25
            count += 1

            # CV (변동계수)
            mean_r = rolling.mean()
            std_r = rolling.std()
            with np.errstate(divide="ignore", invalid="ignore"):
                cv = std_r / mean_r.replace(0, np.nan)
            df[f"{target}_cv_{w}"] = cv
            count += 1

        return count

    # ─── 10. Ratio Features ─────────────────────

    @staticmethod
    def _add_ratio_features(
        df: pd.DataFrame, y: pd.Series, target: str
    ) -> int:
        count = 0

        # lag 간 비율
        lag_pairs = [(1, 7), (1, 14), (1, 30), (7, 14), (7, 30), (14, 30)]
        for l1, l2 in lag_pairs:
            c1, c2 = f"{target}_lag_{l1}", f"{target}_lag_{l2}"
            if c1 in df.columns and c2 in df.columns:
                with np.errstate(divide="ignore", invalid="ignore"):
                    df[f"{target}_ratio_lag{l1}_lag{l2}"] = (
                        df[c1] / df[c2].replace(0, np.nan)
                    )
                count += 1

        # 현재값 대비 rolling mean 비율
        for w in [7, 14, 30]:
            mc = f"{target}_rolling_mean_{w}"
            if mc in df.columns:
                with np.errstate(divide="ignore", invalid="ignore"):
                    df[f"{target}_vs_rmean_{w}"] = y / df[mc].replace(0, np.nan)
                count += 1

        # 현재값 대비 expanding mean 비율
        ec = f"{target}_expanding_mean"
        if ec in df.columns:
            with np.errstate(divide="ignore", invalid="ignore"):
                df[f"{target}_vs_exp_mean"] = y / df[ec].replace(0, np.nan)
            count += 1

        return count

    # ─── 11. Momentum/Trend Features ────────────

    @staticmethod
    def _add_momentum_features(
        df: pd.DataFrame, y: pd.Series, target: str
    ) -> int:
        count = 0

        # Rate of Change (ROC)
        for period in [1, 3, 7, 14, 30]:
            shifted = y.shift(period)
            with np.errstate(divide="ignore", invalid="ignore"):
                roc = (y - shifted) / shifted.replace(0, np.nan)
            df[f"{target}_roc_{period}"] = roc
            count += 1

        # Acceleration (2nd derivative)
        diff1 = y.diff()
        df[f"{target}_acceleration"] = diff1.diff()
        count += 1

        # Cumulative sum
        df[f"{target}_cumsum"] = y.cumsum()
        count += 1

        # Z-score (rolling)
        for w in [7, 14, 30]:
            mean_r = y.rolling(w, min_periods=1).mean()
            std_r = y.rolling(w, min_periods=1).std()
            with np.errstate(divide="ignore", invalid="ignore"):
                df[f"{target}_zscore_{w}"] = (y - mean_r) / std_r.replace(0, np.nan)
            count += 1

        # Sign changes
        sign = np.sign(y.diff())
        df[f"{target}_sign_change"] = (sign != sign.shift(1)).astype(int)
        count += 1

        # Streak (연속 상승/하락)
        diff_sign = np.sign(y.diff())
        streak = diff_sign.copy()
        for i in range(1, len(streak)):
            if streak.iloc[i] == streak.iloc[i - 1] and streak.iloc[i] != 0:
                streak.iloc[i] = streak.iloc[i - 1] + np.sign(streak.iloc[i])
        df[f"{target}_streak"] = streak
        count += 1

        return count

    # ─── 12. Technical Indicators ───────────────

    @staticmethod
    def _add_technical_features(
        df: pd.DataFrame, y: pd.Series, target: str
    ) -> int:
        """금융 기술적 분석 지표 (시계열 범용)"""
        count = 0

        # Bollinger Bands
        for w in [7, 14]:
            ma = y.rolling(w, min_periods=1).mean()
            std = y.rolling(w, min_periods=1).std()
            df[f"{target}_bb_upper_{w}"] = ma + 2 * std
            df[f"{target}_bb_lower_{w}"] = ma - 2 * std
            df[f"{target}_bb_width_{w}"] = 4 * std
            with np.errstate(divide="ignore", invalid="ignore"):
                df[f"{target}_bb_position_{w}"] = (y - df[f"{target}_bb_lower_{w}"]) / (
                    df[f"{target}_bb_width_{w}"].replace(0, np.nan)
                )
            count += 4

        # RSI (Relative Strength Index)
        for period in [7, 14]:
            delta = y.diff()
            gain = delta.where(delta > 0, 0.0).rolling(period, min_periods=1).mean()
            loss = (-delta.where(delta < 0, 0.0)).rolling(period, min_periods=1).mean()
            with np.errstate(divide="ignore", invalid="ignore"):
                rs = gain / loss.replace(0, np.nan)
            df[f"{target}_rsi_{period}"] = 100 - (100 / (1 + rs))
            count += 1

        # MACD
        ema_12 = y.ewm(span=12, min_periods=1).mean()
        ema_26 = y.ewm(span=26, min_periods=1).mean()
        macd = ema_12 - ema_26
        signal = macd.ewm(span=9, min_periods=1).mean()
        df[f"{target}_macd"] = macd
        df[f"{target}_macd_signal"] = signal
        df[f"{target}_macd_hist"] = macd - signal
        count += 3

        # ATR (Average True Range 근사 - High/Low 없이)
        for w in [7, 14]:
            tr = y.diff().abs()
            df[f"{target}_atr_{w}"] = tr.rolling(w, min_periods=1).mean()
            count += 1

        return count
