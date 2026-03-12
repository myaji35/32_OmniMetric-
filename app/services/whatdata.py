"""
WhatDataAI Analyzer
데이터 사전 분석 - AI 활용 가능한 분석 방법 자동 선별
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List
from loguru import logger


class WhatDataAnalyzer:
    """WhatDataAI 사전분석 엔진"""

    def analyze(self, data: List[Dict[str, Any]], target_column: str) -> Dict[str, Any]:
        """
        데이터 특성 분석 및 적합 분석유형 추천

        Args:
            data: 입력 데이터
            target_column: 타겟 컬럼

        Returns:
            분석 결과 및 추천
        """
        logger.info("WhatDataAI 분석 시작")
        df = pd.DataFrame(data)

        if target_column not in df.columns:
            raise ValueError(f"타겟 컬럼 '{target_column}'을 찾을 수 없습니다.")

        y = df[target_column]
        X = df.drop(columns=[target_column])

        # 1. 데이터 기본 정보
        data_info = {
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "feature_columns": len(X.columns),
            "target_column": target_column,
        }

        # 2. 컬럼별 상세 분석
        column_analysis = {}
        for col in df.columns:
            col_info = self._analyze_column(df[col])
            column_analysis[col] = col_info

        # 3. 타겟 변수 분석
        target_analysis = self._analyze_target(y)

        # 4. 적합 분석유형 추천
        recommendations = self._recommend_analysis_types(y, X, df)

        # 5. 데이터 품질 점수
        quality_score = self._calculate_quality_score(df)

        return {
            "data_info": data_info,
            "column_analysis": column_analysis,
            "target_analysis": target_analysis,
            "recommendations": recommendations,
            "quality_score": quality_score,
        }

    def _analyze_column(self, series: pd.Series) -> Dict[str, Any]:
        """개별 컬럼 분석"""
        info: Dict[str, Any] = {
            "dtype": str(series.dtype),
            "missing_count": int(series.isnull().sum()),
            "missing_ratio": float(series.isnull().mean()),
            "unique_count": int(series.nunique()),
        }

        if pd.api.types.is_numeric_dtype(series):
            info["type"] = "numeric"
            info["mean"] = float(series.mean()) if not series.isnull().all() else None
            info["std"] = float(series.std()) if not series.isnull().all() else None
            info["min"] = float(series.min()) if not series.isnull().all() else None
            info["max"] = float(series.max()) if not series.isnull().all() else None
            info["skewness"] = float(series.skew()) if not series.isnull().all() else None
        else:
            info["type"] = "categorical"
            info["top_values"] = series.value_counts().head(5).to_dict()

        return info

    def _analyze_target(self, y: pd.Series) -> Dict[str, Any]:
        """타겟 변수 분석"""
        analysis: Dict[str, Any] = {
            "dtype": str(y.dtype),
            "unique_values": int(y.nunique()),
        }

        if pd.api.types.is_numeric_dtype(y):
            analysis["is_continuous"] = y.nunique() > 10
            analysis["is_binary"] = y.nunique() == 2
            analysis["is_multiclass"] = 2 < y.nunique() <= 20

            if analysis["is_continuous"]:
                analysis["suggested_type"] = "regression"
            elif analysis["is_binary"]:
                analysis["suggested_type"] = "classification"
            else:
                analysis["suggested_type"] = "multiclass"
        else:
            analysis["is_categorical"] = True
            analysis["suggested_type"] = (
                "classification" if y.nunique() == 2 else "multiclass"
            )

        return analysis

    def _recommend_analysis_types(
        self, y: pd.Series, X: pd.DataFrame, df: pd.DataFrame
    ) -> List[Dict[str, Any]]:
        """분석유형 추천"""
        recommendations = []

        # 시계열 감지
        has_date_column = any(
            pd.api.types.is_datetime64_any_dtype(df[col])
            or "date" in col.lower()
            or "time" in col.lower()
            for col in df.columns
        )

        n_unique = y.nunique()

        if pd.api.types.is_numeric_dtype(y) and n_unique > 10:
            recommendations.append({
                "type": "regression",
                "confidence": 0.9,
                "reason": f"타겟이 연속형 수치 ({n_unique}개 고유값)",
                "algorithms_available": 60,
            })

        if n_unique == 2:
            recommendations.append({
                "type": "classification",
                "confidence": 0.95,
                "reason": f"타겟이 이진값 ({list(y.unique()[:5])})",
                "algorithms_available": 17,
            })

        if 2 < n_unique <= 20:
            recommendations.append({
                "type": "multiclass",
                "confidence": 0.85,
                "reason": f"타겟이 {n_unique}개 클래스",
                "algorithms_available": 17,
            })

        if has_date_column:
            recommendations.append({
                "type": "timeseries",
                "confidence": 0.7,
                "reason": "날짜/시간 컬럼 감지됨",
                "algorithms_available": 61,
            })

        # confidence 순 정렬
        recommendations.sort(key=lambda x: x["confidence"], reverse=True)
        return recommendations

    def _calculate_quality_score(self, df: pd.DataFrame) -> Dict[str, Any]:
        """데이터 품질 점수 산출"""
        total_cells = df.shape[0] * df.shape[1]
        missing_cells = df.isnull().sum().sum()
        completeness = 1 - (missing_cells / total_cells) if total_cells > 0 else 0

        # 중복 행 비율
        duplicate_ratio = df.duplicated().mean()

        score = completeness * 0.6 + (1 - duplicate_ratio) * 0.4

        return {
            "overall_score": round(float(score) * 100, 1),
            "completeness": round(float(completeness) * 100, 1),
            "duplicate_ratio": round(float(duplicate_ratio) * 100, 1),
            "missing_cells": int(missing_cells),
        }
