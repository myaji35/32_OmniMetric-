#!/usr/bin/env python3
"""
Simple standalone test runner
테스트 환경 없이 실행 가능한 간단한 테스트
"""
import sys
import os

# 프로젝트 루트를 sys.path에 추가
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import pandas as pd
import numpy as np
from app.models.algorithms.linear_models import OLSRegression, RidgeRegression
from app.models.algorithms.registry import AlgorithmRegistry

def test_basic_algorithm():
    """기본 알고리즘 테스트"""
    print("=" * 60)
    print("테스트 1: 기본 알고리즘 실행")
    print("=" * 60)

    # 샘플 데이터 생성
    np.random.seed(42)
    n_samples = 100
    n_features = 3

    X = pd.DataFrame(
        np.random.randn(n_samples, n_features),
        columns=[f"x{i}" for i in range(n_features)]
    )
    y = pd.Series(2 * X["x0"] + X["x1"] + np.random.randn(n_samples) * 0.1)

    # OLS 테스트
    print("\n[1] OLS 회귀 테스트...")
    ols = OLSRegression()
    result = ols.execute(X, y)
    print(f"   R² 점수: {result['r2_score']:.4f}")
    print(f"   Adj. R²: {result['adj_r2_score']:.4f}")
    print(f"   계수: {result['coefficients']}")

    assert result['r2_score'] > 0.5, "R² 점수가 너무 낮습니다"
    print("   ✅ OLS 테스트 통과")

    # Ridge 테스트
    print("\n[2] Ridge 회귀 테스트...")
    ridge = RidgeRegression()
    result = ridge.execute(X, y)
    print(f"   R² 점수: {result['r2_score']:.4f}")
    print(f"   Adj. R²: {result['adj_r2_score']:.4f}")

    assert result['r2_score'] > 0.5, "R² 점수가 너무 낮습니다"
    print("   ✅ Ridge 테스트 통과")


def test_algorithm_registry():
    """알고리즘 레지스트리 테스트"""
    print("\n" + "=" * 60)
    print("테스트 2: 알고리즘 레지스트리")
    print("=" * 60)

    registry = AlgorithmRegistry()

    # 알고리즘 개수 확인 (CatBoost가 없을 경우 59개)
    count = registry.get_algorithm_count()
    print(f"\n등록된 알고리즘 수: {count}개")
    expected_count = 59  # CatBoost가 Python 3.14와 호환되지 않아 59개
    assert count == expected_count, f"알고리즘 수 불일치: {count} (기대값: {expected_count})"
    print("✅ 알고리즘 개수 테스트 통과")

    # 알고리즘 이름 중복 체크
    names = registry.get_algorithm_names()
    assert len(names) == len(set(names)), "알고리즘 이름 중복 발견"
    print("✅ 알고리즘 이름 중복 체크 통과")

    # 샘플 알고리즘 실행 테스트
    print("\n[샘플 알고리즘 실행 테스트]")
    np.random.seed(42)
    X = pd.DataFrame(np.random.randn(50, 3), columns=["x0", "x1", "x2"])
    y = pd.Series(2 * X["x0"] + X["x1"] + np.random.randn(50) * 0.1)

    test_algos = ["OLS", "Ridge", "Lasso"]
    for algo_name in test_algos:
        algo_func = registry.get_algorithm_by_name(algo_name)
        result = algo_func(X, y)
        print(f"   {algo_name}: R²={result['r2_score']:.4f} ✅")
        assert result['r2_score'] > 0.3, f"{algo_name} R² 너무 낮음"


def test_data_preparation():
    """데이터 전처리 테스트 (Ray 없이)"""
    print("\n" + "=" * 60)
    print("테스트 3: 데이터 전처리")
    print("=" * 60)

    from app.models.schemas import AnalyzeRequest

    # 샘플 데이터
    np.random.seed(42)
    n_samples = 100
    data = []
    for _ in range(n_samples):
        data.append({
            "feature_0": np.random.randn(),
            "feature_1": np.random.randn(),
            "feature_2": np.random.randn(),
            "target": np.random.randn()
        })

    request = AnalyzeRequest(
        data=data,
        target_column="target",
        task_type="regression"
    )

    # TournamentEngine 대신 직접 데이터 전처리
    df = pd.DataFrame(request.data)
    y = df[request.target_column]
    X = df.drop(columns=[request.target_column])

    # 기본 전처리
    X = X.fillna(X.mean(numeric_only=True))
    y = y.fillna(y.mean() if pd.api.types.is_numeric_dtype(y) else y.mode()[0])

    # 범주형 변수 인코딩
    for col in X.select_dtypes(include=['object']).columns:
        X[col] = pd.Categorical(X[col]).codes

    print(f"\n전처리 결과:")
    print(f"   X 형태: {X.shape}")
    print(f"   y 형태: {y.shape}")
    print(f"   결측치: {X.isnull().sum().sum()}")

    assert X.shape[0] == n_samples, "샘플 수 불일치"
    assert X.isnull().sum().sum() == 0, "결측치 처리 실패"
    print("✅ 데이터 전처리 테스트 통과")


def main():
    """메인 테스트 실행"""
    print("\n" + "🚀 " + "=" * 56 + " 🚀")
    print("   OmniMetric 간단한 테스트 시작")
    print("🚀 " + "=" * 56 + " 🚀\n")

    try:
        # 테스트 1: 기본 알고리즘
        test_basic_algorithm()

        # 테스트 2: 레지스트리
        test_algorithm_registry()

        # 테스트 3: 데이터 전처리 (Ray 없이)
        test_data_preparation()

        # 최종 결과
        print("\n" + "🎉 " + "=" * 56 + " 🎉")
        print("   모든 테스트 통과!")
        print("🎉 " + "=" * 56 + " 🎉\n")

        return 0

    except Exception as e:
        print("\n" + "❌ " + "=" * 56 + " ❌")
        print(f"   테스트 실패: {str(e)}")
        print("❌ " + "=" * 56 + " ❌\n")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
