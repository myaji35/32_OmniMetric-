# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 프로젝트 개요

OmniMetric은 60여 가지 통계 알고리즘을 병렬로 실행하여 최적의 결정계수($R^2$)를 도출하고, 수학적 공식과 자연어 리포트를 제공하는 고성능 백엔드 분석 엔진입니다.

## 핵심 아키텍처

### 1. 알고리즘 토너먼트 시스템
- 60개 이상의 통계/ML 알고리즘을 동시에 실행하여 최적 모델 선정
- $R^2$, Adj. $R^2$, P-value 기반 승자 결정
- 선형/비선형 회귀, 트리 기반 모델, 정보 이론 등 포괄

### 2. 병렬 처리 엔진
- Ray 또는 Celery (Redis 기반)를 사용한 워커 분산
- 각 알고리즘을 독립 워커에 할당하여 동시 실행
- 비동기 API 응답: 작업 ID 즉시 반환 후 Webhook/폴링으로 결과 전달

### 3. 데이터 플로우
```
입력 (CSV/JSON) → 분산 (60개 워커) → 경쟁 ($R^2$ 계산)
→ 선정 (최적 모델) → 출력 (공식 + 리포트) → 감시 (자가 보정)
```

### 4. XAI (설명 가능한 AI) 레이어
- SHAP, LIME을 사용한 모델 해석
- 수학적 공식 변환: $Y = w_1X_1 + w_2X_2 + ... + b$
- 변수별 가중치 및 방향성(+/-) 수치화
- 자연어 리포트 자동 생성

### 5. 자가 보정 MLOps
- 실시간 오차 감지 (설정 가능한 임계값)
- 오차 발생 시 자동 재학습 트리거
- 60개 알고리즘 토너먼트 재개최

## 기술 스택

- **Backend**: Python 3.11 + FastAPI
- **Parallelism**: Ray 또는 Celery + Redis
- **Analysis**: PyCaret, Scikit-learn, Statsmodels
- **XAI**: SHAP, LIME
- **API**: RESTful (JSON)

## API 엔드포인트

- `POST /v1/analyze` - 데이터 분석 및 알고리즘 토너먼트 시작
- `GET /v1/report/{task_id}` - 자연어 리포트 및 통계 결과 조회
- `PATCH /v1/threshold` - 오차 감지 임계값 설정

## 성능 목표

- **분석 속도**: 1만 행 데이터, 60개 알고리즘 전체 검토 1분 이내
- **정확도**: $R^2$ 0.85 이상
- **사용성**: 비전문가도 리포트만으로 의사결정 가능

## 외부 시스템 연동

- 누리팜, 인슈어그래프 등 외부 시스템과 API 연동
- CSV/JSON 형식 데이터 입력 지원
