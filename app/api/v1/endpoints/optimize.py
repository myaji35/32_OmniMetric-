"""
Optimize Endpoint
목표 달성 최적화 API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

from app.api.v1.dependencies import verify_api_key
from app.services.optimizer import GoalOptimizer


router = APIRouter()


class OptimizeRequest(BaseModel):
    """최적화 요청"""
    task_id: str = Field(..., description="원본 분석 작업 ID")
    target_value: float = Field(..., description="목표 Y 값")
    constraints: Dict[str, Dict[str, float]] = Field(
        default_factory=dict,
        description='제약조건 {"var_1": {"min": 0, "max": 100}}',
    )
    maximize: bool = Field(default=True, description="True=최대화, False=목표값 근사")


@router.post(
    "/optimize",
    summary="목표 달성 최적화",
    description="제약조건 하에서 목표 달성을 위한 최적 변수 조합을 탐색합니다.",
)
async def optimize(
    request: OptimizeRequest,
    _: None = Depends(verify_api_key),
) -> Dict[str, Any]:
    """목표 달성 최적화 실행"""
    optimizer = GoalOptimizer()
    try:
        result = await optimizer.optimize(
            request.task_id,
            request.target_value,
            request.constraints,
            request.maximize,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
