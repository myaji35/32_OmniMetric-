"""
Report Endpoint
분석 결과 리포트 조회
"""
from fastapi import APIRouter, Depends, HTTPException, status, Path

from app.models.schemas import ReportResponse, StatusResponse
from app.api.v1.dependencies import verify_api_key
from app.core.storage import get_storage


router = APIRouter()


@router.get(
    "/report/{task_id}",
    response_model=ReportResponse,
    summary="분석 리포트 조회",
    description="완료된 분석의 상세 리포트를 반환합니다."
)
async def get_analysis_report(
    task_id: str = Path(..., description="분석 작업 ID"),
    _: None = Depends(verify_api_key)
):
    """
    작업 ID로 분석 결과 조회

    - 작업 완료 여부 확인
    - 토너먼트 결과, 승자 모델, XAI 통찰, 자연어 리포트 반환
    """
    storage = get_storage()

    # 작업 상태 확인
    task_status = await storage.get_task_status(task_id)
    if not task_status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="작업을 찾을 수 없습니다."
        )

    if task_status["status"] != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"작업이 아직 완료되지 않았습니다. 현재 상태: {task_status['status']}"
        )

    # 리포트 조회
    report = await storage.get_report(task_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="리포트를 찾을 수 없습니다."
        )

    return report


@router.get(
    "/status/{task_id}",
    response_model=StatusResponse,
    summary="작업 상태 조회",
    description="진행 중인 분석의 상태를 확인합니다."
)
async def get_task_status(
    task_id: str = Path(..., description="분석 작업 ID"),
    _: None = Depends(verify_api_key)
):
    """
    작업 진행 상태 확인

    - pending: 대기 중
    - processing: 처리 중 (진행률 포함)
    - completed: 완료
    - failed: 실패
    """
    storage = get_storage()

    task_status = await storage.get_task_status(task_id)
    if not task_status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="작업을 찾을 수 없습니다."
        )

    return StatusResponse(
        task_id=task_id,
        status=task_status["status"],
        progress=task_status.get("progress", 0),
        message=task_status.get("message", "")
    )
