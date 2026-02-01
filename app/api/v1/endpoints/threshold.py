"""
Threshold Endpoint
MLOps 재학습 임계값 설정
"""
from fastapi import APIRouter, Depends, status

from app.models.schemas import ThresholdUpdateRequest, ThresholdResponse
from app.api.v1.dependencies import verify_api_key, get_current_settings
from app.core.config import Settings
from datetime import datetime


router = APIRouter()


@router.patch(
    "/threshold",
    response_model=ThresholdResponse,
    summary="재학습 임계값 업데이트",
    description="자가 보정 MLOps의 오차 임계값 및 최소 R² 점수를 조정합니다."
)
async def update_threshold(
    request: ThresholdUpdateRequest,
    settings: Settings = Depends(get_current_settings),
    _: None = Depends(verify_api_key)
):
    """
    임계값 동적 업데이트

    - error_threshold: 재학습 트리거 오차율 (기본 0.15 = 15%)
    - min_r2_score: 최소 R² 요구사항 (기본 0.85)
    """
    # 업데이트 적용
    if request.error_threshold is not None:
        settings.mlops_error_threshold = request.error_threshold

    if request.min_r2_score is not None:
        settings.mlops_min_r2_score = request.min_r2_score

    return ThresholdResponse(
        error_threshold=settings.mlops_error_threshold,
        min_r2_score=settings.mlops_min_r2_score,
        updated_at=datetime.now()
    )


@router.get(
    "/threshold",
    response_model=ThresholdResponse,
    summary="현재 임계값 조회",
    description="현재 설정된 재학습 임계값을 반환합니다."
)
async def get_current_threshold(
    settings: Settings = Depends(get_current_settings),
    _: None = Depends(verify_api_key)
):
    """현재 임계값 조회"""
    return ThresholdResponse(
        error_threshold=settings.mlops_error_threshold,
        min_r2_score=settings.mlops_min_r2_score,
        updated_at=datetime.now()
    )
