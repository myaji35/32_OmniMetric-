# Changelog

All notable changes to OmniMetric will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.2] - 2026-02-09

### 수정됨 (Fixed)
- **Python 3.14 호환성 개선**:
  - CatBoost를 선택적 import로 변경 (Python 3.14에서 빌드 불가)
  - 알고리즘 레지스트리에서 CatBoost 조건부 등록
  - Python 3.14에서는 59개 알고리즘 지원 (Python 3.11에서는 60개)
  - 파일: `app/models/algorithms/tree_models.py:16-23, 113-125`
  - 파일: `app/models/algorithms/registry.py:70-91`

- **가상환경 호환성 수정**:
  - 손상된 pip 패키지들로 인한 경고 메시지 해결
  - 완전한 가상환경 재생성으로 패키지 충돌 해소
  - numpy, pandas 버전 충돌 문제 해결

- **테스트 수정**:
  - run_simple_test.py에서 알고리즘 개수 검증 59개로 조정
  - CatBoost 없이도 정상 동작하도록 수정
  - 파일: `run_simple_test.py:64-68`

### 업데이트됨 (Changed)
- **requirements.txt 버전 범위 확장**:
  - 고정 버전(==)에서 최소 버전(>=)으로 변경
  - scikit-learn: ==1.3.2 → >=1.4.0
  - pandas: ==1.5.3 → >=2.0.0
  - numpy: ==1.24.3 → >=1.24.0
  - 기타 패키지들도 유연한 버전 허용

- **문서 업데이트**:
  - README.md에 Python 3.14 호환성 주의사항 추가
  - Python 3.11 권장 사항 명시
  - 알고리즘 개수 59개로 업데이트 (CatBoost 제외)

### 테스트 결과 (Python 3.14)
```
🚀 간단한 테스트 모두 통과!

✅ 테스트 1: 기본 알고리즘 실행
   - OLS: R² = 0.9978
   - Ridge: R² = 0.9976

✅ 테스트 2: 알고리즘 레지스트리
   - 등록된 알고리즘: 59개 (CatBoost 제외)
   - 중복 없음
   - OLS: R²=0.9973
   - Ridge: R²=0.9960
   - Lasso: R²=0.9853

✅ 테스트 3: 데이터 전처리
   - X 형태: (100, 3)
   - y 형태: (100,)
   - 결측치: 0
```

### 알려진 제한사항
- **Python 3.14 환경**:
  - Ray 패키지 설치 불가 → 전체 pytest 테스트 실행 불가
  - CatBoost 빌드 실패 → 59개 알고리즘만 사용 가능
  - 간단한 테스트(run_simple_test.py)는 정상 동작

- **권장 사항**: 전체 기능을 사용하려면 Python 3.11 또는 3.12 사용

## [1.0.1] - 2026-02-09

### 수정됨 (Fixed)
- **Lasso 회귀 알고리즘 alpha 값 조정**: alpha=1.0 → alpha=0.1로 변경하여 작은 데이터셋에서 성능 개선
  - 이전: 모든 계수가 0으로 수렴하여 R² = 0.0000
  - 현재: 정상적으로 작동하여 R² > 0.98 달성
  - 파일: `app/models/algorithms/linear_models.py:53`

- **ElasticNet 회귀 알고리즘 alpha 값 조정**: alpha=1.0 → alpha=0.1로 변경
  - 파일: `app/models/algorithms/linear_models.py:68`

- **Ensemble ElasticNet 모델 alpha 값 조정**:
  - ElasticNet_L1 (L1 heavy): alpha=1.0 → alpha=0.1
  - ElasticNet_L2 (L2 heavy): alpha=1.0 → alpha=0.1
  - 파일: `app/models/algorithms/ensemble_models.py:326, 347`

### 업데이트됨 (Changed)
- **requirements.txt 의존성 버전 업데이트**:
  - PyCaret 제거 (의존성 충돌 방지)
  - scikit-learn: 1.2.2 → 1.3.2
  - xgboost: 1.7.6 → 2.0.3
  - numpy: 1.23.5 → 1.24.3
  - pandas: 호환 가능한 버전(1.5.3) 유지
  - polars: 제거 (불필요한 의존성)

### 추가됨 (Added)
- **간단한 테스트 스크립트** (`run_simple_test.py`):
  - Ray/Redis 없이도 실행 가능한 독립형 테스트
  - 기본 알고리즘 실행 테스트
  - 60개 알고리즘 레지스트리 검증
  - 데이터 전처리 파이프라인 테스트
  - Docker 환경에서 자동 실행 가능

- **.dockerignore 파일**:
  - 빌드 속도 향상 및 이미지 크기 최적화
  - venv, git, 로그 파일 등 제외

### 테스트 결과
```
✅ 테스트 1: 기본 알고리즘 실행
   - OLS: R² = 0.9978
   - Ridge: R² = 0.9976

✅ 테스트 2: 알고리즘 레지스트리
   - 등록된 알고리즘: 60개
   - 중복 없음
   - OLS: R²=0.9973
   - Ridge: R²=0.9960
   - Lasso: R²=0.9853 (수정 후 정상 작동!)

✅ 테스트 3: 데이터 전처리
   - X 형태: (100, 3)
   - y 형태: (100,)
   - 결측치: 0
```

## [1.0.0] - 2026-02-01

### 초기 릴리스
- 60개 알고리즘 토너먼트 시스템
- Ray 기반 병렬 처리
- SHAP/LIME XAI 통합
- 자연어 리포트 생성
- MLOps 자가 보정 기능
- FastAPI 기반 RESTful API
- Redis 기반 작업 저장소
- Webhook 알림 시스템
