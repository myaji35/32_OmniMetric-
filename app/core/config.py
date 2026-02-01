"""
OmniMetric Configuration Module
환경 변수 및 애플리케이션 설정 관리
"""
from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """애플리케이션 전역 설정"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # API Configuration
    api_title: str = "OmniMetric API"
    api_version: str = "1.0.0"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 4

    # Environment
    environment: Literal["development", "staging", "production"] = "development"
    debug: bool = True

    # Redis Configuration
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str = ""

    # Ray Configuration
    ray_address: str = "auto"
    ray_num_cpus: int = 8
    ray_object_store_memory: int = 2_000_000_000  # 2GB

    # Algorithm Tournament Settings
    tournament_timeout: int = 300  # 5 minutes
    tournament_max_workers: int = 60
    tournament_enable_gpu: bool = False

    # MLOps Auto-Retraining
    mlops_error_threshold: float = 0.15  # 15%
    mlops_min_r2_score: float = 0.85
    mlops_auto_retrain: bool = True
    mlops_retrain_cooldown: int = 3600  # 1 hour

    # XAI Settings
    xai_enable_shap: bool = True
    xai_enable_lime: bool = True
    xai_max_features: int = 20

    # NLG Report Settings
    nlg_language: Literal["ko", "en"] = "ko"
    nlg_detail_level: Literal["brief", "detailed", "comprehensive"] = "detailed"

    # Database (Optional)
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "omnimetric"
    db_user: str = "omnimetric"
    db_password: str = "changeme"

    # Logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    log_format: Literal["json", "text"] = "json"
    log_file_path: str = "./logs/omnimetric.log"

    # External System Integration
    external_webhook_url: str = ""
    external_api_key: str = ""

    @property
    def redis_url(self) -> str:
        """Redis 연결 URL 생성"""
        password = f":{self.redis_password}@" if self.redis_password else ""
        return f"redis://{password}{self.redis_host}:{self.redis_port}/{self.redis_db}"

    @property
    def database_url(self) -> str:
        """PostgreSQL 연결 URL 생성"""
        return (
            f"postgresql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    @property
    def is_production(self) -> bool:
        """프로덕션 환경 여부"""
        return self.environment == "production"

    @property
    def is_development(self) -> bool:
        """개발 환경 여부"""
        return self.environment == "development"


@lru_cache()
def get_settings() -> Settings:
    """
    설정 싱글톤 인스턴스 반환
    FastAPI Depends에서 사용 가능
    """
    return Settings()


# 전역 설정 인스턴스
settings = get_settings()
