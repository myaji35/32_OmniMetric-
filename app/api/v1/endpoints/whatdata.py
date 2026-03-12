"""
WhatDataAI Endpoint
데이터 사전 분석 API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Dict, List, Any

from app.api.v1.dependencies import verify_api_key
from app.services.whatdata import WhatDataAnalyzer


router = APIRouter()


class WhatDataRequest(BaseModel):
    """WhatDataAI 요청"""
    data: List[Dict[str, Any]] = Field(
        ..., description="분석할 데이터", min_length=1
    )
    target_column: str = Field(..., description="타겟 컬럼명")


@router.post(
    "/whatdata",
    summary="WhatDataAI 사전분석",
    description="데이터 특성을 자동 분석하고 적합한 분석 유형을 추천합니다.",
)
async def analyze_data_characteristics(
    request: WhatDataRequest,
    _: None = Depends(verify_api_key),
) -> Dict[str, Any]:
    """WhatDataAI 분석"""
    analyzer = WhatDataAnalyzer()
    try:
        result = analyzer.analyze(request.data, request.target_column)
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
