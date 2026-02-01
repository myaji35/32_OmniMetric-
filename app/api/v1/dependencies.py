"""
FastAPI Dependencies
의존성 주입 및 공통 로직
"""
from typing import Annotated
from fastapi import Depends, Header, HTTPException, status
from app.core.config import Settings, get_settings


async def verify_api_key(
    x_api_key: Annotated[str | None, Header()] = None,
    settings: Settings = Depends(get_settings)
) -> None:
    """
    API 키 검증 (프로덕션 환경에서만)
    """
    if settings.is_production:
        if not x_api_key or x_api_key != settings.external_api_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="유효하지 않은 API 키입니다."
            )


async def get_current_settings() -> Settings:
    """현재 설정 반환"""
    return get_settings()
