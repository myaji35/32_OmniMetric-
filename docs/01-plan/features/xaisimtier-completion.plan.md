# XAISimTier (OmniMetric) 완성 계획서

> **Summary**: PRD v2.0 기준 125종 알고리즘 토너먼트, 4대 분석유형, What-if 시뮬레이션, 최적화, 보안 강화 등 전체 기능 완성
>
> **Project**: OmniMetric (XAISimTier)
> **Version**: 2.0
> **Author**: CTO Lead Agent
> **Date**: 2026-03-12
> **Status**: Draft

---

## 1. Overview

### 1.1 Purpose

PRD v2.0에 정의된 OmniMetric(XAISimTier) 제품의 전체 기능을 구현하여 제품 출시 가능 상태로 완성합니다. 현재 회귀분석 60종 알고리즘 토너먼트만 구현된 상태에서 125종+ 알고리즘, 4대 분석유형, 시뮬레이션/최적화 파이프라인, 보안 강화까지 완성합니다.

### 1.2 Background

- PRD v2.0 기준 현재 구현률: 약 40% (회귀분석 토너먼트만 완성)
- Train/Test Split 미적용으로 과적합 위험 (CRITICAL)
- 분류/다중분류/시계열 분석이 전혀 미구현
- What-if 시뮬레이션, 최적화 등 PRD 핵심 기능 미구현
- 보안 취약점 다수 존재 (하드코딩 비밀번호, CORS, Rate Limiting 등)

### 1.3 Related Documents

- PRD: `/Volumes/E_SSD/02_GitHub.nosync/0032_OmniMetric/prd.md`
- 참고 PDF: `7.0.업무데이터를 활용한 AI기반 시뮬레이션_260308 2212.pdf`

---

## 2. Scope

### 2.1 In Scope

- [x] 회귀분석 30종 알고리즘 토너먼트 (완료, 현재 60종 -> PRD 기준 30종으로 정리)
- [ ] Train/Test Split 적용 (과적합 방지)
- [ ] 분류분석 17종 알고리즘
- [ ] 다중분류분석 17종 알고리즘
- [ ] 시계열분석 61종 알고리즘 + 자동 파생변수 500개
- [ ] What-if 시뮬레이션 (`/v1/simulate`)
- [ ] 목표 달성 최적화 (`/v1/optimize`)
- [ ] WhatDataAI 데이터 사전분석 (`/v1/whatdata`)
- [ ] 행동 시나리오 변환 (`/v1/actions`)
- [ ] CSV 파일 업로드 지원
- [ ] Sim4Brief Report 강화
- [ ] AI Q&A 기능
- [ ] MLOps 실제 재학습 로직 완성
- [ ] 보안 강화 (Rate Limiting, SSRF 방어, 입력 크기 제한)
- [ ] God Object 리팩토링 (TournamentEngine SRP 분리)

### 2.2 Out of Scope

- 프론트엔드 UI (순수 백엔드 API만 구현)
- LLM 지식그래프 연동 (GPT 기반, 별도 프로젝트)
- 현황분석 (차트, 워드클라우드, 주제도) - 프론트엔드 의존
- Kubernetes/Terraform 인프라 구성
- 6대 산업 도메인별 커스텀 로직

---

## 3. Requirements

### 3.1 Functional Requirements

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| FR-01 | Train/Test Split 적용 (80:20) + Cross-Validation | P0-Critical | Pending |
| FR-02 | 분류분석 17종 알고리즘 토너먼트 | P0-High | Pending |
| FR-03 | 다중분류분석 17종 알고리즘 토너먼트 | P0-High | Pending |
| FR-04 | What-if 시뮬레이션 API (`/v1/simulate`) | P0-High | Pending |
| FR-05 | 시계열분석 61종 알고리즘 + 자동 파생변수 | P1-High | Pending |
| FR-06 | 목표 달성 최적화 API (`/v1/optimize`) | P1-High | Pending |
| FR-07 | WhatDataAI 사전분석 API (`/v1/whatdata`) | P1-Medium | Pending |
| FR-08 | 행동 시나리오 변환 API (`/v1/actions`) | P1-Medium | Pending |
| FR-09 | CSV 파일 업로드 지원 | P1-Medium | Pending |
| FR-10 | Sim4Brief Report (LLM 기반 자연어 리포트 강화) | P2-Medium | Pending |
| FR-11 | AI Q&A 기능 | P2-Low | Pending |
| FR-12 | MLOps 실제 재학습 로직 완성 | P2-Medium | Pending |

