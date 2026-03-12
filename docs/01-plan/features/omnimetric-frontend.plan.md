# OmniMetric Frontend 계획서

> **Summary**: OmniMetric(갑) 관리자 + 고객사(을) 분석 결과 확인을 위한 프론트엔드 대시보드
>
> **Project**: OmniMetric (XAISimTier) Frontend
> **Version**: 1.0
> **Author**: Claude Code
> **Date**: 2026-03-12
> **Status**: Approved

---

## 1. Overview

### 1.1 Purpose

OmniMetric 백엔드 API(22개)를 활용하는 프론트엔드 대시보드를 구현합니다.
- **갑(OmniMetric) 관리자**: 고객사 등록, API Key 발행, 연동 상태 모니터링
- **을(고객사) 사용자**: 분석 결과 확인, What-if 시뮬레이션, 행동 시나리오 활용

### 1.2 핵심 질문에 대한 답

> "을 프로젝트에서 읽어온 데이터를 **어떤 근거**로 분석했는지?"

프론트엔드에서 다음을 시각적으로 보여줘야 합니다:
1. **분석 근거**: 155종 알고리즘 중 왜 이것이 승자인지 (R², Adj.R², P-value 비교표)
2. **수학적 공식**: Y = w₁X₁ + w₂X₂ + ... + b (계수 시각화)
3. **변수 기여도**: 각 변수가 결과에 미치는 영향 (% + 방향)
4. **XAI 해석**: SHAP/LIME 기반 변수 중요도 차트
5. **데이터 현황**: 을에서 가져온 데이터의 분포/상관관계/이상치

### 1.3 기술 스택

- **Framework**: Next.js 15 (App Router)
- **Styling**: TailwindCSS + SLDS 스타일
- **Charts**: Recharts (상관행렬, 분포, 기여도)
- **State**: React Server Components + fetch
- **Port**: 3032
- **Backend**: FastAPI localhost:8000 (기존)

---

## 2. 화면 구성 (8개 페이지)

### 2.1 대시보드 (홈) — `/`

| 섹션 | 내용 | API |
|------|------|-----|
| 시스템 상태 | API 서버 상태, 연동 고객사 수 | `GET /health`, `GET /v1/connectors` |
| 최근 분석 | 최근 완료된 분석 작업 목록 | `GET /v1/status/{task_id}` |
| 빠른 실행 | 데이터 업로드 / 분석 시작 버튼 | - |

### 2.2 B2B 커넥터 관리 — `/connectors`

| 섹션 | 내용 | API |
|------|------|-----|
| 커넥터 목록 | 고객사별 연동 상태 카드 | `GET /v1/connectors` |
| API Key 발행 | 고객사 등록 + 키 발행 폼 | `POST /v1/connectors` |
| 상세 조회 | 연동 상세 (감사 로그, 동기화 이력) | `GET /v1/connectors/{id}` |
| 키 갱신/폐기 | API Key 갱신, 연동 해제 | `POST /{id}/renew`, `DELETE /{id}` |
| 키 검증 | API Key 유효성 테스트 | `POST /{id}/verify` |
| 스키마 탐색 | 을의 데이터 구조 확인 | `GET /{id}/schema` |
| 데이터 수집 | 수동 동기화 트리거 | `POST /{id}/sync` |

### 2.3 데이터 업로드 & 현황분석 — `/data`

| 섹션 | 내용 | API |
|------|------|-----|
| CSV 업로드 | 파일 업로드 + 미리보기 테이블 | `POST /v1/upload` |
| WhatDataAI | 데이터 특성 분석 + 추천 분석유형 | `POST /v1/whatdata` |
| 현황분석 (EDA) | 분포 히스토그램, 상관행렬 히트맵, 이상치 차트 | `POST /v1/eda` |

### 2.4 분석 실행 — `/analyze`

| 섹션 | 내용 | API |
|------|------|-----|
| 분석 설정 | 타겟(Y) 선택, 분석유형 선택, XAI 옵션 | - |
| 실행 | 분석 시작 + 진행률 폴링 | `POST /v1/analyze`, `GET /v1/status/{id}` |

### 2.5 분석 결과 & 근거 — `/report/{task_id}` ★핵심

| 섹션 | 내용 | API |
|------|------|-----|
| **승자 알고리즘** | 알고리즘명, R², Adj.R², P-value 카드 | `GET /v1/report/{id}` |
| **수학적 공식** | Y = w₁X₁ + ... + b 수식 표시 | report.winner.formula |
| **변수 기여도 차트** | 변수별 영향도(%) 바 차트 + 방향(+/-) | report.winner.feature_importance |
| **알고리즘 토너먼트** | 전체 알고리즘 R² 랭킹 테이블 | report.all_results |
| **XAI 해석** | SHAP 변수 중요도 (가용 시) | report.xai_insights |
| **Sim4Brief 리포트** | 자연어 요약 (한국어) | report.nlg_report |
| **분석 근거 요약** | "왜 이 알고리즘이 선택됐는지" 설명 카드 | 조합 |

