# OmniMetric(XAISimTier) 연동 가이드 - 을(고객사) 프로젝트용 프롬프트

> 이 문서는 OmniMetric(갑)과 연동하려는 고객사(을) 프로젝트의 AI 코딩 도구에 입력하는 프롬프트입니다.
> 을 프로젝트의 기술 스택에 관계없이 사용할 수 있습니다.

---

## 프롬프트 (복사하여 을 프로젝트의 AI 도구에 입력)

```
# OmniMetric(XAISimTier) B2B 연동 구현 요청

## 배경
우리 프로젝트는 OmniMetric(XAISimTier) AI 분석 플랫폼과 B2B 연동합니다.
OmniMetric은 '갑'(분석 제공자), 우리 프로젝트는 '을'(데이터 제공자)입니다.
갑이 발행한 API Key를 우리 시스템에 등록하고, 갑이 우리 데이터를 읽어서
AI 기반 분석 결과(최적 알고리즘, What-if 시뮬레이션, 행동 시나리오)를 제공합니다.

## 연동 흐름

```
1. 갑(OmniMetric)이 우리에게 API Key 발행
2. 우리가 API Key를 시스템에 등록
3. 우리 서버가 갑에게 콜백 호출하여 키 유효성 검증
4. 검증 완료 후 우리가 데이터 엔드포인트를 갑에게 오픈
5. 갑이 우리 데이터를 수집하여 AI 분석 실행
6. 우리가 갑의 API를 통해 분석 결과 확인
```

## 구현해야 할 기능 (총 6가지)

### 1. API Key 등록 및 저장
- 갑에게 받은 API Key를 안전하게 저장하는 기능
- 환경변수 또는 암호화된 DB에 저장 (평문 저장 금지)
- 설정 화면에서 API Key 등록/수정/삭제 UI 제공

### 2. API Key 유효성 검증 (콜백)
- 갑의 검증 엔드포인트를 호출하여 API Key 유효성 확인
- 요청: POST {OMNIMETRIC_BASE_URL}/v1/connectors/{connector_id}/verify
- 요청 헤더: Authorization: Bearer {API_KEY}
- 응답 예시:
  ```json
  {
    "valid": true,
    "connector_id": "conn_abc123",
    "scope": ["read:data", "read:schema"],
    "expires_at": "2027-03-12T00:00:00Z"
  }
  ```
- 검증 실패 시 사용자에게 알림 및 재등록 유도
- 주기적 검증 (매일 1회 권장)

### 3. 데이터 엔드포인트 오픈 (갑이 호출하는 API)
갑(OmniMetric)이 우리 데이터를 수집하기 위해 호출하는 API를 구현합니다.

#### 3-1. 스키마 조회 API
갑이 우리 데이터 구조를 탐색하기 위해 호출합니다.
```
GET /api/omnimetric/schema
Authorization: Bearer {API_KEY}

응답 예시:
{
  "tables": [
    {
      "name": "sales",
      "description": "매출 데이터",
      "columns": [
        {"name": "date", "type": "datetime", "description": "판매일자"},
        {"name": "amount", "type": "float", "description": "매출액"},
        {"name": "product_id", "type": "integer", "description": "상품ID"},
        {"name": "region", "type": "string", "description": "지역"},
        {"name": "ad_cost", "type": "float", "description": "광고비"}
      ],
      "row_count": 15000,
      "date_range": {"from": "2024-01-01", "to": "2026-03-12"}
    }
  ]
}
```

#### 3-2. 데이터 조회 API
갑이 실제 분석용 데이터를 가져갑니다.
```
GET /api/omnimetric/data/{table_name}
Authorization: Bearer {API_KEY}
Query Params:
  - columns: 조회할 컬럼 (콤마 구분, 선택)
  - limit: 최대 행 수 (기본 10000)
  - offset: 시작 위치 (페이지네이션)
  - date_from: 시작일 (선택)
  - date_to: 종료일 (선택)

응답 예시:
{
  "table": "sales",
  "columns": ["date", "amount", "product_id", "region", "ad_cost"],
  "data": [
    {"date": "2026-01-01", "amount": 150000, "product_id": 1, "region": "서울", "ad_cost": 50000},
    {"date": "2026-01-02", "amount": 180000, "product_id": 2, "region": "부산", "ad_cost": 30000}
  ],
  "total_rows": 15000,
  "returned_rows": 2
}
```

#### 3-3. 데이터 변경 알림 (Webhook Push, 선택사항)
우리 데이터가 변경될 때 갑에게 알림을 보냅니다.
```
POST {OMNIMETRIC_BASE_URL}/v1/connectors/{connector_id}/sync
Authorization: Bearer {API_KEY}
Body:
{
  "event": "data_updated",
  "table": "sales",
  "changed_rows": 150,
  "timestamp": "2026-03-12T10:30:00Z"
}
```

### 4. 인증 미들웨어 (갑의 요청 검증)
- 갑이 우리 API를 호출할 때 API Key를 검증하는 미들웨어
- Authorization 헤더에서 Bearer 토큰 추출
- 저장된 API Key와 비교하여 인증
- 인증 실패 시 401 Unauthorized 반환
- IP 화이트리스트 적용 (OmniMetric 서버 IP만 허용, 선택사항)

```
미들웨어 로직:
1. Authorization 헤더 확인
2. Bearer 토큰 추출
3. 저장된 API Key와 비교
4. scope 확인 (read:data, read:schema)
5. Rate Limiting 적용 (분당 60회 권장)
6. 감사 로그 기록 (누가, 언제, 어떤 데이터)
```

### 5. 분석 결과 조회 (갑의 API 호출)
갑이 분석을 완료한 후 결과를 가져오는 기능입니다.

#### 5-1. 분석 요청
```
POST {OMNIMETRIC_BASE_URL}/v1/analyze
Authorization: Bearer {API_KEY}
Body:
{
  "connector_id": "conn_abc123",
  "table": "sales",
  "target_column": "amount",
  "task_type": "regression",
  "enable_xai": true
}

