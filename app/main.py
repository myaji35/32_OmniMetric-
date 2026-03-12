"""
OmniMetric FastAPI Application
전방위 통계 분석 및 의사결정 엔진 메인 애플리케이션
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from datetime import datetime
import logging

from app.core.config import settings
from app.models.schemas import HealthResponse
from app.api.v1 import api_router


# Logging 설정
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 라이프사이클 관리"""
    # Startup
    logger.info("🚀 OmniMetric API 시작 중...")
    logger.info(f"환경: {settings.environment}")
    logger.info(f"디버그 모드: {settings.debug}")

    # Ray 클러스터 초기화
    from app.core.parallel import RayCluster
    RayCluster.initialize()

    # Redis 연결 확인
    from app.core.storage import get_storage
    storage = get_storage()
    await storage.connect()
    logger.info("✅ Redis 연결 확인 완료")

    yield

    # Shutdown
    logger.info("🛑 OmniMetric API 종료 중...")

    # Ray 클러스터 종료
    RayCluster.shutdown()

    # Redis 연결 종료
    await storage.disconnect()


# FastAPI 인스턴스 생성
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description="125+ 알고리즘 토너먼트 기반 AI 의사결정 시뮬레이션 엔진",
    debug=settings.debug,
    lifespan=lifespan,
    docs_url="/docs" if settings.is_development else None,
    redoc_url="/redoc" if settings.is_development else None,
)


# CORS 미들웨어 (보안 강화: 환경변수로 origin 제어)
_cors_origins = (
    ["*"] if settings.is_development and not settings.allowed_origins
    else [o.strip() for o in settings.allowed_origins.split(",") if o.strip()]
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["*"],
)


# Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """전역 예외 처리"""
    logger.error(f"예외 발생: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": str(exc) if settings.debug else "서버 오류가 발생했습니다.",
            "path": str(request.url)
        }
    )


# Health Check Endpoint
@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    헬스 체크 엔드포인트
    서비스 상태 확인용
    """
    return HealthResponse(
        status="healthy",
        version=settings.api_version,
        environment=settings.environment,
        timestamp=datetime.now()
    )


# Root Endpoint
@app.get("/", tags=["Root"])
async def root():
    """루트 엔드포인트"""
    return {
        "service": "OmniMetric API",
        "version": settings.api_version,
        "status": "running",
        "docs": "/docs" if settings.is_development else "disabled",
        "description": "60+ 알고리즘 토너먼트 기반 전방위 통계 분석 엔진"
    }


# API Router 등록
app.include_router(
    api_router,
    prefix="/v1"
)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.is_development,
        workers=1 if settings.is_development else settings.api_workers,
        log_level=settings.log_level.lower()
    )