### 2.6 What-if 시뮬레이션 — `/simulate/{task_id}`

| 섹션 | 내용 | API |
|------|------|-----|
| 변수 조절 슬라이더 | X 변수 값 조절 (±% 또는 절대값) | - |
| 예측 결과 | 조절된 변수에 따른 Y 예측값 | `POST /v1/simulate` |
| 시나리오 비교 | 복수 시나리오 비교 테이블 | 복수 호출 |

### 2.7 행동 시나리오 — `/actions/{task_id}`

| 섹션 | 내용 | API |
|------|------|-----|
| IF-THEN 카드 | 행동 규칙 카드 (우선순위순) | `POST /v1/actions/{id}` |
| 이력 조회 | 시나리오 생성 이력 | `GET /v1/actions/{id}/history` |
| Webhook 전달 | 외부 시스템 전달 설정 | webhook_url 파라미터 |

### 2.8 AI Q&A — `/qa/{task_id}`

| 섹션 | 내용 | API |
|------|------|-----|
| 채팅 UI | 분석 결과 기반 자유 질문 | `POST /v1/qa/{id}` |
| 추천 질문 | "매출에 가장 큰 영향?" 등 | 프리셋 |

---

## 3. Scope

### 3.1 In Scope

- [x] Next.js 15 App Router 프로젝트 초기화 (포트 3032)
- [ ] 대시보드 (홈)
- [ ] B2B 커넥터 관리 (API Key 발행/갱신/폐기)
- [ ] 데이터 업로드 + WhatDataAI + EDA
- [ ] 분석 실행 + 진행률 폴링
- [ ] **분석 결과 & 근거** (핵심 페이지)
- [ ] What-if 시뮬레이션 대화형 UI
- [ ] 행동 시나리오 카드 UI
- [ ] AI Q&A 채팅 UI

### 3.2 Out of Scope

- 사용자 인증/로그인 (1차에서는 API Key 기반만)
- 모바일 반응형 (데스크톱 우선)
- 워드클라우드/주제도 (2차)
- 다국어 지원

---

## 4. Requirements

### 4.1 Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-01 | B2B 커넥터 관리 (API Key 발행/갱신/폐기/검증) | P0 |
| FR-02 | 분석 결과 & 근거 시각화 (R², 공식, 기여도, XAI) | P0 |
| FR-03 | 데이터 업로드 + EDA 시각화 | P0 |
| FR-04 | What-if 시뮬레이션 대화형 UI | P1 |
| FR-05 | 행동 시나리오 카드 UI | P1 |
| FR-06 | 분석 실행 + 진행률 | P0 |
| FR-07 | AI Q&A 채팅 | P2 |
| FR-08 | 대시보드 (홈) | P1 |

### 4.2 Non-Functional Requirements

| Category | Criteria |
|----------|----------|
| Performance | 차트 렌더링 1초 이내 |
| Usability | 비전문가도 15분 내 첫 분석 완료 가능 |
| Design | SLDS 스타일, Feather Icons |

---

## 5. Implementation Phases

### Phase 1: 프로젝트 초기화 + 레이아웃

- Next.js 15 프로젝트 생성 (포트 3032)
- TailwindCSS + SLDS 스타일 기본 레이아웃
- API 클라이언트 유틸 (fetch wrapper)
- 3-Column Layout: 좌측 Nav, 중앙 Main, 우측 Context

### Phase 2: B2B 커넥터 관리 (FR-01)

- 커넥터 목록 카드
- API Key 발행 폼
- 키 검증/갱신/폐기
- 스키마 탐색 결과 테이블

### Phase 3: 데이터 & 분석 (FR-03, FR-06)

- CSV 업로드 + 데이터 미리보기
- WhatDataAI 추천 UI
- EDA 차트 (분포, 상관행렬, 이상치)
- 분석 실행 + 진행률 폴링 UI

### Phase 4: 분석 결과 & 근거 (FR-02) ★핵심

- 승자 알고리즘 카드
- 수학적 공식 표시
- 변수 기여도 바 차트
- 알고리즘 토너먼트 랭킹 테이블
- XAI 변수 중요도 차트
- Sim4Brief 자연어 리포트

### Phase 5: 시뮬레이션 & 시나리오 (FR-04, FR-05)

- What-if 슬라이더 UI
- 시나리오 비교 테이블
- 행동 시나리오 카드 (IF-THEN)
- 시나리오 이력

### Phase 6: AI Q&A + 대시보드 (FR-07, FR-08)

- 채팅 UI
- 대시보드 요약 카드

---

## 6. Success Criteria

- [ ] 8개 페이지 모두 구현
- [ ] 22개 백엔드 API와 정상 연동
- [ ] 분석 근거(R², 공식, 기여도)가 시각적으로 명확하게 표시
- [ ] 포트 3032에서 정상 실행
- [ ] SLDS 스타일 가이드 준수

---

## Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2026-03-12 | Initial frontend plan | Claude Code |
