"""
Integration Tests
통합 테스트 - 전체 파이프라인 검증
"""
import pytest
import pandas as pd
import numpy as np
from uuid import uuid4

from app.models.schemas import AnalyzeRequest
from app.core.engine import TournamentEngine
from app.services.mlops import MLOpsEngine


class TestEndToEndPipeline:
    """엔드투엔드 파이프라인 테스트"""

    @pytest.fixture
    def integration_data(self):
        """통합 테스트용 데이터"""
        np.random.seed(42)
        n_samples = 200
        n_features = 5

        X = np.random.randn(n_samples, n_features)
        y = 3 * X[:, 0] + 2 * X[:, 1] - X[:, 2] + np.random.randn(n_samples) * 0.2

        df = pd.DataFrame(X, columns=[f"var_{i}" for i in range(n_features)])
        df["outcome"] = y

        return df.to_dict(orient="records")

    @pytest.mark.asyncio
    async def test_full_analysis_pipeline(self, integration_data):
        """전체 분석 파이프라인 테스트"""
        task_id = str(uuid4())
        engine = TournamentEngine()

        request = AnalyzeRequest(
            data=integration_data,
            target_column="outcome",
            task_type="regression",
            enable_xai=True
        )

        # 파이프라인 실행
        await engine.run_tournament(task_id, request)

        # 결과 검증
        report = await engine.storage.get_report(task_id)

        assert report is not None, "리포트 생성 실패"
        assert report.status == "completed", f"작업 상태 오류: {report.status}"
        assert report.winner.r2_score > 0.7, f"R² 점수 낮음: {report.winner.r2_score}"
        assert len(report.top_5_algorithms) == 5, "상위 5개 알고리즘 누락"
        assert report.xai_insights is not None, "XAI 통찰 누락"
        assert report.report is not None, "자연어 리포트 누락"

        print(f"\n✅ 전체 파이프라인 테스트 성공:")
        print(f"   - 작업 ID: {task_id}")
        print(f"   - 승자: {report.winner.algorithm}")
        print(f"   - R² 점수: {report.winner.r2_score:.4f}")
        print(f"   - 테스트된 알고리즘: {report.total_algorithms_tested}개")

    @pytest.mark.asyncio
    async def test_mlops_monitoring(self, integration_data):
        """MLOps 모니터링 기능 테스트"""
        from sklearn.linear_model import LinearRegression

        engine = TournamentEngine()
        mlops = MLOpsEngine()

        request = AnalyzeRequest(
            data=integration_data,
            target_column="outcome",
            task_type="regression",
            enable_xai=False
        )

        # 데이터 전처리
        X, y = engine.prepare_data(request)

        # 모델 학습
        model = LinearRegression()
        model.fit(X, y)

        # 새로운 데이터 생성 (드리프트 시뮬레이션)
        X_new = X.copy()
        y_new = y.copy()

        # 성능 모니터링
        task_id = str(uuid4())
        monitoring_result = await mlops.monitor_model_performance(
            task_id=task_id,
            model=model,
            X_new=X_new,
            y_true=y_new
        )

        assert monitoring_result is not None, "모니터링 결과 누락"
        assert "metrics" in monitoring_result, "오차 지표 누락"
        assert monitoring_result["metrics"]["r2_score"] > 0.5, "모니터링 R² 낮음"

        print(f"\n📊 MLOps 모니터링 테스트:")
        print(f"   - R² 점수: {monitoring_result['metrics']['r2_score']:.4f}")
        print(f"   - MAPE: {monitoring_result['metrics']['mape']:.4f}")
        print(f"   - 재학습 필요: {monitoring_result['needs_retrain']}")


