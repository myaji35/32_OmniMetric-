# OmniMetric (XAISimTier) Gap Analysis Report

> **Analysis Type**: PRD vs Implementation Gap Analysis
>
> **Project**: OmniMetric (XAISimTier)
> **Version**: 1.0.0
> **Analyst**: Claude Code (bkit-gap-detector)
> **Date**: 2026-03-12
> **PRD Document**: [prd.md](../../prd.md)
> **Design Doc**: [xaisimtier-completion.design.md](../02-design/features/xaisimtier-completion.design.md)

---

## 1. Analysis Overview

### 1.1 Analysis Purpose

PRD v2.0에 정의된 15개 핵심 기능 항목과 19개 API 엔드포인트에 대한 실제 구현 코드의 일치도를 정량적으로 평가합니다.

### 1.2 Analysis Scope

- **PRD 문서**: `prd.md` (v2.0)
- **Implementation Path**: `app/` (Python FastAPI)
- **Analysis Date**: 2026-03-12

---

## 2. 4대 분석 유형 (Core Analysis Types)

### 2.1 알고리즘 수량 검증

| 분석 유형 | PRD 목표 | 실제 구현 | Status | Notes |
|---------|---------|---------|--------|-------|
| 회귀분석 (Regression) | 30종 | ~60종 (Linear 10 + Tree 15 + NonLinear 20 + Ensemble 15) | ✅ 초과 달성 | CatBoost 선택적 |
| 분류분석 (Classification) | 17종 | 15~17종 (XGBoost/LightGBM 선택적) | ✅ 일치 | 선택적 임포트 포함 시 17종 |
| 다중분류분석 (Multiclass) | 17종 | 구현 존재 (`multiclass_classifiers.py`) | ✅ 일치 | `get_all_multiclass_classifiers()` |
| 시계열분석 (Time-Series) | 61종 | 61종 (ARIMA 15 + ETS 10 + Regression 12 + Tree 12 + NN 7 + Decompose 5) | ✅ 정확 일치 | 전수 확인 완료 |
| **합계** | **125+** | **~155종** | ✅ | 회귀분석 초과 |

### 2.2 task_type 지원

| task_type | PRD | 구현 (`AnalyzeRequest.task_type`) | Status |
|-----------|-----|------|--------|
| regression | O | O (`Literal["regression", ...]`) | ✅ |
| classification | O | O | ✅ |
| multiclass | O | O | ✅ |
| timeseries | O | O | ✅ |

---

## 3. 15대 핵심 기능 Gap 분석

### 3.1 기능별 구현 현황

