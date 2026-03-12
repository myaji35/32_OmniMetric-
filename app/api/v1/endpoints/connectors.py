"""
B2B Connectors Endpoint
갑-을 연동 시스템 API (7개 엔드포인트)
"""
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional

from app.api.v1.dependencies import verify_api_key, verify_connector_ip
from app.services.connector import get_connector_service


router = APIRouter()


class CreateConnectorRequest(BaseModel):
    """커넥터 생성 요청"""
    tenant_name: str = Field(..., description="고객사 이름")
    callback_url: str = Field(..., description="콜백 URL")
    scopes: List[str] = Field(
        default=["read"], description="권한 범위 (read, write, admin)"
    )
    ip_whitelist: Optional[List[str]] = Field(
        default=None, description="IP 화이트리스트"
    )


class VerifyKeyRequest(BaseModel):
    """API Key 검증 요청"""
    api_key: str = Field(..., description="검증할 API Key")


@router.post(
    "/connectors",
    summary="고객사 연동 등록",
    description="새 고객사를 등록하고 API Key를 발행합니다.",
    status_code=status.HTTP_201_CREATED,
)
async def create_connector(
    request: CreateConnectorRequest,
    _: None = Depends(verify_api_key),
) -> Dict[str, Any]:
    """고객사 연동 등록 및 API Key 발행"""
    service = get_connector_service()
    return service.create_connector(
        request.tenant_name,
        request.callback_url,
        request.scopes,
        request.ip_whitelist,
    )


@router.get(
    "/connectors",
    summary="연동 목록 조회",
    description="등록된 고객사 연동 목록을 반환합니다.",
)
async def list_connectors(
    _: None = Depends(verify_api_key),
) -> List[Dict[str, Any]]:
    """연동 목록"""
    service = get_connector_service()
    return service.list_connectors()


@router.get(
    "/connectors/{connector_id}",
    summary="연동 상세 조회",
    description="특정 고객사 연동의 상세 정보를 반환합니다.",
)
async def get_connector(
    connector_id: str,
    _: None = Depends(verify_api_key),
) -> Dict[str, Any]:
    """연동 상세"""
    service = get_connector_service()
    result = service.get_connector(connector_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="커넥터를 찾을 수 없습니다.",
        )
    return result


@router.post(
    "/connectors/{connector_id}/verify",
    summary="API Key 검증",
    description="갑-을 API Key 유효성을 검증합니다.",
)
async def verify_connector_key(
    connector_id: str,
    request: VerifyKeyRequest,
    _: None = Depends(verify_api_key),
) -> Dict[str, Any]:
    """API Key 검증"""
    service = get_connector_service()
    is_valid = service.verify_api_key(connector_id, request.api_key)
    return {
        "connector_id": connector_id,
        "valid": is_valid,
        "message": "API Key가 유효합니다." if is_valid else "API Key가 유효하지 않습니다.",
    }


@router.post(
    "/connectors/{connector_id}/sync",
    summary="데이터 수집 트리거",
    description="을의 데이터를 수동으로 수집합니다. IP 화이트리스트 검증 적용.",
)
async def sync_connector_data(
    connector_id: str,
    request: Request,
    _: None = Depends(verify_api_key),
) -> Dict[str, Any]:
    """데이터 수집 (IP 화이트리스트 검증 포함)"""
    await verify_connector_ip(request, connector_id)
    service = get_connector_service()
    try:
        return service.sync_data(connector_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get(
    "/connectors/{connector_id}/schema",
    summary="스키마 자동 탐색",
    description="을의 데이터 구조를 자동으로 탐색합니다. IP 화이트리스트 검증 적용.",
)
async def discover_connector_schema(
    connector_id: str,
    request: Request,
    _: None = Depends(verify_api_key),
) -> Dict[str, Any]:
    """스키마 탐색 (IP 화이트리스트 검증 포함)"""
    await verify_connector_ip(request, connector_id)
    service = get_connector_service()
    try:
        return service.discover_schema(connector_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post(
    "/connectors/{connector_id}/renew",
    summary="API Key 갱신",
    description="기존 API Key를 폐기하고 새 키를 발행합니다.",
)
async def renew_connector_key(
    connector_id: str,
    _: None = Depends(verify_api_key),
) -> Dict[str, Any]:
    """API Key 갱신"""
    service = get_connector_service()
    try:
        return service.renew_api_key(connector_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete(
    "/connectors/{connector_id}",
    summary="연동 해제",
    description="고객사 연동을 해제하고 API Key를 폐기합니다.",
)
async def delete_connector(
    connector_id: str,
    _: None = Depends(verify_api_key),
) -> Dict[str, Any]:
    """연동 해제"""
    service = get_connector_service()
    try:
        return service.delete_connector(connector_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
