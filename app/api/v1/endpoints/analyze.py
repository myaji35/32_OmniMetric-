"""
Analyze Endpoint
데이터 분석 및 알고리즘 토너먼트 시작
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from uuid import uuid4
from datetime import datetime

from app.models.schemas import AnalyzeRequest, AnalysisResponse
from app.api.v1.dependencies import verify_api_key
from app.core.engine import TournamentEngine
from app.core.storage import get_storage


router = APIRouter()


@router.post(
    "/analyze",
    response_model=AnalysisResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="데이터 분석 시작",
    description="60+ 알고리즘 토너먼트를 시작하고 작업 ID를 반환합니다."
)
async def analyze_data(
    request: AnalyzeRequest,
    background_tasks: BackgroundTasks,
    _: None = Depends(verify_api_key)
):
    """
    데이터 분석 요청 처리

    - 입력 데이터 검증
    - 작업 ID 생성 및 즉시 반환
    - 백그라운드에서 60개 알고리즘 토너먼트 실행
    """
    # 작업 ID 생성
    task_id = str(uuid4())

    # 스토리지 초기화
    storage = get_storage()
    await storage.update_task_status(task_id, "pending", 0)

    # 토너먼트 엔진 생성 및 백그라운드 작업 시작
    engine = TournamentEngine()
    background_tasks.add_task(engine.run_tournament, task_id, request)

    return AnalysisResponse(
        task_id=task_id,
        status="pending",
        message="분석 작업이 시작되었습니다. /v1/report/{task_id}로 결과를 조회하세요.",
        created_at=datetime.now()
    )