### 3.2 Non-Functional Requirements

| Category | Criteria | Measurement Method |
|----------|----------|-------------------|
| Performance | 1만행, 125개 알고리즘 검토 1분 이내 | 벤치마크 테스트 |
| Accuracy | 주력 도메인 R^2 >= 0.85 | 테스트 데이터셋 |
| Security | Rate Limiting, SSRF 방어, 입력 크기 제한 | 보안 테스트 |
| Security | 하드코딩 비밀번호 제거, CORS 적절한 설정 | 코드 리뷰 |
| Reliability | 실패 알고리즘 격리, 전체 토너먼트 중단 방지 | 통합 테스트 |
| Maintainability | God Object 분리, Factory 패턴 적용 | 코드 리뷰 |

---

## 4. Success Criteria

### 4.1 Definition of Done

- [ ] 4대 분석유형 모두 작동 (회귀/분류/다중분류/시계열)
- [ ] Train/Test Split 적용, 과적합 검증 통과
- [ ] 모든 API 엔드포인트 구현 및 테스트 통과
- [ ] 보안 취약점 0건 (CRITICAL)
- [ ] 통합 테스트 커버리지 80% 이상
- [ ] PRD v2.0 매칭률 90% 이상

### 4.2 Quality Criteria

- [ ] 테스트 커버리지 80% 이상
- [ ] Lint 에러 0건
- [ ] 타입 힌트 100% 적용
- [ ] API 문서 (Swagger) 완전

---

## 5. Risks and Mitigation

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| 과적합 (Train/Test Split 미적용) | Critical | High | 최우선 구현, K-Fold CV 적용 |
| 시계열 61종 알고리즘 복잡도 | High | High | 단계별 구현, 핵심 10종 우선 |
| 파생변수 500개 생성 메모리 부하 | High | Medium | 청크 단위 생성, 메모리 제한 |
| ProcessPoolExecutor 피클링 이슈 | Medium | High | ThreadPoolExecutor 대안, in-process 실행 |
| 보안 취약점 운영 환경 노출 | Critical | Medium | P0에서 즉시 해결 |
| God Object 리팩토링 범위 확대 | Medium | Medium | 인터페이스 유지하며 내부만 분리 |

---

## 6. Architecture Considerations

### 6.1 Project Level Selection

| Level | Characteristics | Recommended For | Selected |
|-------|-----------------|-----------------|:--------:|
| **Starter** | Simple structure | Static sites | |
| **Dynamic** | Feature-based modules, BaaS | Web apps, SaaS MVPs | |
| **Enterprise** | Strict layer separation, DI, microservices | High-traffic systems | X |

### 6.2 Key Architectural Decisions

| Decision | Options | Selected | Rationale |
|----------|---------|----------|-----------|
| Framework | FastAPI | FastAPI | 이미 구축됨, 비동기 지원 |
| Parallelism | Ray / multiprocessing / ThreadPool | multiprocessing + ThreadPool | Ray 선택적, 피클링 이슈 고려 |
| Storage | Redis | Redis | 이미 구축됨, TTL 기반 작업 관리 |
| ML | scikit-learn / PyCaret | scikit-learn 직접 | 세밀한 제어, 알고리즘별 커스텀 |
| Time Series | Prophet / statsmodels / sktime | statsmodels + sktime | 61종 알고리즘 다양성 확보 |
| Optimization | scipy.optimize / optuna | scipy.optimize | 제약조건 최적화 지원 |
| Testing | pytest | pytest | 이미 설정됨 |

### 6.3 리팩토링 대상 아키텍처

