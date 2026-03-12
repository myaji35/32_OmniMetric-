"""
EDA (Exploratory Data Analysis) Endpoint
현황분석 API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

from app.api.v1.dependencies import verify_api_key
from app.services.eda import EDAService


router = APIRouter()


class EDARequest(BaseModel):
    """현황분석 요청"""
    data: List[Dict[str, Any]] = Field(..., description="입력 데이터")
    target_column: Optional[str] = Field(
        default=None, description="타겟 컬럼 (선택)"
    )


@router.post(
    "/eda",
    summary="현황분석 (EDA)",
    description="데이터 분포, 상관행렬, 이상치, 결측치를 분석합니다.",
)
async def run_eda(
    request: EDARequest,
    _: None = Depends(verify_api_key),
) -> Dict[str, Any]:
    """현황분석 수행"""
    if not request.data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="데이터가 비어있습니다.",
        )

    service = EDAService()
    try:
        return service.analyze(request.data, request.target_column)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"현황분석 실패: {str(e)}",
        )