class TestAlgorithmCoverage:
    """알고리즘 커버리지 테스트"""

    def test_all_algorithms_loadable(self):
        """모든 알고리즘 로드 가능 여부 테스트"""
        from app.models.algorithms.registry import AlgorithmRegistry

        registry = AlgorithmRegistry()
        algorithms = registry.get_all_algorithms("regression")

        # CatBoost가 Python 3.14와 호환되지 않아 59개
        assert len(algorithms) == 59, f"회귀 알고리즘 수 불일치: {len(algorithms)}"

        # 모든 알고리즘 이름 중복 확인
        names = [name for name, _ in algorithms]
        assert len(names) == len(set(names)), "알고리즘 이름 중복 발견"

    def test_all_analysis_types(self):
        """4대 분석유형 알고리즘 수 검증"""
        from app.models.algorithms.registry import AlgorithmRegistry

        registry = AlgorithmRegistry()

        assert len(registry.get_all_algorithms("regression")) == 59
        assert len(registry.get_all_algorithms("classification")) == 17
        assert len(registry.get_all_algorithms("multiclass")) == 17
        assert len(registry.get_all_algorithms("timeseries")) == 61

        total = registry.get_total_count()
        assert total == 154, f"총 알고리즘 수 불일치: {total} (목표: 154)"

    def test_sample_algorithms_execution(self):
        """샘플 알고리즘 실행 테스트"""
        from app.models.algorithms.registry import AlgorithmRegistry

        np.random.seed(42)
        n_samples = 100
        n_features = 3

        X = pd.DataFrame(
            np.random.randn(n_samples, n_features),
            columns=[f"x{i}" for i in range(n_features)]
        )
        y = pd.Series(2 * X["x0"] + X["x1"] + np.random.randn(n_samples) * 0.1)

        registry = AlgorithmRegistry()

        # 샘플 알고리즘 테스트 (각 카테고리에서 1개씩)
        test_algos = ["OLS", "RandomForest", "SVR_Linear", "VotingEnsemble"]

        for algo_name in test_algos:
            algo_func = registry.get_algorithm_by_name(algo_name)
            result = algo_func(X, y)

            assert "r2_score" in result, f"{algo_name}: R2 점수 누락"
            assert "coefficients" in result, f"{algo_name}: 계수 누락"

    def test_timeseries_algorithm_execution(self):
        """시계열 알고리즘 실행 테스트"""
        from app.models.algorithms.timeseries.ts_models import (
            NaiveMeanModel, LinearTS, RandomForestTS,
        )

        np.random.seed(42)
        n = 100
        y = pd.Series(np.sin(np.linspace(0, 8 * np.pi, n)) + np.random.normal(0, 0.1, n))
        X = pd.DataFrame({"dummy": range(n)})

        for algo_cls in [NaiveMeanModel, LinearTS, RandomForestTS]:
            algo = algo_cls()
            result = algo.execute(X, y)
            assert "r2_score" in result, f"{algo.name}: R2 누락"


class TestFeatureEngineering:
    """파생변수 생성 테스트"""

    def test_feature_generation(self):
        """파생변수 생성 테스트"""
        from app.services.feature_engineering import FeatureEngineer

        np.random.seed(42)
        dates = pd.date_range("2020-01-01", periods=100, freq="D")
        data = pd.DataFrame({
            "date": dates,
            "value": np.sin(np.linspace(0, 4 * np.pi, 100)) * 100 + 200,
        })

        result = FeatureEngineer.generate_all_features(
            data, target_column="value", date_column="date"
        )

        feature_count = len([c for c in result.columns if c not in ["date", "value"]])
        assert feature_count > 100, f"파생변수 부족: {feature_count}"
        assert result.isnull().sum().sum() == 0, "NaN 잔존"


class TestSim4Brief:
    """Sim4Brief 리포트 테스트"""

    def test_brief_report(self):
        from app.services.nlg import NLGReportGenerator

        winner = {"algorithm_name": "XGBoost", "r2_score": 0.92, "coefficients": {}}
        result = NLGReportGenerator.generate_sim4brief(
            winner, {}, [winner], "Y=...", detail_level="brief"
        )
        assert result["level"] == "brief"
        assert "XGBoost" in result["summary"]

    def test_comprehensive_report(self):
        from app.services.nlg import NLGReportGenerator

        winner = {"algorithm_name": "RF", "r2_score": 0.88, "execution_time": 1.0, "coefficients": {"x": 0.5}}
        importance = {"x": 100.0}
        result = NLGReportGenerator.generate_sim4brief(
            winner, importance, [winner], "Y=0.5*x", detail_level="comprehensive"
        )
        assert result["level"] == "comprehensive"
        assert result["quality_assessment"]["grade"] == "A"
        assert len(result["variable_analysis"]) == 1


class TestAIQA:
    """AI Q&A 테스트"""

    def test_local_answer(self):
        from app.services.ai_qa import AIQuestionAnswer

        qa = AIQuestionAnswer()
        context = {
            "winner": {"algorithm_name": "XGBoost", "r2_score": 0.92, "coefficients": {"x": 0.5}},
            "report": {"summary": "테스트"},
        }
        answer = qa._generate_local_answer("최적 모델은?", context)
        assert "XGBoost" in answer


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