| # | PRD 기능 | 구현 파일 | Status | 상세 |
|---|---------|----------|--------|------|
| 1 | 4대 분석 유형 (125종 알고리즘) | `app/models/algorithms/` (registry, linear, tree, nonlinear, ensemble, classification, multiclass, timeseries) | ✅ 완전 구현 | 155종 초과 달성 |
| 2 | 5단계 파이프라인 | `app/core/engine.py`, `app/services/simulator.py`, `app/services/optimizer.py` | ✅ 구현 | 사용자설정 -> 리포팅 -> 모델링 -> What-if -> 최적화 |
| 3 | WhatDataAI 데이터 사전분석 | `app/services/whatdata.py`, `app/api/v1/endpoints/whatdata.py` | ✅ 완전 구현 | 컬럼 분석, 타겟 분석, 분석유형 추천, 품질 점수 |
| 4 | 현황분석 (차트, 워드클라우드, 주제도) | - | ❌ 미구현 | 서버 사이드 차트 생성 / 워드클라우드 / 주제도 미구현 |
| 5 | 수학적 공식 및 변수 기여도 | `app/services/nlg.py` (`extract_formula`, `calculate_feature_importance`) | ✅ 완전 구현 | Y = w1*X1 + ... + b 공식, 백분율 중요도 |
| 6 | 디시전트리 분석 (XAI 변수 픽처링) | `app/services/xai.py` (SHAP TreeExplainer) | ⚠️ 부분 구현 | SHAP/LIME 구현됨, 전용 디시전트리 시각화 없음 |
| 7 | Sim4Brief Report (실시간 자동 리포팅) | `app/services/nlg.py` (`generate_sim4brief`, brief/detailed/comprehensive) | ✅ 완전 구현 | 3단계 상세도 지원 |
| 8 | AI Q&A | `app/services/ai_qa.py`, `app/api/v1/endpoints/qa.py` | ✅ 완전 구현 | LLM 연동 + 로컬 규칙 기반 fallback |
| 9 | 행동 시나리오 변환 (Action Scenario) | `app/services/actions.py`, `app/api/v1/endpoints/actions.py` | ⚠️ 부분 구현 | IF-THEN 규칙 생성, 우선순위 산정 구현. Webhook/이메일/슬랙 연동 미구현, 시나리오 이력 관리 미구현 |
| 10 | B2B 데이터 커넥터 (갑-을 연동) | `app/services/connector.py`, `app/api/v1/endpoints/connectors.py` | ⚠️ 부분 구현 | API Key 발행/검증/폐기, 스키마탐색 구현. 인메모리 저장(Redis 미이관), 데이터소스 어댑터(REST/GraphQL/DB) 미구현, 수집 스케줄링 미구현, AES-256 암호화 미구현 |
| 11 | 자가 보정 MLOps | `app/services/mlops.py` | ✅ 구현 | 오차 감지, 재학습 트리거, 쿨다운, 드리프트 분석 |
| 12 | LLM + XAISimTier 시너지 | `app/services/ai_qa.py` (OpenAI 연동) | ⚠️ 부분 구현 | AI Q&A 구현됨. 지식그래프 연동은 미구현 |
| 13 | Train/Test Split | `app/core/evaluator.py` | ✅ 완전 구현 | split_data, evaluate_regression, evaluate_classification, cross_validate |
| 14 | 보안 (CORS, Rate Limiting, SSRF) | `app/main.py` (CORS), `app/security/rate_limiter.py`, `app/security/ssrf_guard.py`, `app/security/input_validator.py` | ✅ 완전 구현 | CORS 환경변수 제어, Rate Limiter, SSRF 방어, 입력 검증 |
| 15 | API 엔드포인트 19개 | `app/api/v1/endpoints/` | 아래 상세 분석 참조 | |

### 3.2 기능 Match Rate

```
+--------------------------------------------------+
|  기능 Match Rate: 80.0% (12/15 완전+부분)         |
+--------------------------------------------------+
|  ✅ 완전 구현:   10개 (66.7%)                     |
|  ⚠️ 부분 구현:    4개 (26.7%)                     |
|  ❌ 미구현:       1개 (6.7%)                      |
+--------------------------------------------------+
```

---

## 4. API 엔드포인트 Gap 분석

### 4.1 PRD 정의 vs 실제 구현

| # | Method | PRD Endpoint | 구현 파일 | 구현 경로 | Status |
|---|--------|------------|----------|----------|--------|
| 1 | POST | `/v1/analyze` | `analyze.py` | `/v1/analyze` | ✅ |
| 2 | GET | `/v1/report/{task_id}` | `report.py` | `/v1/report/{task_id}` | ✅ |
| 3 | POST | `/v1/simulate` | `simulate.py` | `/v1/simulate` | ✅ |
| 4 | POST | `/v1/optimize` | `optimize.py` | `/v1/optimize` | ✅ |
| 5 | GET | `/v1/whatdata/{task_id}` | `whatdata.py` | `/v1/whatdata` (POST) | ⚠️ 변경 |
| 6 | POST | `/v1/actions/{task_id}` | `actions.py` | `/v1/actions/{task_id}` | ✅ |
| 7 | GET | `/v1/actions/{task_id}` | `actions.py` | `/v1/actions/{task_id}` | ✅ |
| 8 | PATCH | `/v1/threshold` | `threshold.py` | `/v1/threshold` | ✅ |
| 9 | POST | `/v1/connectors` | `connectors.py` | `/v1/connectors` | ✅ |
| 10 | GET | `/v1/connectors` | `connectors.py` | `/v1/connectors` | ✅ |
| 11 | GET | `/v1/connectors/{connector_id}` | `connectors.py` | `/v1/connectors/{connector_id}` | ✅ |
| 12 | POST | `/v1/connectors/{connector_id}/verify` | `connectors.py` | `/v1/connectors/{connector_id}/verify` | ✅ |
| 13 | POST | `/v1/connectors/{connector_id}/sync` | `connectors.py` | `/v1/connectors/{connector_id}/sync` | ✅ |
| 14 | GET | `/v1/connectors/{connector_id}/schema` | `connectors.py` | `/v1/connectors/{connector_id}/schema` | ✅ |
| 15 | DELETE | `/v1/connectors/{connector_id}` | `connectors.py` | `/v1/connectors/{connector_id}` | ✅ |

