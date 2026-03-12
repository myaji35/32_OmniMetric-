"""
Pydantic Schemas for OmniMetric API
요청/응답 데이터 모델 정의
"""
from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


# ==================== Request Schemas ====================

class AnalyzeRequest(BaseModel):
    """분석 요청 스키마"""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "data": [
                {"age": 25, "income": 50000, "education_years": 16, "target": 1},
                {"age": 30, "income": 60000, "education_years": 18, "target": 1}
            ],
            "target_column": "target",
            "task_type": "regression",
            "enable_xai": True
        }
    })

    data: List[Dict[str, Any]] = Field(
        ...,
        description="분석할 데이터 (JSON 배열 형태)",
        min_length=10
    )
    target_column: str = Field(
        ...,
        description="예측 대상 컬럼명"
    )
    task_type: Literal["regression", "classification", "multiclass", "timeseries"] = Field(
        default="regression",
        description="분석 유형 (regression/classification/multiclass/timeseries)"
    )
    enable_xai: bool = Field(
        default=True,
        description="XAI 분석 활성화 여부"
    )
    webhook_url: Optional[str] = Field(
        default=None,
        description="분석 완료 시 호출할 Webhook URL"
    )


class ThresholdUpdateRequest(BaseModel):
    """임계값 업데이트 요청"""
    error_threshold: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="재학습 트리거 오차 임계값 (0.0 ~ 1.0)"
    )
    min_r2_score: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="최소 R² 점수 요구사항"
    )


# ==================== Response Schemas ====================

class AlgorithmResult(BaseModel):
    """개별 알고리즘 결과"""
    name: str = Field(..., description="알고리즘 이름")
    r2_score: float = Field(..., description="R² 점수")
    adj_r2_score: Optional[float] = Field(None, description="조정된 R² 점수")
    p_value: Optional[float] = Field(None, description="P-value")
    execution_time: float = Field(..., description="실행 시간 (초)")


class WinnerModel(BaseModel):
    """최종 선정 모델"""
    algorithm: str = Field(..., description="선정된 알고리즘")
    r2_score: float = Field(..., description="R² 점수")
    adj_r2_score: Optional[float] = Field(None, description="조정된 R² 점수")
    formula: str = Field(..., description="수학적 공식")
    coefficients: Dict[str, float] = Field(..., description="변수별 계수")
    feature_importance: Dict[str, float] = Field(..., description="변수 중요도 (%)")


class XAIInsights(BaseModel):
    """XAI 통찰"""
    shap_values: Optional[Dict[str, float]] = Field(None, description="SHAP 값")
    lime_explanation: Optional[str] = Field(None, description="LIME 설명")
    top_features: List[str] = Field(..., description="상위 영향 변수")


class NaturalLanguageReport(BaseModel):
    """자연어 리포트"""
    summary: str = Field(..., description="분석 요약")
    key_findings: List[str] = Field(..., description="핵심 발견사항")
    variable_impacts: List[str] = Field(..., description="변수별 영향 설명")
    selection_reason: str = Field(..., description="모델 선정 사유")


class AnalysisResponse(BaseModel):
    """분석 응답 (즉시 반환)"""
    task_id: str = Field(..., description="작업 ID")
    status: Literal["pending", "processing", "completed", "failed"] = Field(
        default="pending",
        description="작업 상태"
    )
    message: str = Field(..., description="상태 메시지")
    created_at: datetime = Field(default_factory=datetime.now, description="생성 시간")


class ReportResponse(BaseModel):
    """리포트 응답 (완료 시 반환)"""
    task_id: str = Field(..., description="작업 ID")
    status: Literal["completed", "failed"] = Field(..., description="작업 상태")

    # Tournament Results
    total_algorithms_tested: int = Field(..., description="테스트된 알고리즘 수")
    tournament_duration: float = Field(..., description="토너먼트 소요 시간 (초)")
    top_5_algorithms: List[AlgorithmResult] = Field(..., description="상위 5개 알고리즘")

    # Winner Model
    winner: WinnerModel = Field(..., description="최종 선정 모델")

    # XAI (Optional)
    xai_insights: Optional[XAIInsights] = Field(None, description="XAI 통찰")

    # Natural Language Report
    report: NaturalLanguageReport = Field(..., description="자연어 리포트")

    # Metadata
    completed_at: datetime = Field(default_factory=datetime.now, description="완료 시간")
    data_shape: tuple[int, int] = Field(..., description="데이터 형태 (행, 열)")


class StatusResponse(BaseModel):
    """작업 상태 응답"""
    task_id: str
    status: Literal["pending", "processing", "completed", "failed"]
    progress: Optional[int] = Field(None, ge=0, le=100, description="진행률 (%)")
    message: str


class ThresholdResponse(BaseModel):
    """임계값 응답"""
    error_threshold: float
    min_r2_score: float
    updated_at: datetime = Field(default_factory=datetime.now)


class HealthResponse(BaseModel):
    """헬스 체크 응답"""
    status: Literal["healthy", "unhealthy"]
    version: str
    environment: str
    timestamp: datetime = Field(default_factory=datetime.now)
