"""
Simulate Endpoint
What-if 시뮬레이션 API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Dict, List, Any

from app.api.v1.dependencies import verify_api_key
from app.services.simulator import WhatIfSimulator


router = APIRouter()


class SimulateRequest(BaseModel):
    """시뮬레이션 요청"""
    task_id: str = Field(..., description="원본 분석 작업 ID")
    scenarios: List[Dict[str, float]] = Field(
        ...,
        description="시나리오 리스트",
        min_length=1,
    )


@router.post(
    "/simulate",
    summary="What-if 시뮬레이션",
    description="학습된 모델에 가상 입력값을 주입하여 예측값을 반환합니다.",
)
async def simulate(
    request: SimulateRequest,
    _: None = Depends(verify_api_key),
) -> Dict[str, Any]:
    """What-if 시뮬레이션 실행"""
    simulator = WhatIfSimulator()
    try:
        result = await simulator.simulate(request.task_id, request.scenarios)
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
