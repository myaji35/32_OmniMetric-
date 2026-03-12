"""
Rate Limiter
API 요청 속도 제한
"""
from typing import Optional
from loguru import logger


class RateLimiter:
    """인메모리 Rate Limiter (Redis 미사용 환경 대응)"""

    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self._request_counts: dict = {}

    def is_allowed(self, client_id: str) -> bool:
        """요청 허용 여부 확인"""
        import time

        now = time.time()
        window_start = now - 60

        if client_id not in self._request_counts:
            self._request_counts[client_id] = []

        # 만료된 요청 제거
        self._request_counts[client_id] = [
            t for t in self._request_counts[client_id] if t > window_start
        ]

        if len(self._request_counts[client_id]) >= self.requests_per_minute:
            logger.warning(f"Rate limit 초과: {client_id}")
            return False

        self._request_counts[client_id].append(now)
        return True


# 전역 인스턴스
_rate_limiter: Optional[RateLimiter] = None


def get_rate_limiter() -> RateLimiter:
    """Rate Limiter 싱글톤 인스턴스"""
    global _rate_limiter
    if _rate_limiter is None:
        from app.core.config import settings
        _rate_limiter = RateLimiter(
            requests_per_minute=getattr(settings, "rate_limit_per_minute", 60)
        )
    return _rate_limiter
