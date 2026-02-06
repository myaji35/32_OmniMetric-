
# [0032] OmniMetric

## Identity
- **ID**: 0032
- **Category**: SaaS
- **Governance**: [9999] Master Root
- **Status**: Sentinel-Standardized

---
# OmniMetric

**전방위 통계 분석 및 의사결정 엔진**

60여 가지 통계 알고리즘을 병렬로 가동하여 최적의 결정계수($R^2$)를 도출하고, 그 근거를 수학적 공식과 자연어 리포트로 제공하는 고성능 백엔드 분석 엔진입니다.

## 🎯 핵심 기능

### 1️⃣ 60+ 알고리즘 토너먼트
- 선형/비선형 회귀, 트리 기반 모델, 정보 이론 등 60개 이상의 알고리즘 동시 실행
- $R^2$, Adj. $R^2$, P-value 기반 최적 모델 자동 선정

### 2️⃣ 초고속 병렬 처리
- Ray 기반 분산 컴퓨팅으로 1만 행 데이터 1분 이내 분석
- 비동기 API 응답으로 대규모 데이터셋 처리 효율화

### 3️⃣ 설명 가능한 AI (XAI)
- SHAP, LIME을 활용한 모델 해석
- 수학적 공식 변환 및 변수별 기여도 수치화

### 4️⃣ 자연어 리포트 생성
- "A 변수가 10% 증가 → B는 5% 상승" 형태의 직관적 설명
- 알고리즘 선정 사유 자동 문서화

### 5️⃣ 자가 보정 MLOps
- 실시간 오차 감지 및 자동 재학습
- 설정 가능한 임계값 기반 모델 업데이트

---

## 🚀 빠른 시작

### 사전 요구사항
- Python 3.11+
- Docker & Docker Compose (선택사항)
- Redis (로컬 또는 Docker)

### 설치 방법

#### 1. 저장소 클론
```bash
git clone https://github.com/gagahoho/omnimetric.git
cd omnimetric
```

#### 2. 의존성 설치
```bash
# Poetry 사용 시
poetry install

# 또는 pip 사용 시
pip install -r requirements.txt
```

#### 3. 환경 변수 설정
```bash
cp .env.example .env
# .env 파일을 편집하여 필요한 설정 변경
```

#### 4. 서버 실행

**로컬 실행**
```bash
python -m app.main
# 또는
uvicorn app.main:app --reload
```

**Docker Compose 실행**
```bash
docker-compose up -d
```

서버가 시작되면 다음 URL로 접근 가능:
- API 문서: http://localhost:8000/docs
- 헬스 체크: http://localhost:8000/health

---

## 📡 API 사용 예시

### 1. 데이터 분석 시작
```bash
curl -X POST "http://localhost:8000/v1/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "data": [
      {"age": 25, "income": 50000, "education": 16, "target": 1},
      {"age": 30, "income": 60000, "education": 18, "target": 1}
    ],
    "target_column": "target",
    "task_type": "regression",
    "enable_xai": true
  }'
```

**응답**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "message": "분석 작업이 시작되었습니다.",
  "created_at": "2026-02-01T10:30:00"
}
```

### 2. 분석 결과 조회
```bash
curl "http://localhost:8000/v1/report/{task_id}"
```

### 3. 재학습 임계값 설정
```bash
curl -X PATCH "http://localhost:8000/v1/threshold" \
  -H "Content-Type: application/json" \
  -d '{
    "error_threshold": 0.10,
    "min_r2_score": 0.90
  }'
```

---

## 🏗️ 아키텍처

```
omnimetric/
├── app/
│   ├── api/v1/              # API 엔드포인트
│   ├── core/                # 핵심 엔진 (토너먼트, 병렬 처리)
│   ├── models/              # 알고리즘 구현체 & 스키마
│   ├── services/            # XAI, NLG, MLOps
│   └── main.py              # FastAPI 엔트리포인트
├── tests/                   # 테스트 코드
├── prd.md                   # 제품 요구사항 정의서
└── docker-compose.yml       # 컨테이너 오케스트레이션
```

---

## 🧪 개발 환경

### 테스트 실행
```bash
pytest tests/ -v
```

### 코드 포맷팅
```bash
black app/
ruff check app/
```

### 타입 체크
```bash
mypy app/
```

---

## 📊 성능 목표

- **분석 속도**: 1만 행 데이터, 60개 알고리즘 전체 검토 1분 이내
- **정확도**: $R^2$ 0.85 이상
- **사용성**: 비전문가도 리포트만으로 의사결정 가능

---

## 🛠️ 기술 스택

| 구분 | 기술 |
|------|------|
| Backend | Python 3.11, FastAPI |
| Parallelism | Ray, Celery + Redis |
| ML/통계 | PyCaret, Scikit-learn, Statsmodels, XGBoost, LightGBM, CatBoost |
| XAI | SHAP, LIME |
| 컨테이너 | Docker, Docker Compose |

---

## 📄 라이선스

Copyright © 2026 주식회사 가가호호. All rights reserved.

---

## 📞 문의

- **개발사**: 주식회사 가가호호
- **대표**: 강승식
- **이메일**: ceo@gagahoho.com
