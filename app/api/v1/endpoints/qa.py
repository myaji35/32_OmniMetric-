"""
AI Q&A Endpoint
분석 결과 기반 자연어 질의응답 API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

from app.api.v1.dependencies import verify_api_key
from app.services.ai_qa import AIQuestionAnswer


router = APIRouter()


class QARequest(BaseModel):
    """AI Q&A 요청"""
    question: str = Field(..., description="분석 결과에 대한 질문", min_length=1, max_length=500)
    context: Optional[Dict[str, Any]] = Field(
        default=None, description="추가 컨텍스트 (선택)"
    )


@router.post(
    "/qa/{task_id}",
    summary="AI Q&A",
    description="분석 결과를 기반으로 자연어 질문에 답변합니다.",
)
async def ask_question(
    task_id: str,
    request: QARequest,
    _: None = Depends(verify_api_key),
) -> Dict[str, Any]:
    """AI 기반 분석 결과 Q&A"""
    qa_service = AIQuestionAnswer()
    try:
        result = await qa_service.answer_question(
            task_id=task_id,
            question=request.question,
            context=request.context,
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI Q&A 처리 실패: {str(e)}",
        )
