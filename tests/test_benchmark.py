"""
Performance Benchmark Tests
성능 벤치마크 테스트 스위트
"""
import pytest
import pandas as pd
import numpy as np
import time
from datetime import datetime

from app.core.engine import TournamentEngine
from app.models.schemas import AnalyzeRequest


class TestPerformanceBenchmark:
    """성능 벤치마크 테스트"""

    @pytest.fixture
    def sample_data_1k(self):
        """1,000행 샘플 데이터"""
        np.random.seed(42)
        n_samples = 1000
        n_features = 5

        X = np.random.randn(n_samples, n_features)
        y = 2 * X[:, 0] + 3 * X[:, 1] - 1.5 * X[:, 2] + np.random.randn(n_samples) * 0.1

        df = pd.DataFrame(X, columns=[f"feature_{i}" for i in range(n_features)])
        df["target"] = y

        return df.to_dict(orient="records")

    @pytest.fixture
    def sample_data_10k(self):
        """10,000행 샘플 데이터"""
        np.random.seed(42)
        n_samples = 10000
        n_features = 10

        X = np.random.randn(n_samples, n_features)
        y = sum(X[:, i] * (i + 1) for i in range(5)) + np.random.randn(n_samples) * 0.5

        df = pd.DataFrame(X, columns=[f"feature_{i}" for i in range(n_features)])
        df["target"] = y

        return df.to_dict(orient="records")

    @pytest.mark.asyncio
    async def test_1k_rows_performance(self, sample_data_1k):
        """1,000행 데이터 처리 성능 테스트"""
        engine = TournamentEngine()

        request = AnalyzeRequest(
            data=sample_data_1k,
            target_column="target",
            task_type="regression",
            enable_xai=False
        )

        start_time = time.time()

        # 데이터 전처리
        X, y = engine.prepare_data(request)

        # 알고리즘 로드
        algorithms = engine.algorithm_registry.get_all_algorithms("regression")

        # 토너먼트 실행
        results = engine.parallel_tournament.run_tournament(algorithms, X, y)

        # 승자 선정
        winner = engine.parallel_tournament.get_winner(results)

        elapsed = time.time() - start_time

        # 성능 검증
        assert elapsed < 120, f"1,000행 처리 시간 초과: {elapsed:.2f}초 (목표: 120초 이내)"
        assert winner["r2_score"] > 0.5, f"R² 점수 너무 낮음: {winner['r2_score']:.4f}"

        print(f"\n✅ 1K 행 벤치마크:")
        print(f"   - 처리 시간: {elapsed:.2f}초")
        print(f"   - 승자: {winner['algorithm_name']}")
        print(f"   - R² 점수: {winner['r2_score']:.4f}")
        print(f"   - 테스트된 알고리즘: {len(results)}개")

    @pytest.mark.asyncio
    async def test_10k_rows_performance(self, sample_data_10k):
        """10,000행 데이터 처리 성능 테스트 (PRD 목표)"""
        engine = TournamentEngine()

        request = AnalyzeRequest(
            data=sample_data_10k,
            target_column="target",
            task_type="regression",
            enable_xai=False
        )

        start_time = time.time()

        X, y = engine.prepare_data(request)
        algorithms = engine.algorithm_registry.get_all_algorithms("regression")
        results = engine.parallel_tournament.run_tournament(algorithms, X, y)
        winner = engine.parallel_tournament.get_winner(results)

        elapsed = time.time() - start_time

        # PRD 목표: 1만 행 1분 이내
        assert elapsed < 60, f"10,000행 처리 시간 목표 미달성: {elapsed:.2f}초 (목표: 60초 이내)"
        assert winner["r2_score"] >= 0.85, f"R² 목표 미달성: {winner['r2_score']:.4f} (목표: 0.85)"

        print(f"\n🎯 10K 행 벤치마크 (PRD 목표):")
        print(f"   - 처리 시간: {elapsed:.2f}초 / 60초")
        print(f"   - 승자: {winner['algorithm_name']}")
        print(f"   - R² 점수: {winner['r2_score']:.4f} / 0.85")
        print(f"   - 초당 처리량: {len(sample_data_10k) / elapsed:.0f} 행/초")

    def test_algorithm_count(self):
        """등록된 알고리즘 수 검증"""
        engine = TournamentEngine()
        # 회귀분석 알고리즘 수 (CatBoost Python 3.14 미호환으로 59개)
        algorithm_count = engine.algorithm_registry.get_algorithm_count()
        assert algorithm_count == 59, f"회귀 알고리즘 수 불일치: {algorithm_count} (목표: 59)"

        # 전체 알고리즘 수 (4대 유형 합산)
        total = engine.algorithm_registry.get_total_count()
        assert total == 154, f"총 알고리즘 수 불일치: {total} (목표: 154)"

    def test_data_preprocessing_speed(self):
        """데이터 전처리 속도 테스트"""
        np.random.seed(42)
        n_samples = 10000
        n_features = 20

        X = np.random.randn(n_samples, n_features)
        y = np.random.randn(n_samples)

        df = pd.DataFrame(X, columns=[f"feature_{i}" for i in range(n_features)])
        df["target"] = y

        # 결측치 추가
        for col in df.columns[:5]:
            mask = np.random.random(n_samples) < 0.1
            df.loc[mask, col] = np.nan

        data = df.to_dict(orient="records")

        engine = TournamentEngine()
        request = AnalyzeRequest(
            data=data,
            target_column="target",
            task_type="regression",
            enable_xai=False
        )

        start_time = time.time()
        X_processed, y_processed = engine.prepare_data(request)
        elapsed = time.time() - start_time

        assert elapsed < 5, f"전처리 시간 초과: {elapsed:.2f}초 (목표: 5초 이내)"
        assert X_processed.isnull().sum().sum() == 0, "결측치 처리 실패"

        print(f"\n⚡ 전처리 성능:")
        print(f"   - 처리 시간: {elapsed:.4f}초")
        print(f"   - 데이터 형태: {X_processed.shape}")
        print(f"   - 결측치 제거: ✅")


