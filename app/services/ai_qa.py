"""
AI Q&A Service
분석 결과 기반 자연어 질의응답 (LLM 연동)
"""
from typing import Dict, Any, Optional, List
from loguru import logger

from app.core.config import settings
from app.core.storage import TaskStorage


class AIQuestionAnswer:
    """AI 기반 분석 결과 Q&A 서비스"""

    def __init__(self) -> None:
        self.storage = TaskStorage()
        self.model = settings.llm_model
        self._client: Optional[Any] = None

    def _get_client(self) -> Optional[Any]:
        """OpenAI 클라이언트 초기화 (lazy)"""
        if self._client is not None:
            return self._client

        if not settings.openai_api_key:
            logger.warning("OpenAI API Key가 설정되지 않았습니다. 로컬 응답 모드 사용.")
            return None

        try:
            from openai import OpenAI

            self._client = OpenAI(api_key=settings.openai_api_key)
            return self._client
        except ImportError:
            logger.warning("openai 패키지가 설치되지 않았습니다. 로컬 응답 모드 사용.")
            return None

    async def answer_question(
        self,
        task_id: str,
        question: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        분석 결과를 기반으로 사용자 질문에 답변

        Args:
            task_id: 분석 작업 ID
            question: 사용자 질문
            context: 추가 컨텍스트 (분석 결과 등)

        Returns:
            답변 결과
        """
        logger.info(f"AI Q&A 요청: task_id={task_id}, question={question[:50]}...")

        # 1. 분석 결과 로드
        analysis_context = context or {}
        if not analysis_context:
            analysis_context = await self._load_analysis_context(task_id)

        if not analysis_context:
            return {
                "task_id": task_id,
                "question": question,
                "answer": f"작업 ID '{task_id}'에 대한 분석 결과를 찾을 수 없습니다.",
                "source": "error",
                "confidence": 0.0,
            }

        # 2. LLM 또는 로컬 응답 생성
        client = self._get_client()
        if client:
            answer = self._ask_llm(client, question, analysis_context)
            source = "llm"
        else:
            answer = self._generate_local_answer(question, analysis_context)
            source = "local"

        return {
            "task_id": task_id,
            "question": question,
            "answer": answer,
            "source": source,
            "confidence": 0.9 if source == "llm" else 0.6,
            "model": self.model if source == "llm" else "rule-based",
        }

    async def _load_analysis_context(self, task_id: str) -> Dict[str, Any]:
        """분석 결과를 스토리지에서 로드"""
        try:
            if not self.storage.redis_client:
                await self.storage.connect()
            result = await self.storage.get_result(task_id)
            return result or {}
        except Exception as e:
            logger.warning(f"분석 결과 로드 실패: {e}")
            return {}

    def _ask_llm(
        self, client: Any, question: str, context: Dict[str, Any]
    ) -> str:
        """LLM에 질문"""
        system_prompt = self._build_system_prompt(context)

        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": question},
                ],
                temperature=0.3,
                max_tokens=1000,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"LLM 호출 실패: {e}")
            return self._generate_local_answer(question, context)

    def _build_system_prompt(self, context: Dict[str, Any]) -> str:
        """시스템 프롬프트 구성"""
        report = context.get("report", {})
        winner = context.get("winner", {})

        prompt = (
            "당신은 OmniMetric AI 분석 결과 전문가입니다. "
            "사용자가 분석 결과에 대해 질문하면 정확하고 이해하기 쉽게 답변합니다.\n\n"
            "## 분석 결과 컨텍스트\n"
        )

        if winner:
            prompt += f"- 최적 알고리즘: {winner.get('algorithm_name', 'N/A')}\n"
            prompt += f"- R2 Score: {winner.get('r2_score', 'N/A')}\n"
            prompt += f"- 계수: {winner.get('coefficients', {})}\n"

        if report:
            prompt += f"- 요약: {report.get('summary', 'N/A')}\n"
            prompt += f"- 핵심 발견: {report.get('key_findings', [])}\n"
            prompt += f"- 변수 영향: {report.get('variable_impacts', [])}\n"

        prompt += (
            "\n한국어로 답변하세요. "
            "전문용어는 괄호 안에 영문을 병기하세요."
        )

        return prompt

    def _generate_local_answer(
        self, question: str, context: Dict[str, Any]
    ) -> str:
        """LLM 없이 규칙 기반 응답 생성"""
        question_lower = question.lower()
        winner = context.get("winner", {})
        report = context.get("report", {})

        # 최적 모델 관련 질문
        if any(kw in question_lower for kw in ["최적", "최고", "best", "winner", "승자"]):
            algo = winner.get("algorithm_name", "알 수 없음")
            r2 = winner.get("r2_score", 0)
            return (
                f"최적 모델은 '{algo}'이며, "
                f"R2 Score {r2:.4f} ({r2*100:.2f}%)를 달성했습니다."
            )

        # 변수 중요도 관련 질문
        if any(kw in question_lower for kw in ["변수", "중요", "영향", "feature", "importance"]):
            impacts = report.get("variable_impacts", [])
            if impacts:
                return "변수별 영향도:\n" + "\n".join(f"- {v}" for v in impacts[:5])
            coefs = winner.get("coefficients", {})
            if coefs:
                sorted_coefs = sorted(coefs.items(), key=lambda x: abs(x[1]), reverse=True)
                lines = [f"- {k}: {v:.4f}" for k, v in sorted_coefs[:5] if k != "intercept"]
                return "주요 변수 계수:\n" + "\n".join(lines)
            return "변수 중요도 정보를 찾을 수 없습니다."

        # 공식 관련 질문
        if any(kw in question_lower for kw in ["공식", "수식", "formula", "equation"]):
            formula = report.get("formula", "")
            if formula:
                return f"분석 결과 수학 공식: {formula}"
            return "공식 정보를 찾을 수 없습니다."

        # R2/성능 관련 질문
        if any(kw in question_lower for kw in ["r2", "성능", "정확도", "accuracy", "score"]):
            r2 = winner.get("r2_score", 0)
            adj_r2 = winner.get("adj_r2_score")
            answer = f"모델 성능: R2 = {r2:.4f} ({r2*100:.2f}%)"
            if adj_r2:
                answer += f", Adjusted R2 = {adj_r2:.4f}"
            return answer

        # 일반 질문
        summary = report.get("summary", "")
        if summary:
            return f"분석 요약: {summary}"

        return "질문에 대한 구체적인 답변을 생성할 수 없습니다. 분석 결과를 다시 확인해 주세요."