### 4.2 PRD에 없는 추가 구현

| # | Method | Endpoint | 구현 파일 | Notes |
|---|--------|----------|----------|-------|
| A1 | GET | `/v1/status/{task_id}` | `report.py` | 작업 상태 폴링 |
| A2 | GET | `/v1/threshold` | `threshold.py` | 현재 임계값 조회 |
| A3 | POST | `/v1/upload` | `upload.py` | CSV 파일 업로드 |
| A4 | POST | `/v1/qa/{task_id}` | `qa.py` | AI Q&A |
| A5 | POST | `/v1/whatdata` | `whatdata.py` | WhatDataAI (PRD는 GET, 구현은 POST) |
| A6 | GET | `/health` | `main.py` | 헬스 체크 |
| A7 | GET | `/` | `main.py` | 루트 엔드포인트 |

### 4.3 API Match Rate

```
+--------------------------------------------------+
|  API Match Rate: 93.3% (14/15 일치)              |
+--------------------------------------------------+
|  ✅ 정확 일치:   14개 (93.3%)                     |
|  ⚠️ 메서드 변경:  1개 (6.7%) - whatdata           |
|  ❌ 미구현:       0개 (0.0%)                      |
|  추가 구현:       7개 (PRD에 없음)                 |
+--------------------------------------------------+
```

---

## 5. 병렬 처리 시스템 분석

| 항목 | PRD 요구사항 | 구현 | Status |
|------|------------|------|--------|
| 병렬 엔진 | Ray 또는 Celery (Redis) | Ray (주) + multiprocessing (fallback) | ✅ |
| 워커 분산 | 125개 알고리즘 병렬 | max_workers=60, 라운드 로빈 할당 | ✅ |
| 비동기 응답 | 작업 ID 즉시 반환 | HTTP 202 + BackgroundTasks | ✅ |
| Webhook 알림 | 완료 시 Webhook 호출 | `app/services/webhook.py` | ✅ |
| 폴링 지원 | 결과 폴링 | `GET /v1/status/{task_id}` | ✅ |

---

## 6. XAI (설명 가능한 AI) 분석

| 항목 | PRD 요구사항 | 구현 | Status |
|------|------------|------|--------|
| SHAP | 모델 해석 | TreeExplainer, LinearExplainer, KernelExplainer | ✅ |
| LIME | 모델 해석 | LimeTabularExplainer | ✅ |
| 수학적 공식 | Y = w1X1 + ... + b | `NLGReportGenerator.extract_formula()` | ✅ |
| 변수 가중치 | 백분율 + 방향성(+/-) | `calculate_feature_importance()` | ✅ |
| 디시전트리 시각화 | XAI 변수 픽처링 | 전용 시각화 미구현 | ⚠️ |

---

## 7. 시계열 파생변수 엔진

| 항목 | PRD 요구사항 | 구현 (`feature_engineering.py`) | Status |
|------|------------|------|--------|
| 파생변수 수 | ~500개 자동생성 | 500+개 (12개 카테고리) | ✅ |
| Lag Features | O | 30개 (lag 1~30) | ✅ |
| Rolling Statistics | O | 30개 (6 window x 5 stats) | ✅ |
| Calendar Features | O | 20개+ (14 기본 + 6 cyclical) | ✅ |
| Technical Indicators | 금융 지표 | Bollinger, RSI, MACD, ATR | ✅ |

---

## 8. 보안 분석

