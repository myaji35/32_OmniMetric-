"""
API v1 Router
모든 v1 엔드포인트 통합
"""
from fastapi import APIRouter
from app.api.v1.endpoints import analyze, report, threshold


api_router = APIRouter()

# 각 엔드포인트 라우터 등록
api_router.include_router(analyze.router, tags=["분석"])
api_router.include_router(report.router, tags=["리포트"])
api_router.include_router(threshold.router, tags=["설정"])
