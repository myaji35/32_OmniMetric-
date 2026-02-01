"""
Task Storage
Redis 기반 작업 상태 및 결과 저장
"""
import redis.asyncio as aioredis
import json
from typing import Optional, Literal
from loguru import logger

from app.core.config import settings
from app.models.schemas import ReportResponse


class TaskStorage:
    """Redis 기반 작업 저장소"""

    def __init__(self):
        self.redis_client: Optional[aioredis.Redis] = None

    async def connect(self) -> None:
        """Redis 연결"""
        if self.redis_client is None:
            self.redis_client = await aioredis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            logger.info(f"✅ Redis 연결 완료: {settings.redis_host}:{settings.redis_port}")

    async def disconnect(self) -> None:
        """Redis 연결 종료"""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("🛑 Redis 연결 종료")

    async def update_task_status(
        self,
        task_id: str,
        status: Literal["pending", "processing", "completed", "failed"],
        progress: int = 0
    ) -> None:
        """
        작업 상태 업데이트

        Args:
            task_id: 작업 ID
            status: 작업 상태
            progress: 진행률 (0-100)
        """
        if not self.redis_client:
            await self.connect()

        key = f"task:{task_id}:status"
        value = json.dumps({
            "status": status,
            "progress": progress,
            "message": self._get_status_message(status, progress)
        })

        await self.redis_client.set(key, value, ex=3600)  # 1시간 TTL
        logger.info(f"작업 {task_id} 상태 업데이트: {status} ({progress}%)")

    async def get_task_status(self, task_id: str) -> Optional[dict]:
        """작업 상태 조회"""
        if not self.redis_client:
            await self.connect()

        key = f"task:{task_id}:status"
        value = await self.redis_client.get(key)

        if value:
            return json.loads(value)
        return None

    async def save_report(self, task_id: str, report: ReportResponse) -> None:
        """
        분석 리포트 저장

        Args:
            task_id: 작업 ID
            report: 리포트 객체
        """
        if not self.redis_client:
            await self.connect()

        key = f"task:{task_id}:report"
        value = report.model_dump_json()

        await self.redis_client.set(key, value, ex=86400)  # 24시간 TTL
        logger.info(f"작업 {task_id} 리포트 저장 완료")

    async def get_report(self, task_id: str) -> Optional[ReportResponse]:
        """리포트 조회"""
        if not self.redis_client:
            await self.connect()

        key = f"task:{task_id}:report"
        value = await self.redis_client.get(key)

        if value:
            return ReportResponse.model_validate_json(value)
        return None

    async def save_error(self, task_id: str, error_message: str) -> None:
        """오류 메시지 저장"""
        if not self.redis_client:
            await self.connect()

        key = f"task:{task_id}:error"
        await self.redis_client.set(key, error_message, ex=86400)
        logger.error(f"작업 {task_id} 오류 저장: {error_message}")

    async def get_error(self, task_id: str) -> Optional[str]:
        """오류 메시지 조회"""
        if not self.redis_client:
            await self.connect()

        key = f"task:{task_id}:error"
        return await self.redis_client.get(key)

    def _get_status_message(self, status: str, progress: int) -> str:
        """상태별 메시지 생성"""
        messages = {
            "pending": "분석 대기 중...",
            "processing": f"분석 진행 중... ({progress}%)",
            "completed": "분석 완료",
            "failed": "분석 실패"
        }
        return messages.get(status, "알 수 없는 상태")


# 전역 싱글톤 인스턴스
_storage_instance: Optional[TaskStorage] = None


def get_storage() -> TaskStorage:
    """TaskStorage 싱글톤 인스턴스 반환"""
    global _storage_instance
    if _storage_instance is None:
        _storage_instance = TaskStorage()
    return _storage_instance