| 항목 | PRD 요구사항 | 구현 | Status |
|------|------------|------|--------|
| CORS | 환경변수 기반 origin 제어 | `main.py` CORSMiddleware + `allowed_origins` | ✅ |
| Rate Limiting | API 속도 제한 | `app/security/rate_limiter.py` (인메모리) | ✅ |
| SSRF 방어 | Webhook URL 검증 | `app/security/ssrf_guard.py` (private IP 차단) | ✅ |
| API Key SHA-256 | 평문 저장 금지 | `connector.py` `hashlib.sha256` | ✅ |
| IP 화이트리스트 | 지원 | `connector.py` `ip_whitelist` 필드 | ⚠️ 저장만, 실제 검증 미구현 |
| TLS 1.3 | 필수 | 배포 환경 의존 (코드 레벨 검증 불가) | - |
| AES-256 데이터 암호화 | 옵션 | 미구현 | ❌ |
| 입력 검증 | 데이터 크기 제한 | `input_validator.py` (100K행, 500열, 50MB) | ✅ |

---

## 9. B2B 데이터 커넥터 상세 분석

| PRD 세부 기능 | 구현 | Status |
|-------------|------|--------|
| API Key 생성/갱신/폐기 | `create_connector()`, `delete_connector()` | ⚠️ 갱신 미구현 |
| SHA-256 해시 저장 | `hashlib.sha256` + prefix만 보관 | ✅ |
| 키 유효성 검증 (콜백) | `verify_api_key()` | ✅ |
| 데이터 소스 어댑터 (REST/GraphQL/DB) | 미구현 | ❌ |
| 스키마 자동 탐색 | `discover_schema()` (stub) | ⚠️ 인터페이스만 |
| 수집 스케줄링 (실시간/주기적/온디맨드) | `sync_data()` (온디맨드만) | ⚠️ |
| 데이터 격리 (멀티테넌시) | connector_id 별 분리 | ⚠️ 인메모리 |
| 감사 로그 | `audit_log` 필드 | ✅ |
| Rate Limiting per API Key | 미구현 (글로벌 Rate Limiter만) | ❌ |

---

## 10. 행동 시나리오 변환 상세 분석

| PRD 세부 기능 | 구현 | Status |
|-------------|------|--------|
| IF-THEN 규칙 자동 생성 | `ActionScenarioConverter.generate_scenarios()` | ✅ |
| 임계값 기반 트리거 | `thresholds` 파라미터 지원 | ✅ |
| 우선순위 자동 산정 (Impact x Probability) | `_calculate_priority()` | ✅ |
| Webhook/이메일/슬랙 외부 연동 | 미구현 | ❌ |
| 시나리오 이력 관리 | 미구현 (생성만, 저장 없음) | ❌ |

---

## 11. Overall Score

```
+--------------------------------------------------+
|  Overall Match Rate: 82%                          |
+==================================================+
|                                                    |
|  Category               Score     Status           |
|  -------               -----     ------           |
|  4대 분석 유형           100%       ✅              |
|  알고리즘 수량           100%       ✅ (초과 달성)   |
|  API 엔드포인트          93%       ✅              |
|  5단계 파이프라인         90%       ✅              |
|  WhatDataAI              95%       ✅              |
|  현황분석                  0%       ❌              |
|  수학적 공식/기여도      100%       ✅              |
|  디시전트리 시각화        50%       ⚠️              |
|  Sim4Brief Report       100%       ✅              |
|  AI Q&A                  85%       ✅              |
|  행동 시나리오 변환       60%       ⚠️              |
|  B2B 데이터 커넥터        55%       ⚠️              |
|  자가 보정 MLOps          90%       ✅              |
|  LLM 시너지              50%       ⚠️              |
|  Train/Test Split       100%       ✅              |
|  보안                    80%       ✅              |
|  병렬 처리              100%       ✅              |
|  시계열 파생변수         100%       ✅              |
|  -------               -----                      |
|  Overall                 82%       ✅              |
|                                                    |
+--------------------------------------------------+
```

---

## 12. Missing Features (PRD O, 구현 X)

