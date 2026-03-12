---
name: OmniMetric (XAISimTier) Project Status
description: PRD v2.0 기반 AI 의사결정 시뮬레이션 엔진 프로젝트 현황 - 125종 알고리즘, 4대 분석유형
type: project
---

OmniMetric(XAISimTier)은 125종+ AI 알고리즘 병렬 토너먼트 기반 의사결정 엔진이다.

**Why:** CEO 강승식 대표님이 ICT폴리텍대학 한일 교수의 업무데이터 AI 시뮬레이션 방법론을 SaaS 제품화하려는 프로젝트.

**How to apply:**
- 현재 구현률 ~40% (회귀분석 60종만 완료)
- CRITICAL: Train/Test Split 미적용 -> 과적합 위험
- 미구현: 분류(17종), 다중분류(17종), 시계열(61종), What-if 시뮬레이션, 최적화
- 보안 이슈: db_password 하드코딩, CORS *, Rate Limiting 없음
- 기술스택: Python 3.11, FastAPI, Ray/multiprocessing, Redis, scikit-learn, SHAP/LIME
- PDCA Plan 완료(2026-03-12), Design 단계 진행 예정
