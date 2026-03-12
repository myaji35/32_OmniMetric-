"""
B2B Connector Service
갑(OmniMetric)-을(고객사) 데이터 연동 서비스
"""
import hashlib
import json
import os
import secrets
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
from loguru import logger

from app.core.storage import TaskStorage


# 영속 저장 경로 (환경변수 또는 기본 경로)
CONNECTOR_STORE_PATH = Path(
    os.environ.get("OMNIMETRIC_CONNECTOR_STORE", "data/connectors.json")
)


class B2BConnectorService:
    """B2B 데이터 커넥터 서비스 (파일 기반 영속화)"""

    def __init__(self) -> None:
        self.storage = TaskStorage()
        self._connectors: Dict[str, Dict[str, Any]] = {}
        self._load_from_disk()

    def _load_from_disk(self) -> None:
        """디스크에서 커넥터 데이터 로드"""
        if CONNECTOR_STORE_PATH.exists():
            try:
                with open(CONNECTOR_STORE_PATH, "r", encoding="utf-8") as f:
                    self._connectors = json.load(f)
                logger.info(f"커넥터 데이터 로드: {len(self._connectors)}건")
            except (json.JSONDecodeError, OSError) as e:
                logger.warning(f"커넥터 데이터 로드 실패, 빈 저장소 시작: {e}")
                self._connectors = {}

    def _save_to_disk(self) -> None:
        """디스크에 커넥터 데이터 저장"""
        CONNECTOR_STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(CONNECTOR_STORE_PATH, "w", encoding="utf-8") as f:
            json.dump(self._connectors, f, ensure_ascii=False, indent=2)

    def verify_ip(self, connector_id: str, client_ip: str) -> bool:
        """
        IP 화이트리스트 검증

        Args:
            connector_id: 커넥터 ID
            client_ip: 클라이언트 IP

        Returns:
            허용 여부 (화이트리스트 비어있으면 항상 True)
        """
        connector = self._connectors.get(connector_id)
        if not connector:
            return False

        whitelist = connector.get("ip_whitelist", [])
        if not whitelist:
            return True  # 화이트리스트 미설정 시 모두 허용

        is_allowed = client_ip in whitelist
        if not is_allowed:
            logger.warning(
                f"IP 차단: {client_ip} (커넥터: {connector_id}, "
                f"허용 목록: {whitelist})"
            )
            connector["audit_log"].append({
                "action": "ip_blocked",
                "client_ip": client_ip,
                "timestamp": datetime.now().isoformat(),
            })
            self._save_to_disk()

        return is_allowed

    def renew_api_key(self, connector_id: str) -> Dict[str, Any]:
        """
        API Key 갱신

        Args:
            connector_id: 커넥터 ID

        Returns:
            새 API Key 정보
        """
        connector = self._connectors.get(connector_id)
        if not connector:
            raise ValueError(f"커넥터 {connector_id}를 찾을 수 없습니다.")

        if connector["status"] != "active":
            raise ValueError(f"커넥터가 비활성 상태입니다: {connector['status']}")

        # 새 키 생성
        new_raw_key = secrets.token_urlsafe(48)
        new_key_hash = hashlib.sha256(new_raw_key.encode()).hexdigest()

        connector["api_key_hash"] = new_key_hash
        connector["api_key_prefix"] = new_raw_key[:8]
        connector["audit_log"].append({
            "action": "key_renewed",
            "timestamp": datetime.now().isoformat(),
        })

        self._save_to_disk()
        logger.info(f"API Key 갱신: {connector['tenant_name']} (ID: {connector_id})")

        return {
            "connector_id": connector_id,
            "tenant_name": connector["tenant_name"],
            "api_key": new_raw_key,
            "api_key_prefix": new_raw_key[:8],
            "message": "API Key가 갱신되었습니다. 이전 키는 더 이상 유효하지 않습니다.",
        }

    def create_connector(
        self,
        tenant_name: str,
        callback_url: str,
        scopes: List[str],
        ip_whitelist: List[str] | None = None,
    ) -> Dict[str, Any]:
        """
        고객사 연동 등록 및 API Key 발행

        Args:
            tenant_name: 고객사 이름
            callback_url: 콜백 URL
            scopes: 권한 범위 리스트
            ip_whitelist: IP 화이트리스트

        Returns:
            커넥터 정보 (API Key 포함)
        """
        # API Key 생성
        raw_api_key = secrets.token_urlsafe(48)
        api_key_hash = hashlib.sha256(raw_api_key.encode()).hexdigest()
        connector_id = secrets.token_hex(16)

        connector = {
            "connector_id": connector_id,
            "tenant_name": tenant_name,
            "callback_url": callback_url,
            "scopes": scopes,
            "api_key_hash": api_key_hash,
            "api_key_prefix": raw_api_key[:8],  # 식별용 prefix만 저장
            "ip_whitelist": ip_whitelist or [],
            "status": "active",
            "created_at": datetime.now().isoformat(),
            "last_sync_at": None,
            "sync_count": 0,
            "audit_log": [],
        }

        self._connectors[connector_id] = connector
        self._save_to_disk()
        logger.info(f"B2B 커넥터 생성: {tenant_name} (ID: {connector_id})")

        # 응답에는 평문 키를 포함 (최초 1회만 노출)
        return {
            "connector_id": connector_id,
            "tenant_name": tenant_name,
            "api_key": raw_api_key,
            "api_key_prefix": raw_api_key[:8],
            "scopes": scopes,
            "status": "active",
            "message": "API Key는 이 응답에서만 확인 가능합니다. 안전하게 보관하세요.",
        }

    def list_connectors(self) -> List[Dict[str, Any]]:
        """연동 목록 조회"""
        return [
            {
                "connector_id": c["connector_id"],
                "tenant_name": c["tenant_name"],
                "status": c["status"],
                "api_key_prefix": c["api_key_prefix"],
                "scopes": c["scopes"],
                "last_sync_at": c["last_sync_at"],
                "sync_count": c["sync_count"],
                "created_at": c["created_at"],
            }
            for c in self._connectors.values()
        ]

    def get_connector(self, connector_id: str) -> Optional[Dict[str, Any]]:
        """특정 커넥터 상세 조회"""
        connector = self._connectors.get(connector_id)
        if not connector:
            return None

        return {
            "connector_id": connector["connector_id"],
            "tenant_name": connector["tenant_name"],
            "callback_url": connector["callback_url"],
            "status": connector["status"],
            "api_key_prefix": connector["api_key_prefix"],
            "scopes": connector["scopes"],
            "ip_whitelist": connector["ip_whitelist"],
            "last_sync_at": connector["last_sync_at"],
            "sync_count": connector["sync_count"],
            "created_at": connector["created_at"],
            "audit_log": connector["audit_log"][-10:],  # 최근 10건
        }

    def verify_api_key(self, connector_id: str, api_key: str) -> bool:
        """API Key 유효성 검증"""
        connector = self._connectors.get(connector_id)
        if not connector:
            return False

        if connector["status"] != "active":
            return False

        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        is_valid = key_hash == connector["api_key_hash"]

        # 감사 로그
        connector["audit_log"].append({
            "action": "verify_key",
            "success": is_valid,
            "timestamp": datetime.now().isoformat(),
        })
        self._save_to_disk()

        return is_valid

    def sync_data(self, connector_id: str) -> Dict[str, Any]:
        """데이터 수집 트리거"""
        connector = self._connectors.get(connector_id)
        if not connector:
            raise ValueError(f"커넥터 {connector_id}를 찾을 수 없습니다.")

        if connector["status"] != "active":
            raise ValueError(f"커넥터가 비활성 상태입니다: {connector['status']}")

        # 동기화 기록
        connector["last_sync_at"] = datetime.now().isoformat()
        connector["sync_count"] += 1
        connector["audit_log"].append({
            "action": "sync_data",
            "timestamp": datetime.now().isoformat(),
        })

        self._save_to_disk()
        logger.info(f"데이터 동기화 트리거: {connector['tenant_name']}")

        return {
            "connector_id": connector_id,
            "tenant_name": connector["tenant_name"],
            "sync_status": "triggered",
            "sync_count": connector["sync_count"],
            "message": "데이터 수집이 트리거되었습니다.",
        }

    def discover_schema(self, connector_id: str) -> Dict[str, Any]:
        """데이터 스키마 자동 탐색"""
        connector = self._connectors.get(connector_id)
        if not connector:
            raise ValueError(f"커넥터 {connector_id}를 찾을 수 없습니다.")

        connector["audit_log"].append({
            "action": "discover_schema",
            "timestamp": datetime.now().isoformat(),
        })
        self._save_to_disk()

        # 스키마 탐색 (실제 구현에서는 을의 API를 호출)
        return {
            "connector_id": connector_id,
            "tenant_name": connector["tenant_name"],
            "schema_discovery": "pending",
            "message": "스키마 탐색이 시작되었습니다. 을의 데이터 엔드포인트 연결 필요.",
        }

    def delete_connector(self, connector_id: str) -> Dict[str, Any]:
        """커넥터 삭제 및 API Key 폐기"""
        connector = self._connectors.get(connector_id)
        if not connector:
            raise ValueError(f"커넥터 {connector_id}를 찾을 수 없습니다.")

        tenant_name = connector["tenant_name"]
        del self._connectors[connector_id]
        self._save_to_disk()

        logger.info(f"B2B 커넥터 삭제: {tenant_name} (ID: {connector_id})")

        return {
            "connector_id": connector_id,
            "tenant_name": tenant_name,
            "status": "deleted",
            "message": "커넥터가 삭제되고 API Key가 폐기되었습니다.",
        }


# 전역 싱글톤
_connector_service: Optional[B2BConnectorService] = None


def get_connector_service() -> B2BConnectorService:
    """B2BConnectorService 싱글톤"""
    global _connector_service
    if _connector_service is None:
        _connector_service = B2BConnectorService()
    return _connector_service
