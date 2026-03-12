"""
Data Preprocessor
데이터 전처리 모듈 (TournamentEngine에서 분리)
"""
import pandas as pd
import numpy as np
from typing import Tuple, List, Optional
from loguru import logger

from app.models.schemas import AnalyzeRequest


class DataPreprocessor:
    """데이터 전처리 담당"""

    @staticmethod
    def prepare_data(
        request: AnalyzeRequest,
    ) -> Tuple[pd.DataFrame, pd.Series]:
        """
        분석 요청 데이터를 전처리

        Args:
            request: 분석 요청 데이터

        Returns:
            (X, y) 튜플 - 독립변수 DataFrame, 종속변수 Series
        """
        logger.info("데이터 전처리 시작")

        # JSON 데이터를 DataFrame으로 변환
        df = pd.DataFrame(request.data)
        logger.info(f"데이터 형태: {df.shape} (행: {df.shape[0]}, 열: {df.shape[1]})")

        # 종속 변수 분리
        if request.target_column not in df.columns:
            raise ValueError(f"타겟 컬럼 '{request.target_column}'을 찾을 수 없습니다.")

        y = df[request.target_column]
        X = df.drop(columns=[request.target_column])

        # 기본 전처리
        X, y = DataPreprocessor._handle_missing_values(X, y)
        X = DataPreprocessor._encode_categoricals(X)

        logger.info(f"전처리 완료: X={X.shape}, y={y.shape}")
        return X, y

    @staticmethod
    def prepare_data_from_df(
        df: pd.DataFrame,
        target_column: str,
    ) -> Tuple[pd.DataFrame, pd.Series]:
        """
        DataFrame에서 직접 전처리

        Args:
            df: 입력 DataFrame
            target_column: 타겟 컬럼명

        Returns:
            (X, y) 튜플
        """
        if target_column not in df.columns:
            raise ValueError(f"타겟 컬럼 '{target_column}'을 찾을 수 없습니다.")

        y = df[target_column]
        X = df.drop(columns=[target_column])

        X, y = DataPreprocessor._handle_missing_values(X, y)
        X = DataPreprocessor._encode_categoricals(X)

        return X, y

    @staticmethod
    def _handle_missing_values(
        X: pd.DataFrame,
        y: pd.Series,
    ) -> Tuple[pd.DataFrame, pd.Series]:
        """결측치 처리"""
        # 수치형: 평균으로 대체
        X = X.fillna(X.mean(numeric_only=True))

        # 종속변수 결측치
        if pd.api.types.is_numeric_dtype(y):
            y = y.fillna(y.mean())
        else:
            y = y.fillna(y.mode()[0] if len(y.mode()) > 0 else "unknown")

        return X, y

    @staticmethod
    def _encode_categoricals(X: pd.DataFrame) -> pd.DataFrame:
        """범주형 변수 인코딩 (Label Encoding)"""
        for col in X.select_dtypes(include=["object"]).columns:
            X[col] = pd.Categorical(X[col]).codes
        return X

    @staticmethod
    def validate_data(
        data: list,
        max_rows: int = 100_000,
        max_columns: int = 500,
    ) -> None:
        """
        데이터 유효성 검증

        Args:
            data: 입력 데이터 리스트
            max_rows: 최대 행 수
            max_columns: 최대 열 수

        Raises:
            ValueError: 데이터가 제한을 초과하는 경우
        """
        if len(data) > max_rows:
            raise ValueError(
                f"데이터 행 수가 제한을 초과합니다: {len(data)} > {max_rows}"
            )

        if len(data) > 0:
            n_cols = len(data[0])
            if n_cols > max_columns:
                raise ValueError(
                    f"데이터 열 수가 제한을 초과합니다: {n_cols} > {max_columns}"
                )