```
현재 구조 (God Object):
TournamentEngine
  ├── prepare_data()
  ├── extract_formula()
  ├── calculate_feature_importance()
  ├── generate_nlg_report()
  └── run_tournament()

목표 구조 (SRP 분리):
app/
├── core/
│   ├── engine.py              → TournamentOrchestrator (오케스트레이터만)
│   ├── parallel.py            → ParallelTournament (유지)
│   ├── preprocessor.py        → DataPreprocessor (NEW)
│   ├── evaluator.py           → ModelEvaluator (NEW: Train/Test Split)
│   └── storage.py             → TaskStorage (유지)
├── models/
│   ├── algorithms/
│   │   ├── base.py            → BaseAlgorithm 확장 (분류/시계열)
│   │   ├── registry.py        → AlgorithmRegistry 확장 (4유형)
│   │   ├── regression/        → 회귀 30종 (NEW: 분리)
│   │   ├── classification/    → 분류 17종 (NEW)
│   │   ├── multiclass/        → 다중분류 17종 (NEW)
│   │   └── timeseries/        → 시계열 61종 (NEW)
│   └── schemas.py             → 확장 (시뮬레이션/최적화 스키마)
├── services/
│   ├── xai.py                 → XAIEngine (유지, 분류 지원 추가)
│   ├── simulator.py           → WhatIfSimulator (NEW)
│   ├── optimizer.py           → GoalOptimizer (NEW)
│   ├── whatdata.py            → WhatDataAnalyzer (NEW)
│   ├── actions.py             → ActionScenarioConverter (NEW)
│   ├── nlg.py                 → NLGReportGenerator (NEW: engine에서 분리)
│   ├── mlops.py               → MLOpsEngine (완성)
│   └── webhook.py             → WebhookService (유지)
├── api/v1/endpoints/
│   ├── analyze.py             → 확장 (4유형 지원)
│   ├── report.py              → 유지
│   ├── simulate.py            → NEW
│   ├── optimize.py            → NEW
│   ├── whatdata.py            → NEW
│   ├── actions.py             → NEW
│   ├── upload.py              → NEW (CSV 업로드)
│   └── threshold.py           → 유지
└── security/                  → NEW
    ├── rate_limiter.py
    ├── input_validator.py
    └── ssrf_guard.py
```

---

## 7. Implementation Phases (스프린트 계획)

### Phase 1: 기반 강화 + 치명적 이슈 해결 (P0)
**예상 소요: 1일**

1. **Train/Test Split 적용** (FR-01)
   - `app/core/evaluator.py` 신규 생성
   - 80:20 Split + Optional K-Fold CV
   - BaseAlgorithm.execute()에서 전체 데이터 학습 -> Split 기반으로 변경
   - R^2, Adj R^2를 테스트셋 기준으로 재계산

2. **보안 강화**
   - 하드코딩 비밀번호 제거 (환경변수 필수화)
   - CORS 적절한 설정 (allow_origins 제한)
   - Rate Limiting (slowapi 적용)
   - Webhook URL SSRF 방어 (private IP 차단)
   - 입력 데이터 크기 제한 (행 수, 파일 크기)

3. **TournamentEngine 리팩토링**
   - DataPreprocessor 분리
   - NLGReportGenerator 분리
   - ModelEvaluator 분리

### Phase 2: 분류/다중분류 분석 (P0)
**예상 소요: 1일**

4. **분류분석 17종 알고리즘** (FR-02)
   - `app/models/algorithms/classification/` 디렉토리
   - LogisticRegression, SVM, RandomForest, XGBoost, LightGBM, CatBoost 등
   - 평가지표: Accuracy, Precision, Recall, F1, AUC-ROC
   - BaseAlgorithm 확장 -> ClassificationAlgorithm

5. **다중분류분석 17종 알고리즘** (FR-03)
   - `app/models/algorithms/multiclass/` 디렉토리
   - OvR/OvO 전략 포함
   - 평가지표: Macro/Micro F1, Confusion Matrix

6. **AlgorithmRegistry 4유형 지원**
   - task_type별 알고리즘 자동 로드
   - `regression`, `classification`, `multiclass`, `timeseries`

### Phase 3: 시뮬레이션 + 최적화 (P0-P1)
**예상 소요: 1일**

7. **What-if 시뮬레이션** (FR-04)
   - `app/services/simulator.py`
   - 학습된 모델에 가상 입력값 주입 -> 예측값 반환
   - 다중 시나리오 비교
   - POST `/v1/simulate`

8. **목표 달성 최적화** (FR-06)
   - `app/services/optimizer.py`
   - scipy.optimize 기반 제약조건 최적화
   - 목표(Y) 달성을 위한 최적 X 조합 탐색
   - 예산, ROI 등 제약조건 지원
   - POST `/v1/optimize`

### Phase 4: 시계열분석 (P1)
**예상 소요: 1.5일**