class TestXAIPerformance:
    """XAI 성능 테스트"""

    @pytest.fixture
    def xai_test_data(self):
        """XAI 테스트용 데이터"""
        np.random.seed(42)
        n_samples = 500
        n_features = 8

        X = np.random.randn(n_samples, n_features)
        y = 2 * X[:, 0] + X[:, 1] + np.random.randn(n_samples) * 0.1

        df = pd.DataFrame(X, columns=[f"feature_{i}" for i in range(n_features)])
        df["target"] = y

        return df.to_dict(orient="records")

    @pytest.mark.asyncio
    async def test_xai_overhead(self, xai_test_data):
        """XAI 활성화 시 오버헤드 측정"""
        from app.services.xai import XAIEngine
        from sklearn.linear_model import LinearRegression

        engine = TournamentEngine()
        request = AnalyzeRequest(
            data=xai_test_data,
            target_column="target",
            task_type="regression",
            enable_xai=True
        )

        X, y = engine.prepare_data(request)

        # 모델 학습
        model = LinearRegression()
        model.fit(X, y)

        # XAI 엔진 초기화
        xai_engine = XAIEngine()

        start_time = time.time()
        xai_result = xai_engine.explain_model(model, X, y, "LinearRegression")
        elapsed = time.time() - start_time

        # XAI 오버헤드 10초 이내 목표
        assert elapsed < 10, f"XAI 처리 시간 초과: {elapsed:.2f}초"
        assert xai_result.get("top_features"), "XAI 특성 추출 실패"

        print(f"\n🔍 XAI 성능:")
        print(f"   - 처리 시간: {elapsed:.2f}초")
        print(f"   - 상위 특성: {xai_result.get('top_features', [])[:3]}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
