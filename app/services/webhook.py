"""
Webhook Service
외부 시스템 연동 및 알림
"""
import httpx
from typing import Dict, Any, Optional
from loguru import logger

from app.core.config import settings


class WebhookService:
    """Webhook 전송 서비스"""

    def __init__(self):
        self.timeout = 30.0  # 30초 타임아웃

    async def send_completion_notification(
        self,
        task_id: str,
        webhook_url: str,
        report_summary: Dict[str, Any]
    ) -> bool:
        """
        분석 완료 알림 전송

        Args:
            task_id: 작업 ID
            webhook_url: Webhook URL
            report_summary: 리포트 요약

        Returns:
            전송 성공 여부
        """
        logger.info(f"📤 Webhook 전송 시작: {task_id} → {webhook_url}")

        payload = {
            "event": "analysis_completed",
            "task_id": task_id,
            "timestamp": report_summary.get("completed_at"),
            "summary": {
                "winner_algorithm": report_summary.get("winner", {}).get("algorithm"),
                "r2_score": report_summary.get("winner", {}).get("r2_score"),
                "total_algorithms": report_summary.get("total_algorithms_tested"),
                "duration": report_summary.get("tournament_duration")
            },
            "report_url": f"/v1/report/{task_id}"
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    webhook_url,
                    json=payload,
                    headers={
                        "Content-Type": "application/json",
                        "X-OmniMetric-Event": "analysis_completed",
                        "X-OmniMetric-Task-ID": task_id
                    }
                )

                if response.status_code in [200, 201, 202, 204]:
                    logger.info(f"✅ Webhook 전송 성공: {response.status_code}")
                    return True
                else:
                    logger.warning(
                        f"⚠️ Webhook 응답 오류: {response.status_code} - {response.text}"
                    )
                    return False

        except httpx.TimeoutException:
            logger.error(f"❌ Webhook 타임아웃: {webhook_url}")
            return False
        except Exception as e:
            logger.error(f"❌ Webhook 전송 실패: {str(e)}")
            return False

    async def send_error_notification(
        self,
        task_id: str,
        webhook_url: str,
        error_message: str
    ) -> bool:
        """
        오류 알림 전송

        Args:
            task_id: 작업 ID
            webhook_url: Webhook URL
            error_message: 오류 메시지

        Returns:
            전송 성공 여부
        """
        logger.info(f"📤 오류 Webhook 전송: {task_id}")

        payload = {
            "event": "analysis_failed",
            "task_id": task_id,
            "error": error_message,
            "timestamp": None  # datetime.now() 추가 가능
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    webhook_url,
                    json=payload,
                    headers={
                        "Content-Type": "application/json",
                        "X-OmniMetric-Event": "analysis_failed",
                        "X-OmniMetric-Task-ID": task_id
                    }
                )

                return response.status_code in [200, 201, 202, 204]

        except Exception as e:
            logger.error(f"❌ 오류 Webhook 전송 실패: {str(e)}")
            return False

    async def send_retrain_notification(
        self,
        original_task_id: str,
        new_task_id: str,
        webhook_url: str,
        trigger_reason: str
    ) -> bool:
        """
        재학습 알림 전송

        Args:
            original_task_id: 원본 작업 ID
            new_task_id: 재학습 작업 ID
            webhook_url: Webhook URL
            trigger_reason: 재학습 트리거 사유

        Returns:
            전송 성공 여부
        """
        logger.info(f"📤 재학습 Webhook 전송: {new_task_id}")

        payload = {
            "event": "model_retrain_triggered",
            "original_task_id": original_task_id,
            "new_task_id": new_task_id,
            "reason": trigger_reason,
            "timestamp": None
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    webhook_url,
                    json=payload,
                    headers={
                        "Content-Type": "application/json",
                        "X-OmniMetric-Event": "model_retrain_triggered"
                    }
                )

                return response.status_code in [200, 201, 202, 204]

        except Exception as e:
            logger.error(f"❌ 재학습 Webhook 전송 실패: {str(e)}")
            return False


# 전역 싱글톤 인스턴스
_webhook_service: Optional[WebhookService] = None


def get_webhook_service() -> WebhookService:
    """WebhookService 싱글톤 인스턴스 반환"""
    global _webhook_service
    if _webhook_service is None:
        _webhook_service = WebhookService()
    return _webhook_service
