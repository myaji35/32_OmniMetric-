"""
Regression Tests - 버그 회귀 테스트
최근 수정된 버그(404 라우트 누락, 입력 검증, 스키마)에 대한 회귀 방지
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.schemas import (
    AnalyzeRequest,
    ThresholdUpdateRequest,
    HealthResponse,
)
from app.security.input_validator import validate_analyze_input, validate_file_size


# ==================== FastAPI TestClient ====================

client = TestClient(app, raise_server_exceptions=False)


# ==================== 1. API 라우트 회귀 테스트 ====================
# fix: e596e93 - 시뮬레이션/행동시나리오/AI Q&A 인덱스 페이지 404 해결


class TestAPIRouteRegression:
    """API 라우트 존재 여부 및 404 회귀 방지 테스트"""

    def test_health_endpoint_returns_200(self):
        """GET /health - 헬스 체크 정상 응답"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "environment" in data

    def test_root_endpoint_returns_200(self):
        """GET / - 루트 엔드포인트 정상 응답"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "OmniMetric API"
        assert data["status"] == "running"

    def test_docs_endpoint_available_in_dev(self):
        """GET /docs - 개발 환경에서 Swagger UI 접근 가능"""
        response = client.get("/docs")
        # 개발 환경이면 200, 프로덕션이면 404
        assert response.status_code in (200, 404)

    def test_simulate_endpoint_registered(self):
        """POST /v1/simulate - 시뮬레이션 엔드포인트 등록 확인 (404가 아닌지)"""
        # 빈 body로 요청 → 422(검증 실패)이면 라우트 존재 확인
        response = client.post("/v1/simulate", json={})
        assert response.status_code != 404, (
            "시뮬레이션 엔드포인트가 등록되지 않았습니다 (404 회귀)"
        )
        assert response.status_code == 422  # Pydantic 검증 실패

    def test_actions_post_endpoint_registered(self):
        """POST /v1/actions/{task_id} - 행동 시나리오 생성 엔드포인트 확인"""
        response = client.post("/v1/actions/test_task_123", json={})
        # 라우트 존재: 404(데이터 없음)는 허용, "detail" 필드가 있으면 비즈니스 로직 404
        # 라우트 미등록: 404 + {"detail": "Not Found"}
        if response.status_code == 404:
            data = response.json()
            assert data.get("detail") != "Not Found", (
                "행동 시나리오 POST 엔드포인트가 등록되지 않았습니다 (404 회귀)"
            )

    def test_actions_get_endpoint_registered(self):
        """GET /v1/actions/{task_id} - 행동 시나리오 조회 엔드포인트 확인"""
        response = client.get("/v1/actions/test_task_123")
        if response.status_code == 404:
            data = response.json()
            assert data.get("detail") != "Not Found", (
                "행동 시나리오 GET 엔드포인트가 등록되지 않았습니다 (404 회귀)"
            )

    def test_actions_history_endpoint_registered(self):
        """GET /v1/actions/{task_id}/history - 시나리오 이력 엔드포인트 확인"""
        response = client.get("/v1/actions/test_task_123/history")
        assert response.status_code != 404, (
            "행동 시나리오 이력 엔드포인트가 등록되지 않았습니다 (404 회귀)"
        )

    def test_qa_endpoint_registered(self):
        """POST /v1/qa/{task_id} - AI Q&A 엔드포인트 확인"""
        response = client.post(
            "/v1/qa/test_task_123",
            json={"question": "테스트 질문입니다"},
        )
        assert response.status_code != 404, (
            "AI Q&A 엔드포인트가 등록되지 않았습니다 (404 회귀)"
        )

    def test_analyze_endpoint_registered(self):
        """POST /v1/analyze - 분석 엔드포인트 확인"""
        response = client.post("/v1/analyze", json={})
        assert response.status_code != 404, (
            "분석 엔드포인트가 등록되지 않았습니다 (404 회귀)"
        )
        assert response.status_code == 422

    def test_report_endpoint_registered(self):
        """GET /v1/report/{task_id} - 리포트 엔드포인트 확인"""
        response = client.get("/v1/report/test_task_123")
        # 데이터 없음 404(비즈니스)는 허용, 라우트 미등록 404는 불허
        if response.status_code == 404:
            data = response.json()
            assert data.get("detail") != "Not Found", (
                "리포트 엔드포인트가 등록되지 않았습니다 (404 회귀)"
            )

    def test_threshold_endpoint_registered(self):
        """PATCH /v1/threshold - 임계값 설정 엔드포인트 확인"""
        response = client.patch("/v1/threshold", json={})
        assert response.status_code != 404, (
            "임계값 엔드포인트가 등록되지 않았습니다 (404 회귀)"
        )

    def test_nonexistent_route_returns_404(self):
        """존재하지 않는 경로는 404를 반환해야 함"""
        response = client.get("/v1/nonexistent_endpoint_xyz")
        assert response.status_code == 404

    def test_eda_endpoint_registered(self):
        """POST /v1/eda - 현황분석 엔드포인트 확인"""
        response = client.post("/v1/eda", json={})
        assert response.status_code != 404, (
            "현황분석 엔드포인트가 등록되지 않았습니다 (404 회귀)"
        )

    def test_upload_endpoint_registered(self):
        """POST /v1/upload - 업로드 엔드포인트 확인"""
        response = client.post("/v1/upload")
        assert response.status_code != 404, (
            "업로드 엔드포인트가 등록되지 않았습니다 (404 회귀)"
        )


# ==================== 2. 입력 검증 회귀 테스트 ====================


class TestInputValidationRegression:
    """입력 검증 로직 회귀 테스트"""

    def test_empty_data_raises_error(self):
        """빈 데이터 입력 시 ValueError 발생"""
        with pytest.raises(ValueError, match="비어있습니다"):
            validate_analyze_input([])

    def test_valid_data_passes(self):
        """정상 데이터는 검증 통과"""
        data = [{"col1": i, "col2": i * 2} for i in range(20)]
        validate_analyze_input(data)  # 예외 없이 통과

    def test_exceeds_max_rows(self):
        """행 수 제한 초과 시 ValueError 발생"""
        data = [{"col": i} for i in range(101)]
        with pytest.raises(ValueError, match="행 수가 제한"):
            validate_analyze_input(data, max_rows=100)

    def test_exceeds_max_columns(self):
        """열 수 제한 초과 시 ValueError 발생"""
        row = {f"col_{i}": i for i in range(51)}
        data = [row]
        with pytest.raises(ValueError, match="열 수가 제한"):
            validate_analyze_input(data, max_columns=50)

    def test_file_size_within_limit(self):
        """파일 크기 제한 내 → 통과"""
        validate_file_size(10 * 1024 * 1024)  # 10MB

    def test_file_size_exceeds_limit(self):
        """파일 크기 초과 시 ValueError"""
        with pytest.raises(ValueError, match="파일 크기가 제한"):
            validate_file_size(60 * 1024 * 1024, max_size_mb=50)


# ==================== 3. Pydantic 스키마 회귀 테스트 ====================


class TestSchemaValidationRegression:
    """Pydantic 스키마 검증 회귀 테스트"""

    def test_analyze_request_valid(self):
        """AnalyzeRequest 정상 생성"""
        data = [{"x": i, "y": i * 2} for i in range(10)]
        req = AnalyzeRequest(
            data=data,
            target_column="y",
            task_type="regression",
            enable_xai=True,
        )
        assert req.target_column == "y"
        assert req.task_type == "regression"
        assert req.enable_xai is True
        assert len(req.data) == 10

    def test_analyze_request_requires_min_data(self):
        """AnalyzeRequest는 최소 10개 데이터 필요"""
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            AnalyzeRequest(
                data=[{"x": 1}],  # 1개 → min_length=10 위반
                target_column="x",
            )

    def test_analyze_request_task_type_validation(self):
        """AnalyzeRequest task_type은 지정된 값만 허용"""
        from pydantic import ValidationError

        data = [{"x": i} for i in range(10)]
        with pytest.raises(ValidationError):
            AnalyzeRequest(
                data=data,
                target_column="x",
                task_type="invalid_type",
            )

    def test_analyze_request_all_task_types(self):
        """4대 분석 유형 모두 허용되는지 확인"""
        data = [{"x": i} for i in range(10)]
        for task_type in ["regression", "classification", "multiclass", "timeseries"]:
            req = AnalyzeRequest(
                data=data,
                target_column="x",
                task_type=task_type,
            )
            assert req.task_type == task_type

    def test_threshold_update_request_range(self):
        """ThresholdUpdateRequest 값 범위 검증 (0.0 ~ 1.0)"""
        from pydantic import ValidationError

        # 정상 범위
        req = ThresholdUpdateRequest(error_threshold=0.15, min_r2_score=0.85)
        assert req.error_threshold == 0.15

        # 범위 초과
        with pytest.raises(ValidationError):
            ThresholdUpdateRequest(error_threshold=1.5)

        with pytest.raises(ValidationError):
            ThresholdUpdateRequest(min_r2_score=-0.1)

    def test_health_response_schema(self):
        """HealthResponse 스키마 정상 생성"""
        from datetime import datetime

        resp = HealthResponse(
            status="healthy",
            version="1.0.0",
            environment="development",
            timestamp=datetime.now(),
        )
        assert resp.status == "healthy"


# ==================== 4. CORS 미들웨어 회귀 테스트 ====================


class TestCORSRegression:
    """CORS 설정 회귀 테스트"""

    def test_cors_preflight_allowed(self):
        """OPTIONS 프리플라이트 요청 허용"""
        response = client.options(
            "/health",
            headers={
                "Origin": "http://localhost:3032",
                "Access-Control-Request-Method": "GET",
            },
        )
        # CORS가 활성화되어 있으면 200
        assert response.status_code == 200

    def test_cors_headers_present(self):
        """응답에 CORS 헤더 포함"""
        response = client.get(
            "/health",
            headers={"Origin": "http://localhost:3032"},
        )
        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers


# ==================== 5. 에러 핸들링 회귀 테스트 ====================


class TestErrorHandlingRegression:
    """에러 핸들링 회귀 테스트"""

    def test_invalid_json_returns_422(self):
        """잘못된 JSON 형식 → 422"""
        response = client.post(
            "/v1/analyze",
            content="not a json",
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 422

    def test_simulate_missing_required_fields_returns_422(self):
        """시뮬레이션 필수 필드 누락 → 422 (404가 아님)"""
        response = client.post("/v1/simulate", json={"task_id": "abc"})
        # scenarios 누락 → 422
        assert response.status_code == 422

    def test_qa_empty_question_returns_422(self):
        """AI Q&A 빈 질문 → 422"""
        response = client.post(
            "/v1/qa/test_task",
            json={"question": ""},
        )
        assert response.status_code == 422


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
