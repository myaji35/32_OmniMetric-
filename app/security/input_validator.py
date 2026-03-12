"""
Input Validator
입력 데이터 크기 및 형식 검증
"""
from typing import List, Dict, Any
from loguru import logger


# 기본 제한값
MAX_ROWS = 100_000
MAX_COLUMNS = 500
MAX_CELL_LENGTH = 10_000


def validate_analyze_input(
    data: List[Dict[str, Any]],
    max_rows: int = MAX_ROWS,
    max_columns: int = MAX_COLUMNS,
) -> None:
    """
    분석 입력 데이터 검증

    Args:
        data: 입력 데이터
        max_rows: 최대 행 수
        max_columns: 최대 열 수

    Raises:
        ValueError: 제한 초과 시
    """
    if not data:
        raise ValueError("데이터가 비어있습니다.")

    if len(data) > max_rows:
        raise ValueError(
            f"데이터 행 수가 제한({max_rows:,})을 초과합니다: {len(data):,}행"
        )

    if len(data) > 0:
        n_cols = len(data[0])
        if n_cols > max_columns:
            raise ValueError(
                f"데이터 열 수가 제한({max_columns})을 초과합니다: {n_cols}열"
            )

    logger.info(f"입력 검증 통과: {len(data)}행")


def validate_file_size(
    file_size_bytes: int,
    max_size_mb: int = 50,
) -> None:
    """
    파일 크기 검증

    Args:
        file_size_bytes: 파일 크기 (바이트)
        max_size_mb: 최대 크기 (MB)

    Raises:
        ValueError: 크기 초과 시
    """
    max_bytes = max_size_mb * 1024 * 1024
    if file_size_bytes > max_bytes:
        raise ValueError(
            f"파일 크기가 제한({max_size_mb}MB)을 초과합니다: "
            f"{file_size_bytes / (1024 * 1024):.1f}MB"
        )