응답: {"task_id": "task_xyz789", "status": "pending"}
```

#### 5-2. 분석 결과 조회
```
GET {OMNIMETRIC_BASE_URL}/v1/report/{task_id}
Authorization: Bearer {API_KEY}

응답 예시:
{
  "status": "completed",
  "winner": {
    "algorithm": "XGBoost",
    "r2_score": 0.91,
    "formula": "amount = 2.3*ad_cost + 1500*is_weekend - 300*rain + 85000"
  },
  "xai_insights": {
    "top_features": [
      {"name": "ad_cost", "impact": "+38%", "direction": "positive"},
      {"name": "is_weekend", "impact": "+27%", "direction": "positive"}
    ]
  },
  "report": {
    "summary": "광고비가 매출에 가장 큰 영향(+38%)을 미칩니다.",
    "recommendations": [
      "광고비를 10% 올리면 매출 약 15% 증가가 예상됩니다.",
      "주말 프로모션이 평일 대비 27% 더 효과적입니다."
    ]
  },
  "action_scenarios": [
    {
      "rule": "IF 주말 AND 비예보 THEN 배달 인력 15% 추가 확보",
      "priority": "HIGH",
      "expected_impact": "+12% 매출"
    }
  ]
}
```

#### 5-3. What-if 시뮬레이션 요청
```
POST {OMNIMETRIC_BASE_URL}/v1/simulate
Authorization: Bearer {API_KEY}
Body:
{
  "task_id": "task_xyz789",
  "scenarios": [
    {"ad_cost": {"change": "+10%"}},
    {"ad_cost": {"change": "+20%"}, "price": {"change": "-5%"}}
  ]
}
```

### 6. 연동 상태 대시보드 (선택사항)
- 갑과의 연동 상태를 시각적으로 확인하는 관리 화면
- 표시 항목:
  - API Key 유효성 상태 (유효/만료/오류)
  - 마지막 데이터 수집 시각
  - 수집된 데이터 건수
  - 최근 분석 결과 요약
  - 행동 시나리오 목록

## 보안 요구사항
- [ ] API Key는 환경변수 또는 암호화된 DB에 저장 (평문 금지)
- [ ] 갑-을 통신은 TLS 1.3 이상 필수
- [ ] 데이터 엔드포인트는 인증된 요청만 허용
- [ ] 감사 로그: 모든 데이터 접근 이력 기록
- [ ] Rate Limiting: 분당 60회 이하
- [ ] 민감 데이터 컬럼은 제외 옵션 제공 (exclude_columns 파라미터)

## 환경 변수
```
OMNIMETRIC_BASE_URL=https://api.omnimetric.ai
OMNIMETRIC_API_KEY=omk_발행받은_키_여기에_입력
OMNIMETRIC_CONNECTOR_ID=conn_abc123
OMNIMETRIC_ALLOWED_TABLES=sales,products,customers
OMNIMETRIC_EXCLUDE_COLUMNS=password,ssn,credit_card
```

## 테스트 체크리스트
- [ ] API Key 등록 및 저장 정상 동작
- [ ] 갑에게 콜백하여 키 유효성 검증 성공
- [ ] 갑이 스키마 조회 API 호출 시 정상 응답
- [ ] 갑이 데이터 조회 API 호출 시 정상 응답 (페이지네이션 포함)
- [ ] 인증 미들웨어가 잘못된 키를 거부
- [ ] 분석 요청 및 결과 조회 정상 동작
- [ ] 민감 데이터 컬럼이 제외되는지 확인
- [ ] Rate Limiting 동작 확인

위 요구사항을 우리 프로젝트 기술 스택에 맞게 구현해주세요.
```

---

## 사용법

1. 위 프롬프트 전체를 복사합니다
2. 을(고객사) 프로젝트의 AI 코딩 도구 (Claude Code, Cursor, Copilot 등)에 붙여넣기합니다
3. 을 프로젝트의 기술 스택(Rails, Django, Express 등)에 맞게 자동으로 구현됩니다

## 갑(OmniMetric) 관리자 할 일
1. `/v1/connectors` API로 고객사 등록 및 API Key 발행
2. 을에게 API Key + 이 프롬프트 문서 전달
3. 을이 연동 완료 후 `/v1/connectors/{id}/verify`로 상호 검증
4. `/v1/connectors/{id}/sync`로 데이터 수집 시작
