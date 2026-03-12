"""
Actions Endpoint
행동 시나리오 변환 API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

from app.api.v1.dependencies import verify_api_key
from app.services.actions import ActionScenarioConverter


router = APIRouter()


class ActionRequest(BaseModel):
    """행동 시나리오 생성 요청"""
    thresholds: Optional[Dict[str, float]] = Field(
        default=None,
        description='임계값 설정 {"variable_name": threshold_value}',
    )


@router.post(
    "/actions/{task_id}",
    summary="행동 시나리오 생성",
    description="분석 결과를 IF-THEN 행동 규칙으로 자동 변환합니다.",
)
async def generate_action_scenarios(
    task_id: str,
    request: ActionRequest = ActionRequest(),
    _: None = Depends(verify_api_key),
) -> Dict[str, Any]:
    """행동 시나리오 생성"""
    converter = ActionScenarioConverter()
    try:
        result = await converter.generate_scenarios(task_id, request.thresholds)
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get(
    "/actions/{task_id}",
    summary="행동 시나리오 조회",
    description="생성된 행동 시나리오 목록을 조회합니다.",
)
async def get_action_scenarios(
    task_id: str,
    _: None = Depends(verify_api_key),
) -> Dict[str, Any]:
    """행동 시나리오 조회 (POST와 동일하지만 기본 임계값)"""
    converter = ActionScenarioConverter()
    try:
        result = await converter.generate_scenarios(task_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
