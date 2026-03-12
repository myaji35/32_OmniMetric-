"""
API v1 Router
모든 v1 엔드포인트 통합 (PRD v2.0 전체 API)
"""
from fastapi import APIRouter
from app.api.v1.endpoints import (
    analyze,
    report,
    threshold,
    simulate,
    optimize,
    whatdata,
    actions,
    upload,
    connectors,
    qa,
)


api_router = APIRouter()

# 기존 엔드포인트
api_router.include_router(analyze.router, tags=["분석"])
api_router.include_router(report.router, tags=["리포트"])
api_router.include_router(threshold.router, tags=["설정"])

# Phase 3: 시뮬레이션/최적화
api_router.include_router(simulate.router, tags=["시뮬레이션"])
api_router.include_router(optimize.router, tags=["최적화"])

# Phase 5: WhatDataAI, 행동 시나리오, CSV 업로드
api_router.include_router(whatdata.router, tags=["WhatDataAI"])
api_router.include_router(actions.router, tags=["행동 시나리오"])
api_router.include_router(upload.router, tags=["업로드"])

# Phase 6: AI Q&A
api_router.include_router(qa.router, tags=["AI Q&A"])

# Phase 7: B2B 데이터 커넥터
api_router.include_router(connectors.router, tags=["B2B 커넥터"])
