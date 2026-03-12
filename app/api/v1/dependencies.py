"""
FastAPI Dependencies
의존성 주입 및 공통 로직
"""
from typing import Annotated
from fastapi import Depends, Header, HTTPException, Request, status
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


async def verify_connector_ip(
    request: Request,
    connector_id: str,
) -> None:
    """
    B2B 커넥터 IP 화이트리스트 검증

    Args:
        request: FastAPI Request (클라이언트 IP 추출)
        connector_id: 커넥터 ID
    """
    from app.services.connector import get_connector_service

    client_ip = request.client.host if request.client else "unknown"
    service = get_connector_service()

    if not service.verify_ip(connector_id, client_ip):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"IP {client_ip}는 이 커넥터에 대한 접근이 허용되지 않습니다.",
        )


async def get_current_settings() -> Settings:
    """현재 설정 반환"""
    return get_settings()