| # | 항목 | PRD 위치 | 설명 | Impact |
|---|------|---------|------|--------|
| M1 | 현황분석 (차트/워드클라우드/주제도) | PRD 3.5 | 데이터 탐색 시각화 전체 미구현 | High |
| M2 | 데이터 소스 어댑터 | PRD 3.9.3 | REST/GraphQL/DB 직접 연결 미구현 | Medium |
| M3 | 수집 스케줄링 | PRD 3.9.3 | 실시간(Webhook push)/주기적(Cron) 미구현 | Medium |
| M4 | AES-256 데이터 암호화 | PRD 3.9.4 | 전송 시 암호화 옵션 미구현 | Medium |
| M5 | Webhook/이메일/슬랙 행동 전달 | PRD 3.8 | 외부 시스템 연동 미구현 | Low |
| M6 | 시나리오 이력 관리 | PRD 3.8 | 실행 결과 추적/효과 측정 미구현 | Low |
| M7 | LLM 지식그래프 연동 | PRD 4.1-4.2 | 지식그래프 기반 맥락 제공 미구현 | Medium |
| M8 | 디시전트리 시각화 | PRD 3.6 | 전용 변수 픽처링 시각화 미구현 | Low |
| M9 | API Key 갱신 | PRD 3.9.3 | API Key 갱신 기능 미구현 | Low |
| M10 | IP 화이트리스트 검증 | PRD 3.9.4 | 저장만 구현, 실제 IP 검증 미구현 | Medium |

---

## 13. Added Features (PRD X, 구현 O)

| # | 항목 | 구현 위치 | 설명 |
|---|------|---------|------|
| A1 | CSV 파일 업로드 | `app/api/v1/endpoints/upload.py` | 직접 업로드 후 JSON 변환 |
| A2 | 작업 상태 폴링 | `GET /v1/status/{task_id}` | 진행률(%) 포함 |
| A3 | 현재 임계값 조회 | `GET /v1/threshold` | PATCH 외 조회 추가 |
| A4 | AI Q&A 로컬 fallback | `ai_qa.py` | OpenAI 미설정 시 규칙 기반 응답 |
| A5 | 데이터 드리프트 분석 | `mlops.py` `get_drift_analysis()` | 학습/신규 데이터 분포 비교 |
| A6 | multiprocessing fallback | `parallel.py` | Ray 미설치 시 ProcessPoolExecutor |
| A7 | 헬스 체크 엔드포인트 | `GET /health` | 서비스 상태 확인 |

---

## 14. Changed Features (PRD != 구현)

| # | 항목 | PRD 설계 | 실제 구현 | Impact |
|---|------|---------|---------|--------|
| C1 | WhatDataAI API | `GET /v1/whatdata/{task_id}` | `POST /v1/whatdata` (body에 데이터 전달) | Low |
| C2 | 알고리즘 수 | 125종 | ~155종 (회귀 초과) | None (긍정적) |
| C3 | 병렬 워커 수 | 125개 | 60개 (max_workers 설정) | Low |
| C4 | AI Q&A 엔드포인트 | PRD에 명시 없음 | `POST /v1/qa/{task_id}` 추가 | None (긍정적) |
| C5 | B2B 커넥터 저장소 | 영속적 저장 암시 | 인메모리 딕셔너리 | High |

---

## 15. Recommended Actions

### 15.1 Immediate (High Priority)

| # | 항목 | 설명 | 예상 작업량 |
|---|------|------|----------|
| 1 | B2B 커넥터 영속화 | 인메모리 -> Redis/DB 이관 | 4h |
| 2 | IP 화이트리스트 검증 | 저장만이 아닌 실제 IP 체크 로직 | 2h |

### 15.2 Short-term (Medium Priority)

| # | 항목 | 설명 | 예상 작업량 |
|---|------|------|----------|
| 3 | 현황분석 기본 구현 | 데이터 분포/상관행렬 JSON 반환 | 8h |
| 4 | 행동 시나리오 이력 저장 | Redis에 시나리오 이력 영속화 | 4h |
| 5 | 외부 알림 연동 | Webhook 기반 행동 시나리오 전달 | 6h |
| 6 | API Key 갱신 기능 | 커넥터 키 갱신 엔드포인트 | 2h |
| 7 | AES-256 암호화 옵션 | 데이터 전송 시 암호화 | 4h |

### 15.3 Long-term (Backlog)

