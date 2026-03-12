"""
EDA (Exploratory Data Analysis) Service
현황분석 - 데이터 분포, 상관행렬, 통계 요약 제공
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from loguru import logger


class EDAService:
    """현황분석 (Exploratory Data Analysis) 서비스"""

    def analyze(
        self,
        data: List[Dict[str, Any]],
        target_column: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        데이터 현황분석 수행

        Args:
            data: 입력 데이터
            target_column: 타겟 컬럼 (선택)

        Returns:
            현황분석 결과 (분포, 상관행렬, 이상치 등)
        """
        logger.info("현황분석(EDA) 시작")
        df = pd.DataFrame(data)

        result: Dict[str, Any] = {
            "summary_statistics": self._summary_statistics(df),
            "distribution": self._distribution_analysis(df),
            "correlation_matrix": self._correlation_matrix(df),
            "missing_analysis": self._missing_analysis(df),
            "outlier_analysis": self._outlier_analysis(df),
        }

        if target_column and target_column in df.columns:
            result["target_distribution"] = self._target_distribution(
                df, target_column
            )

        logger.info("현황분석(EDA) 완료")
        return result

    def _summary_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """기술통계량"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(exclude=[np.number]).columns.tolist()

        stats: Dict[str, Any] = {
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "numeric_columns": len(numeric_cols),
            "categorical_columns": len(categorical_cols),
            "memory_usage_bytes": int(df.memory_usage(deep=True).sum()),
        }

        # 수치형 기술통계
        if numeric_cols:
            desc = df[numeric_cols].describe().to_dict()
            stats["numeric_stats"] = {
                col: {k: round(float(v), 4) for k, v in col_stats.items()}
                for col, col_stats in desc.items()
            }

        # 범주형 기술통계
        if categorical_cols:
            stats["categorical_stats"] = {}
            for col in categorical_cols:
                stats["categorical_stats"][col] = {
                    "unique_count": int(df[col].nunique()),
                    "top_value": str(df[col].mode().iloc[0]) if not df[col].mode().empty else None,
                    "top_frequency": int(df[col].value_counts().iloc[0]) if not df[col].empty else 0,
                }

        return stats

    def _distribution_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """데이터 분포 분석 (히스토그램 bin 데이터)"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        distributions: Dict[str, Any] = {}

        for col in numeric_cols:
            series = df[col].dropna()
            if len(series) == 0:
                continue

            # 히스토그램 빈 계산
            counts, bin_edges = np.histogram(series, bins=min(20, len(series)))
            distributions[col] = {
                "bins": [round(float(e), 4) for e in bin_edges],
                "counts": [int(c) for c in counts],
                "skewness": round(float(series.skew()), 4),
                "kurtosis": round(float(series.kurtosis()), 4),
                "normality": "normal" if abs(series.skew()) < 0.5 else (
                    "right_skewed" if series.skew() > 0 else "left_skewed"
                ),
            }

        return distributions

    def _correlation_matrix(self, df: pd.DataFrame) -> Dict[str, Any]:
        """상관행렬 (Pearson)"""
        numeric_df = df.select_dtypes(include=[np.number])
        if numeric_df.empty or len(numeric_df.columns) < 2:
            return {"message": "수치형 컬럼이 2개 미만으로 상관분석 불가"}

        corr = numeric_df.corr(method="pearson")

        # 강한 상관관계 추출
        strong_correlations = []
        cols = corr.columns.tolist()
        for i in range(len(cols)):
            for j in range(i + 1, len(cols)):
                val = float(corr.iloc[i, j])
                if abs(val) >= 0.5:
                    strong_correlations.append({
                        "var1": cols[i],
                        "var2": cols[j],
                        "correlation": round(val, 4),
                        "strength": "strong" if abs(val) >= 0.7 else "moderate",
                    })

        strong_correlations.sort(key=lambda x: abs(x["correlation"]), reverse=True)

        return {
            "matrix": {
                col: {c2: round(float(corr.loc[col, c2]), 4) for c2 in cols}
                for col in cols
            },
            "strong_correlations": strong_correlations,
        }

    def _missing_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """결측치 분석"""
        missing = df.isnull().sum()
        total = len(df)

        columns_with_missing = []
        for col in df.columns:
            count = int(missing[col])
            if count > 0:
                columns_with_missing.append({
                    "column": col,
                    "missing_count": count,
                    "missing_ratio": round(count / total * 100, 2),
                })

        columns_with_missing.sort(key=lambda x: x["missing_ratio"], reverse=True)

        return {
            "total_missing": int(missing.sum()),
            "total_cells": int(total * len(df.columns)),
            "overall_missing_ratio": round(
                float(missing.sum()) / (total * len(df.columns)) * 100, 2
            ) if total > 0 else 0,
            "columns_with_missing": columns_with_missing,
        }

    def _outlier_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """이상치 분석 (IQR 방법)"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        outliers: Dict[str, Any] = {}

        for col in numeric_cols:
            series = df[col].dropna()
            if len(series) == 0:
                continue

            q1 = float(series.quantile(0.25))
            q3 = float(series.quantile(0.75))
            iqr = q3 - q1
            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr

            outlier_count = int(((series < lower) | (series > upper)).sum())
            if outlier_count > 0:
                outliers[col] = {
                    "outlier_count": outlier_count,
                    "outlier_ratio": round(outlier_count / len(series) * 100, 2),
                    "lower_bound": round(lower, 4),
                    "upper_bound": round(upper, 4),
                    "iqr": round(iqr, 4),
                }

        return outliers

    def _target_distribution(
        self, df: pd.DataFrame, target_column: str
    ) -> Dict[str, Any]:
        """타겟 변수 분포 상세"""
        series = df[target_column].dropna()
        result: Dict[str, Any] = {"column": target_column}

        if pd.api.types.is_numeric_dtype(series):
            result["type"] = "numeric"
            result["mean"] = round(float(series.mean()), 4)
            result["median"] = round(float(series.median()), 4)
            result["std"] = round(float(series.std()), 4)

            # 분위수
            result["percentiles"] = {
                f"p{p}": round(float(series.quantile(p / 100)), 4)
                for p in [10, 25, 50, 75, 90]
            }
        else:
            result["type"] = "categorical"
            vc = series.value_counts()
            result["class_distribution"] = {
                str(k): int(v) for k, v in vc.items()
            }
            result["class_balance"] = round(
                float(vc.min() / vc.max()), 4
            ) if len(vc) > 1 else 1.0

        return result
