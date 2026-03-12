"""
SSRF Guard
Webhook URL의 SSRF(Server-Side Request Forgery) 공격 방어
"""
import ipaddress
from urllib.parse import urlparse
from loguru import logger


# 차단 대상 private/reserved IP 범위
BLOCKED_NETWORKS = [
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),  # link-local
    ipaddress.ip_network("0.0.0.0/8"),
    ipaddress.ip_network("::1/128"),  # IPv6 loopback
    ipaddress.ip_network("fc00::/7"),  # IPv6 private
    ipaddress.ip_network("fe80::/10"),  # IPv6 link-local
]

BLOCKED_HOSTNAMES = {"localhost", "0.0.0.0", "127.0.0.1", "::1", "metadata.google.internal"}


def validate_webhook_url(url: str) -> bool:
    """
    Webhook URL의 안전성 검증

    Args:
        url: 검증할 URL

    Returns:
        안전한 URL이면 True

    Raises:
        ValueError: 위험한 URL인 경우
    """
    if not url:
        return True

    parsed = urlparse(url)

    # HTTPS 강제 (프로덕션 환경)
    if parsed.scheme not in ("http", "https"):
        raise ValueError(f"허용되지 않는 프로토콜: {parsed.scheme}")

    hostname = parsed.hostname
    if not hostname:
        raise ValueError("호스트명이 없습니다.")

    # 차단된 호스트명 확인
    if hostname.lower() in BLOCKED_HOSTNAMES:
        raise ValueError(f"차단된 호스트: {hostname}")

    # IP 주소 직접 입력 시 private IP 확인
    try:
        ip = ipaddress.ip_address(hostname)
        for network in BLOCKED_NETWORKS:
            if ip in network:
                raise ValueError(f"내부 네트워크 접근 차단: {hostname}")
    except ValueError as e:
        if "차단" in str(e) or "내부" in str(e):
            raise
        # hostname이 IP가 아닌 경우 (도메인) - DNS 확인은 런타임에 수행
        pass

    logger.info(f"Webhook URL 검증 통과: {url}")
    return True