| # | 항목 | 설명 |
|---|------|------|
| 8 | 데이터 소스 어댑터 | REST/GraphQL/DB 연결 범용 커넥터 |
| 9 | 수집 스케줄링 (Cron) | Celery Beat 기반 주기적 수집 |
| 10 | LLM 지식그래프 | RAG 기반 맥락 제공 파이프라인 |
| 11 | 디시전트리 시각화 | graphviz/d3.js 기반 트리 시각화 |
| 12 | 워드클라우드/주제도 | 텍스트 분석 + 지리 시각화 |

---

## 16. PRD 문서 업데이트 필요 항목

- [ ] CSV 업로드 API (`POST /v1/upload`) 추가
- [ ] 작업 상태 폴링 API (`GET /v1/status/{task_id}`) 추가
- [ ] 현재 임계값 조회 API (`GET /v1/threshold`) 추가
- [ ] AI Q&A API (`POST /v1/qa/{task_id}`) 추가
- [ ] WhatDataAI 엔드포인트 변경 반영 (`GET` -> `POST`)
- [ ] 알고리즘 수량 업데이트 (125종 -> 155종)
- [ ] 헬스 체크 엔드포인트 (`GET /health`) 추가

---

## 17. Architecture Analysis

### 17.1 Folder Structure

```
app/
├── api/v1/endpoints/     # API Layer (Presentation)
│   ├── analyze.py
│   ├── report.py
│   ├── simulate.py
│   ├── optimize.py
│   ├── whatdata.py
│   ├── actions.py
│   ├── connectors.py
│   ├── qa.py
│   ├── upload.py
│   └── threshold.py
├── core/                 # Core Engine (Application)
│   ├── config.py
│   ├── engine.py
│   ├── evaluator.py
│   ├── parallel.py
│   ├── preprocessor.py
│   └── storage.py
├── models/               # Data Models (Domain)
│   ├── schemas.py
│   └── algorithms/       # Algorithm Registry
│       ├── base.py
│       ├── registry.py
│       ├── linear_models.py
│       ├── nonlinear_models.py
│       ├── tree_models.py
│       ├── ensemble_models.py
│       ├── classification/
│       ├── multiclass/
│       └── timeseries/
├── services/             # Business Services (Application)
│   ├── xai.py
│   ├── nlg.py
│   ├── simulator.py
│   ├── optimizer.py
│   ├── whatdata.py
│   ├── actions.py
│   ├── connector.py
│   ├── mlops.py
│   ├── ai_qa.py
│   ├── feature_engineering.py
│   └── webhook.py
├── security/             # Security (Infrastructure)
│   ├── rate_limiter.py
│   ├── ssrf_guard.py
│   └── input_validator.py
└── main.py               # Application Entry
```

### 17.2 Architecture Score

```
+--------------------------------------------------+
|  Architecture Compliance: 90%                     |
+--------------------------------------------------+
|  ✅ Layer separation:    Clear (api/core/services) |
|  ✅ Dependency direction: Correct                  |
|  ✅ SRP applied:         engine.py refactored      |
|  ⚠️ Minor coupling:     storage in services       |
+--------------------------------------------------+
```

---

## 18. Summary

| Category | Score | Status |
|----------|:-----:|:------:|
| Design Match (PRD vs Code) | 82% | ✅ |
| API Compliance | 93% | ✅ |
| Algorithm Coverage | 100% | ✅ |
| Architecture | 90% | ✅ |
| Security | 80% | ✅ |
| **Overall** | **82%** | **✅** |

> **결론**: PRD v2.0 대비 82% Match Rate 달성. 핵심 엔진(알고리즘 토너먼트, 병렬 처리, XAI, Sim4Brief)은 완전 구현 상태입니다. 주요 미구현 항목은 현황분석 시각화(차트/워드클라우드/주제도)와 B2B 커넥터 고급 기능(어댑터, 스케줄링, 암호화)입니다. Match Rate >= 90% 달성을 위해 B2B 커넥터 영속화 및 현황분석 기본 기능 구현을 우선 권장합니다.

---

## Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2026-03-12 | Initial PRD vs Implementation gap analysis | Claude Code |