9. **시계열분석 61종 알고리즘** (FR-05)
   - `app/models/algorithms/timeseries/` 디렉토리
   - ARIMA, SARIMA, Prophet, ExponentialSmoothing 등
   - 핵심 20종 우선 구현, 나머지 점진적 추가
   - 자동 파생변수 생성 엔진 (lag, rolling, diff 등)

10. **자동 파생변수 500개 생성**
    - `app/services/feature_engineering.py`
    - 시간 기반: lag(1~30), rolling_mean, rolling_std
    - 주기 기반: day_of_week, month, quarter, is_weekend
    - 차분: diff(1), diff(2), pct_change
    - 메모리 효율적 청크 단위 생성

### Phase 5: 데이터 분석 + 행동 시나리오 (P1)
**예상 소요: 1일**

11. **WhatDataAI 사전분석** (FR-07)
    - `app/services/whatdata.py`
    - 데이터 특성 자동 분석 (타입, 분포, 결측치, 이상치)
    - 적합 분석 유형 자동 추천
    - GET `/v1/whatdata/{task_id}`

12. **행동 시나리오 변환** (FR-08)
    - `app/services/actions.py`
    - IF-THEN 규칙 자동 생성
    - 임계값 기반 트리거
    - 우선순위 자동 산정 (Impact x Probability)
    - POST/GET `/v1/actions/{task_id}`

13. **CSV 파일 업로드** (FR-09)
    - `app/api/v1/endpoints/upload.py`
    - multipart/form-data 지원
    - 파일 크기 제한, 형식 검증

### Phase 6: 리포트 강화 + MLOps (P2)
**예상 소요: 1일**

14. **Sim4Brief Report 강화** (FR-10)
    - `app/services/nlg.py` 강화
    - 분석유형별 맞춤 리포트 템플릿
    - 변수 영향도 자연어 변환 개선

15. **AI Q&A** (FR-11)
    - 분석 결과 기반 질의응답
    - LLM API 연동 (OpenAI/Anthropic)

16. **MLOps 실제 재학습** (FR-12)
    - 오차 감지 -> 토너먼트 재실행 자동화
    - 데이터 드리프트 감지 -> 알림

---

## 8. Convention Prerequisites

### 8.1 Existing Project Conventions

- [x] `CLAUDE.md` 코딩 컨벤션 존재
- [ ] `docs/01-plan/conventions.md` 미존재
- [ ] `CONVENTIONS.md` 미존재
- [x] `pyproject.toml` 설정 존재
- [ ] `ruff.toml` / `flake8` 미설정

### 8.2 Conventions to Define/Verify

| Category | Current State | To Define | Priority |
|----------|---------------|-----------|:--------:|
| **Naming** | 혼재 (한영 혼용) | snake_case 통일, 한글 docstring만 | High |
| **Folder structure** | 평면 구조 | 분석유형별 모듈 분리 | High |
| **Error handling** | 기본 try/catch | 커스텀 Exception 계층 | Medium |
| **Testing** | 기본 테스트만 | pytest 구조화, fixture 정의 | Medium |

### 8.3 Environment Variables

| Variable | Purpose | Scope | Status |
|----------|---------|-------|:------:|
| `REDIS_HOST` | Redis 연결 | Server | Done |
| `REDIS_PASSWORD` | Redis 인증 | Server | Done |
| `DB_PASSWORD` | DB 비밀번호 | Server | Hardcoded (FIX) |
| `API_KEY` | API 인증 | Server | Done |
| `OPENAI_API_KEY` | LLM 연동 | Server | NEW |
| `RATE_LIMIT_PER_MINUTE` | Rate Limiting | Server | NEW |
| `MAX_UPLOAD_SIZE_MB` | 업로드 제한 | Server | NEW |
| `ALLOWED_ORIGINS` | CORS 설정 | Server | NEW |

---

## 9. Next Steps

1. [x] Plan 문서 작성 (현재)
2. [ ] Design 문서 작성 (`/pdca design xaisimtier-completion`)
3. [ ] Phase 1 구현 시작 (Train/Test Split + 보안 + 리팩토링)
4. [ ] Phase 2-6 순차 구현
5. [ ] Gap Analysis (`/pdca analyze xaisimtier-completion`)

---

## Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 0.1 | 2026-03-12 | Initial draft | CTO Lead Agent |
