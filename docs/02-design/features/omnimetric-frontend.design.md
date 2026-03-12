# OmniMetric Frontend 설계서

> **Summary**: OmniMetric 프론트엔드 대시보드 상세 설계 (컴포넌트, API 연동, 데이터 흐름)
>
> **Project**: OmniMetric Frontend
> **Version**: 1.0
> **Date**: 2026-03-12
> **Status**: In Progress
> **Plan Reference**: `docs/01-plan/features/omnimetric-frontend.plan.md`

---

## 1. 기술 아키텍처

### 1.1 시스템 구성도

```
┌─────────────────────────────────────────────────────┐
│  Next.js 15 App Router (Port 3032)                  │
│  ┌──────────────────────────────────────────────┐   │
│  │  Layout (3-Column SLDS)                       │   │
│  │  ┌────────┬──────────────┬───────────────┐   │   │
│  │  │ NavBar │  Main Content │ Context Panel │   │   │
│  │  │ 240px  │  flex-1      │ 320px (opt)   │   │   │
│  │  └────────┴──────────────┴───────────────┘   │   │
│  └──────────────────────────────────────────────┘   │
│                        ↕ fetch                       │
│  ┌──────────────────────────────────────────────┐   │
│  │  API Client Layer (lib/api.ts)                │   │
│  │  - Base URL: http://localhost:8000            │   │
│  │  - Header: X-API-Key                          │   │
│  │  - Error handling + retry                     │   │
│  └──────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
                        ↕ HTTP/JSON
┌─────────────────────────────────────────────────────┐
│  FastAPI Backend (Port 8000)                         │
│  22 API Endpoints (v1)                               │
└─────────────────────────────────────────────────────┘
```

### 1.2 기술 스택 상세

| 구분 | 기술 | 버전 | 용도 |
|------|------|------|------|
| Framework | Next.js | 15.x | App Router, RSC |
| Runtime | Node.js | 20+ | 서버 런타임 |
| Styling | TailwindCSS | 4.x | SLDS 스타일 구현 |
| Charts | Recharts | 2.x | 바 차트, 히트맵, 분포 |
| Icons | Feather Icons | react-feather | SVG 라인 아이콘 |
| HTTP | fetch (native) | - | API 클라이언트 |
| Form | React Hook Form | 7.x | 폼 검증 |

### 1.3 프로젝트 구조

```
frontend/
├── app/
│   ├── layout.tsx              # 3-Column SLDS 레이아웃
│   ├── page.tsx                # 대시보드 (홈)
│   ├── globals.css             # TailwindCSS + SLDS 토큰
│   ├── connectors/
│   │   ├── page.tsx            # 커넥터 목록
│   │   └── [id]/
│   │       └── page.tsx        # 커넥터 상세
│   ├── data/
│   │   └── page.tsx            # 업로드 + WhatData + EDA
│   ├── analyze/
│   │   └── page.tsx            # 분석 실행
│   ├── report/
│   │   └── [taskId]/
│   │       └── page.tsx        # 분석 결과 & 근거 ★핵심
│   ├── simulate/
│   │   └── [taskId]/
│   │       └── page.tsx        # What-if 시뮬레이션
│   ├── actions/
│   │   └── [taskId]/
│   │       └── page.tsx        # 행동 시나리오
│   └── qa/
│       └── [taskId]/
│           └── page.tsx        # AI Q&A 채팅
├── components/
│   ├── layout/
│   │   ├── Sidebar.tsx         # 좌측 네비게이션
│   │   ├── Header.tsx          # 상단 헤더 (Compact)
│   │   └── ContextPanel.tsx    # 우측 컨텍스트 패널
│   ├── ui/
│   │   ├── Card.tsx            # SLDS 카드
│   │   ├── Badge.tsx           # Solid 배지
│   │   ├── Button.tsx          # 액션 버튼
│   │   ├── Input.tsx           # 폼 입력 (border-gray-300)
│   │   ├── Select.tsx          # 셀렉트 (bg-white)
│   │   ├── Table.tsx           # 데이터 테이블
│   │   ├── Modal.tsx           # 모달 다이얼로그
│   │   ├── Spinner.tsx         # 로딩 스피너
│   │   └── StatusBadge.tsx     # 상태 배지 (solid)
│   ├── charts/
│   │   ├── BarChart.tsx        # 변수 기여도 바 차트
│   │   ├── HeatmapChart.tsx    # 상관행렬 히트맵
│   │   ├── DistributionChart.tsx # 분포 히스토그램
│   │   ├── RankingTable.tsx    # 알고리즘 랭킹 테이블
│   │   └── ShapChart.tsx       # SHAP 변수 중요도
│   ├── connectors/
│   │   ├── ConnectorCard.tsx   # 커넥터 카드
│   │   ├── CreateForm.tsx      # 커넥터 생성 폼
│   │   └── SchemaViewer.tsx    # 스키마 뷰어
│   ├── report/
│   │   ├── WinnerCard.tsx      # 승자 알고리즘 카드
│   │   ├── FormulaDisplay.tsx  # 수학적 공식 표시
│   │   ├── FeatureImportance.tsx # 변수 기여도
│   │   ├── TournamentRanking.tsx # 토너먼트 랭킹
│   │   ├── XAIInsights.tsx     # XAI 해석
│   │   └── NLGReport.tsx       # 자연어 리포트
│   └── simulate/
│       ├── VariableSlider.tsx  # 변수 조절 슬라이더
│       └── ScenarioCompare.tsx # 시나리오 비교
├── lib/
│   ├── api.ts                  # API 클라이언트 (fetch wrapper)
│   ├── types.ts                # TypeScript 타입 정의
│   └── utils.ts                # 유틸리티 함수
├── next.config.ts
├── tailwind.config.ts
├── tsconfig.json
└── package.json
```

---

## 2. 디자인 시스템 (SLDS 스타일)

### 2.1 Color Tokens

```css
/* SLDS Design Tokens */
--color-brand-primary: #00A1E0;      /* Salesforce Blue */
--color-brand-hover: #0088C7;        /* Hover state */
--color-bg-default: #F3F2F2;         /* 페이지 배경 */
--color-bg-card: #FFFFFF;            /* 카드 배경 */
--color-text-default: #16325C;       /* 기본 텍스트 (Navy) */
--color-text-secondary: #54698D;     /* 보조 텍스트 */
--color-border: #D8DDE6;             /* 카드 테두리 (gray-300급) */
--color-success: #04844B;            /* 성공/활성 */
--color-warning: #FFB75D;            /* 경고 */
--color-error: #C23934;              /* 오류/비활성 */
```

### 2.2 레이아웃 규칙

```
┌──────────────────────────────────────────────────────────────┐
│ Header (h-14, bg-[#16325C], text-white)                      │
├────────┬─────────────────────────────────┬───────────────────┤
│ NavBar │           Main Content          │  Context Panel    │
│ w-60   │           flex-1                │  w-80 (optional)  │
│ bg-wht │           bg-[#F3F2F2]          │  bg-white         │
│ border │           p-6                   │  border-l         │
│  -r    │                                 │  p-4              │
└────────┴─────────────────────────────────┴───────────────────┘
```

### 2.3 컴포넌트 스타일 규칙

| 컴포넌트 | 스타일 |
|----------|--------|
| Card | `bg-white border border-gray-200 rounded-lg shadow-sm` |
| Card Header | `px-4 py-3 border-b border-gray-200 font-semibold text-[#16325C]` |
| Button (Primary) | `bg-[#00A1E0] hover:bg-[#0088C7] text-white px-4 py-2.5 rounded-lg text-sm font-medium` |
| Button (Secondary) | `bg-white border border-gray-300 text-[#16325C] hover:bg-gray-50` |
| Input | `w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm text-gray-900 placeholder-gray-400 focus:border-[#00A1E0] focus:ring-1 focus:ring-[#00A1E0]` |
| Label | `block text-xs font-semibold text-gray-600 mb-1.5` |
| Badge (Solid) | `px-2 py-0.5 rounded text-xs font-medium text-white` + 배경색 직접 지정 |
| Table Header | `text-xs font-semibold text-gray-500 uppercase bg-gray-50 px-4 py-3` |
| Table Cell | `px-4 py-3 text-sm text-gray-900` |

---

## 3. API 클라이언트 설계

### 3.1 lib/api.ts

```typescript
const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface ApiOptions {
  method?: string;
  body?: unknown;
  headers?: Record<string, string>;
}

async function apiClient<T>(path: string, options: ApiOptions = {}): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    method: options.method || 'GET',
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': process.env.NEXT_PUBLIC_API_KEY || '',
      ...options.headers,
    },
    body: options.body ? JSON.stringify(options.body) : undefined,
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(error.detail || `API Error: ${res.status}`);
  }
  return res.json();
}

// === Health ===
export const getHealth = () => apiClient<HealthResponse>('/health');

// === Connectors (7개) ===
export const listConnectors = () => apiClient<Connector[]>('/v1/connectors');
export const getConnector = (id: string) => apiClient<ConnectorDetail>(`/v1/connectors/${id}`);
export const createConnector = (data: CreateConnectorReq) =>
  apiClient<Connector>('/v1/connectors', { method: 'POST', body: data });
export const verifyConnectorKey = (id: string, apiKey: string) =>
  apiClient<VerifyResult>(`/v1/connectors/${id}/verify`, { method: 'POST', body: { api_key: apiKey } });
export const syncConnector = (id: string) =>
  apiClient<SyncResult>(`/v1/connectors/${id}/sync`, { method: 'POST' });
export const getConnectorSchema = (id: string) =>
  apiClient<SchemaResult>(`/v1/connectors/${id}/schema`);
export const renewConnectorKey = (id: string) =>
  apiClient<RenewResult>(`/v1/connectors/${id}/renew`, { method: 'POST' });
export const deleteConnector = (id: string) =>
  apiClient<DeleteResult>(`/v1/connectors/${id}`, { method: 'DELETE' });

// === Upload & Data (3개) ===
export const uploadCSV = (file: File, targetColumn: string) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('target_column', targetColumn);
  return fetch(`${BASE_URL}/v1/upload`, { method: 'POST', body: formData }).then(r => r.json());
};
export const postWhatData = (data: WhatDataReq) =>
  apiClient<WhatDataResult>('/v1/whatdata', { method: 'POST', body: data });
export const postEDA = (data: EDAReq) =>
  apiClient<EDAResult>('/v1/eda', { method: 'POST', body: data });

// === Analysis (3개) ===
export const startAnalysis = (data: AnalyzeReq) =>
  apiClient<AnalysisResponse>('/v1/analyze', { method: 'POST', body: data });
export const getTaskStatus = (taskId: string) =>
  apiClient<StatusResponse>(`/v1/status/${taskId}`);
export const getReport = (taskId: string) =>
  apiClient<ReportResponse>(`/v1/report/${taskId}`);

// === Simulation & Optimize (2개) ===
export const simulate = (data: SimulateReq) =>
  apiClient<SimulateResult>('/v1/simulate', { method: 'POST', body: data });
export const optimize = (data: OptimizeReq) =>
  apiClient<OptimizeResult>('/v1/optimize', { method: 'POST', body: data });

// === Actions (3개) ===
export const generateActions = (taskId: string, data: ActionReq) =>
  apiClient<ActionResult>(`/v1/actions/${taskId}`, { method: 'POST', body: data });
export const getActions = (taskId: string) =>
  apiClient<ActionResult>(`/v1/actions/${taskId}`);
export const getActionHistory = (taskId: string) =>
  apiClient<ActionHistory>(`/v1/actions/${taskId}/history`);

// === AI Q&A (1개) ===
export const askQuestion = (taskId: string, data: QAReq) =>
  apiClient<QAResult>(`/v1/qa/${taskId}`, { method: 'POST', body: data });

// === Threshold (2개) ===
export const getThreshold = () => apiClient<ThresholdResponse>('/v1/threshold');
export const updateThreshold = (data: ThresholdUpdateReq) =>
  apiClient<ThresholdResponse>('/v1/threshold', { method: 'PATCH', body: data });
```

### 3.2 lib/types.ts (핵심 타입)

```typescript
// === Connector ===
interface Connector {
  connector_id: string;
  tenant_name: string;
  status: 'active' | 'inactive' | 'suspended';
  created_at: string;
  scopes: string[];
}

interface CreateConnectorReq {
  tenant_name: string;
  callback_url: string;
  scopes: string[];
  ip_whitelist?: string[];
}

// === Analysis ===
interface AnalyzeReq {
  data: Record<string, unknown>[];
  target_column: string;
  task_type: 'regression' | 'classification' | 'multiclass' | 'timeseries';
  enable_xai: boolean;
  webhook_url?: string;
}

interface AnalysisResponse {
  task_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  message: string;
  created_at: string;
}

interface StatusResponse {
  task_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number | null;
  message: string;
}

// === Report (핵심) ===
interface AlgorithmResult {
  name: string;
  r2_score: number;
  adj_r2_score: number | null;
  p_value: number | null;
  execution_time: number;
}

interface WinnerModel {
  algorithm: string;
  r2_score: number;
  adj_r2_score: number | null;
  formula: string;
  coefficients: Record<string, number>;
  feature_importance: Record<string, number>;
}

interface XAIInsights {
  shap_values: Record<string, number> | null;
  lime_explanation: string | null;
  top_features: string[];
}

interface NaturalLanguageReport {
  summary: string;
  key_findings: string[];
  variable_impacts: string[];
  selection_reason: string;
}

interface ReportResponse {
  task_id: string;
  status: 'completed' | 'failed';
  total_algorithms_tested: number;
  tournament_duration: number;
  top_5_algorithms: AlgorithmResult[];
  winner: WinnerModel;
  xai_insights: XAIInsights | null;
  report: NaturalLanguageReport;
  completed_at: string;
  data_shape: [number, number];
}

// === Simulate ===
interface SimulateReq {
  task_id: string;
  scenarios: Record<string, number>[];
}

// === Actions ===
interface ActionReq {
  thresholds?: Record<string, number>;
  webhook_url?: string;
}

// === Q&A ===
interface QAReq {
  question: string;
  context?: string;
}
```

---

## 4. 페이지별 상세 설계

### 4.1 대시보드 (홈) — `/`

**목적**: 시스템 전체 현황 한눈에 파악

```
┌─────────────────────────────────────────────────────┐
│ [Compact Header] OmniMetric Dashboard               │
├─────────────────────────────────────────────────────┤
│ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐   │
│ │ API     │ │ 연동    │ │ 최근    │ │ 알고리즘│   │
│ │ Status  │ │ 고객사  │ │ 분석    │ │ 155+    │   │
│ │ ●Active │ │ 12건   │ │ 3건    │ │ 4 유형  │   │
│ └─────────┘ └─────────┘ └─────────┘ └─────────┘   │
│                                                      │
│ ┌────────────────────────────────────────────────┐  │
│ │ 최근 분석 작업                          [+새 분석] │
│ │ ┌────┬──────────┬────────┬────────┬────────┐  │  │
│ │ │ ID │ 분석유형  │ 상태   │ R²    │ 시간   │  │  │
│ │ │ t01│ 회귀분석  │ ✅완료 │ 0.923 │ 45s    │  │  │
│ │ │ t02│ 분류     │ 🔄진행 │ -     │ -      │  │  │
│ │ └────┴──────────┴────────┴────────┴────────┘  │  │
│ └────────────────────────────────────────────────┘  │
│                                                      │
│ ┌──────────────────┐ ┌──────────────────────────┐   │
│ │ 빠른 실행        │ │ 시스템 정보              │   │
│ │ [📤 데이터 업로드]│ │ Version: 1.0.0           │   │
│ │ [📊 분석 시작]   │ │ Env: development          │   │
│ │ [🔗 커넥터 관리] │ │ Uptime: 2h 15m           │   │
│ └──────────────────┘ └──────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

**API 연동**:
- `GET /health` → 시스템 상태 카드
- `GET /v1/connectors` → 연동 고객사 수
- `GET /v1/threshold` → 현재 설정값

**컴포넌트**:
- `StatCard` (KPI 요약 4개)
- `RecentAnalysisTable` (최근 작업 목록)
- `QuickActionPanel` (빠른 실행 버튼)

---

### 4.2 B2B 커넥터 관리 — `/connectors`

**목적**: 고객사(을) 연동 등록, API Key 관리

```
┌─────────────────────────────────────────────────────┐
│ [Header] B2B 커넥터 관리              [+ 고객사 등록] │
├─────────────────────────────────────────────────────┤
│                                                      │
│ ┌──────────────────┐ ┌──────────────────┐           │
│ │ 🏢 누리팜        │ │ 🏢 인슈어그래프  │           │
│ │ Status: Active   │ │ Status: Active   │           │
│ │ Scopes: read     │ │ Scopes: read,wrt │           │
│ │ Created: 3/10    │ │ Created: 3/11    │           │
│ │ ─────────────── │ │ ─────────────── │           │
│ │ [검증] [갱신]    │ │ [검증] [갱신]    │           │
│ │ [스키마] [동기화] │ │ [스키마] [동기화] │           │
│ └──────────────────┘ └──────────────────┘           │
│                                                      │
└─────────────────────────────────────────────────────┘
```

**커넥터 상세** — `/connectors/[id]`:

```
┌─────────────────────────────────────────────────────┐
│ [Header] 누리팜 연동 상세     [갱신] [해제] [동기화]  │
├─────────────────────────────────────────────────────┤
│ ┌────────────────────────────────────────────────┐  │
│ │ 기본 정보                                       │  │
│ │ Tenant: 누리팜 | ID: conn_abc123                │  │
│ │ Status: Active | Scopes: read, write            │  │
│ │ Callback: https://nuriparm.com/webhook          │  │
│ │ IP Whitelist: 10.0.1.0/24, 192.168.1.100       │  │
│ │ Created: 2026-03-10T09:30:00Z                   │  │
│ └────────────────────────────────────────────────┘  │
│                                                      │
│ ┌────────────────────────────────────────────────┐  │
│ │ API Key 검증                                    │  │
│ │ [Enter API Key............] [검증하기]           │  │
│ │ Result: ✅ API Key가 유효합니다.                 │  │
│ └────────────────────────────────────────────────┘  │
│                                                      │
│ ┌────────────────────────────────────────────────┐  │
│ │ 스키마 탐색 결과                                │  │
│ │ ┌──────────┬────────┬──────────┐               │  │
│ │ │ 컬럼명   │ 타입   │ Nullable │               │  │
│ │ │ age      │ int    │ No       │               │  │
│ │ │ income   │ float  │ No       │               │  │
│ │ │ target   │ int    │ No       │               │  │
│ │ └──────────┴────────┴──────────┘               │  │
│ └────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

**API 연동 (7개)**:
- `GET /v1/connectors` → 목록
- `GET /v1/connectors/{id}` → 상세
- `POST /v1/connectors` → 생성 (모달 폼)
- `POST /v1/connectors/{id}/verify` → Key 검증
- `POST /v1/connectors/{id}/renew` → Key 갱신
- `POST /v1/connectors/{id}/sync` → 데이터 동기화
- `GET /v1/connectors/{id}/schema` → 스키마 탐색
- `DELETE /v1/connectors/{id}` → 연동 해제

**컴포넌트**:
- `ConnectorCard` (카드형 목록)
- `CreateConnectorModal` (생성 폼 모달)
- `KeyVerifyForm` (Key 검증 인풋)
- `SchemaViewer` (스키마 테이블)

---

### 4.3 데이터 업로드 & 현황분석 — `/data`

**목적**: CSV 업로드 → WhatDataAI 추천 → EDA 시각화

```
┌─────────────────────────────────────────────────────┐
│ [Header] 데이터 관리                                  │
├─────────────────────────────────────────────────────┤
│ ┌ Step 1: CSV 업로드 ─────────────────────────────┐ │
│ │  ┌────────────────────────────────────────┐      │ │
│ │  │       📤 파일을 여기에 드래그하세요       │      │ │
│ │  │       또는 클릭하여 선택                  │      │ │
│ │  └────────────────────────────────────────┘      │ │
│ │  타겟 컬럼: [Select Column ▼]                     │ │
│ │  [업로드하기]                                      │ │
│ │                                                    │ │
│ │  미리보기 (상위 10행):                              │ │
│ │  ┌──────┬────────┬──────┬────────┐               │ │
│ │  │ age  │ income │ edu  │ target │               │ │
│ │  │  25  │ 50000  │  16  │   1    │               │ │
│ │  └──────┴────────┴──────┴────────┘               │ │
│ └────────────────────────────────────────────────── │
│                                                      │
│ ┌ Step 2: WhatDataAI 추천 ────────────────────────┐ │
│ │  데이터 특성: 수치형 12개, 범주형 3개              │ │
│ │  추천 분석유형: ✅ 회귀분석 (연속형 타겟)          │ │
│ │  데이터 품질: 87% (결측값 2개 컬럼)               │ │
│ └──────────────────────────────────────────────────┘ │
│                                                      │
│ ┌ Step 3: 현황분석 (EDA) ─────────────────────────┐ │
│ │  [분포] [상관행렬] [이상치] [결측값]    탭 전환    │ │
│ │  ┌────────────────────────────────────────┐      │ │
│ │  │ 📊 분포 히스토그램                      │      │ │
│ │  │   (Recharts BarChart)                   │      │ │
│ │  └────────────────────────────────────────┘      │ │
│ └──────────────────────────────────────────────────┘ │
│                                                      │
│ [📊 분석 시작 →]                                     │
└─────────────────────────────────────────────────────┘
```

**API 연동 (3개)**:
- `POST /v1/upload` → CSV 업로드 (FormData)
- `POST /v1/whatdata` → 데이터 특성 분석
- `POST /v1/eda` → EDA 분석 (분포, 상관행렬, 이상치)

**컴포넌트**:
- `FileDropzone` (드래그 앤 드롭 업로드)
- `DataPreviewTable` (미리보기 테이블)
- `WhatDataPanel` (추천 결과 표시)
- `EDATabPanel` (탭 전환: 분포/상관행렬/이상치/결측값)
- `DistributionChart` (Recharts BarChart)
- `HeatmapChart` (Recharts 상관행렬)

---

### 4.4 분석 실행 — `/analyze`

**목적**: 분석 설정 + 실행 + 진행률 모니터링

```
┌─────────────────────────────────────────────────────┐
│ [Header] 분석 실행                                    │
├─────────────────────────────────────────────────────┤
│ ┌ 분석 설정 ──────────────────────────────────────┐ │
│ │                                                    │ │
│ │  타겟 컬럼(Y):  [target ▼]                        │ │
│ │                                                    │ │
│ │  분석 유형:                                        │ │
│ │  ○ 회귀분석 (60개 알고리즘)                        │ │
│ │  ○ 이진분류 (17개 알고리즘)                        │ │
│ │  ○ 다중분류 (17개 알고리즘)                        │ │
│ │  ○ 시계열분석 (61개 알고리즘)                      │ │
│ │                                                    │ │
│ │  ☑ XAI 분석 활성화 (SHAP/LIME)                    │ │
│ │                                                    │ │
│ │  Webhook URL: [https://...]  (선택사항)            │ │
│ │                                                    │ │
│ │  [🚀 분석 시작]                                    │ │
│ └────────────────────────────────────────────────── │
│                                                      │
│ ┌ 진행 상태 ──────────────────────────────────────┐ │
│ │  Task ID: task_abc123                              │ │
│ │  Status: 🔄 Processing                            │ │
│ │  ████████████░░░░░░░░  65%                        │ │
│ │  "60개 알고리즘 중 39개 완료..."                    │ │
│ │                                                    │ │
│ │  [결과 보기 →] (완료 시 활성화)                     │ │
│ └──────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
```

**데이터 흐름**:
1. 사용자 설정 입력
2. `POST /v1/analyze` → `task_id` 수신 (202 Accepted)
3. `GET /v1/status/{task_id}` 폴링 (3초 간격)
4. `status === 'completed'` → 결과 페이지로 이동

**API 연동 (2개)**:
- `POST /v1/analyze` → 분석 시작
- `GET /v1/status/{task_id}` → 진행률 폴링

**컴포넌트**:
- `AnalysisForm` (설정 폼)
- `TaskTypeSelector` (분석유형 라디오)
- `ProgressBar` (진행률 바)
- `StatusPoller` (폴링 로직 hook)

---

### 4.5 분석 결과 & 근거 — `/report/[taskId]` ★핵심

**목적**: "왜 이 알고리즘이 선택됐는지" 시각적 증거 제시

```
┌─────────────────────────────────────────────────────┐
│ [Header] 분석 결과 & 근거         Task: task_abc123  │
├─────────────────────────────────────────────────────┤
│                                                      │
│ ┌ 🏆 승자 알고리즘 ──────────────────────────────┐  │
│ │  Random Forest Regressor                        │  │
│ │  R² = 0.9234  |  Adj.R² = 0.9187  |  P < 0.001 │  │
│ │  155개 알고리즘 토너먼트에서 1위 선정            │  │
│ │  실행 시간: 2.34초                               │  │
│ └────────────────────────────────────────────────┘  │
│                                                      │
│ ┌ 📐 수학적 공식 ────────────────────────────────┐  │
│ │                                                  │  │
│ │  Y = 0.42×income + 0.31×age - 0.15×debt + 12.5 │  │
│ │                                                  │  │
│ │  ┌──────────┬────────┬──────────┐               │  │
│ │  │ 변수     │ 계수   │ 방향     │               │  │
│ │  │ income   │ +0.42  │ ↑ 양(+)  │               │  │
│ │  │ age      │ +0.31  │ ↑ 양(+)  │               │  │
│ │  │ debt     │ -0.15  │ ↓ 음(-)  │               │  │
│ │  │ intercpt │ +12.50 │ 절편     │               │  │
│ │  └──────────┴────────┴──────────┘               │  │
│ └────────────────────────────────────────────────┘  │
│                                                      │
│ ┌ 📊 변수 기여도 ────────────────────────────────┐  │
│ │                                                  │  │
│ │  income   ███████████████████████  42%  (+)      │  │
│ │  age      ██████████████          31%  (+)      │  │
│ │  debt     ████████               15%  (-)      │  │
│ │  edu      █████                  12%  (+)      │  │
│ │                                                  │  │
│ └────────────────────────────────────────────────┘  │
│                                                      │
│ ┌ 🏅 알고리즘 토너먼트 랭킹 ────────────────────┐  │
│ │  ┌────┬─────────────────────┬───────┬────────┐ │  │
│ │  │ #  │ 알고리즘            │ R²    │ P-val  │ │  │
│ │  │ 1  │ Random Forest       │ 0.923 │ <0.001 │ │  │
│ │  │ 2  │ Gradient Boosting   │ 0.918 │ <0.001 │ │  │
│ │  │ 3  │ XGBoost             │ 0.912 │ <0.001 │ │  │
│ │  │ 4  │ Ridge Regression    │ 0.891 │ <0.001 │ │  │
│ │  │ 5  │ Lasso               │ 0.887 │  0.002 │ │  │
│ │  └────┴─────────────────────┴───────┴────────┘ │  │
│ └────────────────────────────────────────────────┘  │
│                                                      │
│ ┌ 🔍 XAI 해석 (SHAP) ──────────────────────────┐  │
│ │  상위 영향 변수: income, age, debt              │  │
│ │                                                  │  │
│ │  SHAP Values:                                    │  │
│ │  income  ████████████████████  +0.35             │  │
│ │  age     ███████████           +0.22             │  │
│ │  debt    ██████████            -0.18             │  │
│ │                                                  │  │
│ │  LIME: "income이 1단위 증가하면 Y가             │  │
│ │         평균 0.42 증가하는 경향을 보입니다."     │  │
│ └────────────────────────────────────────────────┘  │
│                                                      │
│ ┌ 📝 Sim4Brief 리포트 ─────────────────────────┐   │
│ │  분석 요약:                                     │   │
│ │  "155개 알고리즘을 실행한 결과, Random Forest   │   │
│ │   Regressor가 R² 0.9234로 최적 모델로 선정     │   │
│ │   되었습니다. income 변수가 42%로 가장 큰       │   │
│ │   영향을 미치며, 양(+)의 방향성을 보입니다."    │   │
│ │                                                  │   │
│ │  핵심 발견:                                      │   │
│ │  • income은 결과에 가장 큰 양의 영향            │   │
│ │  • debt는 유일한 음의 영향 변수                  │   │
│ │  • age와 education은 보조적 양의 영향           │   │
│ │                                                  │   │
│ │  모델 선정 사유:                                  │   │
│ │  "R² 0.9234, P-value < 0.001로 통계적으로       │   │
│ │   유의미하며, 비선형 관계를 효과적으로 포착"     │   │
│ └────────────────────────────────────────────────┘  │
│                                                      │
│ [📈 시뮬레이션 →] [⚡ 행동 시나리오 →] [💬 Q&A →]  │
└─────────────────────────────────────────────────────┘
```

**API 연동 (1개)**:
- `GET /v1/report/{task_id}` → 전체 리포트 데이터

**응답 데이터 매핑**:

| UI 섹션 | 데이터 소스 |
|---------|------------|
| 승자 카드 | `report.winner.algorithm`, `.r2_score`, `.adj_r2_score` |
| 수학적 공식 | `report.winner.formula`, `.coefficients` |
| 변수 기여도 | `report.winner.feature_importance` |
| 토너먼트 랭킹 | `report.top_5_algorithms` |
| XAI 해석 | `report.xai_insights.shap_values`, `.lime_explanation`, `.top_features` |
| Sim4Brief | `report.report.summary`, `.key_findings`, `.variable_impacts`, `.selection_reason` |

**컴포넌트**:
- `WinnerCard` — 승자 알고리즘 하이라이트 카드
- `FormulaDisplay` — Y = w₁X₁ + ... + b 수식 + 계수 테이블
- `FeatureImportanceChart` — 수평 바 차트 (Recharts BarChart)
- `TournamentRanking` — 알고리즘 R² 랭킹 테이블 (정렬 가능)
- `XAIInsightsPanel` — SHAP 바 차트 + LIME 텍스트
- `NLGReportCard` — 자연어 요약, 핵심 발견, 선정 사유

---

### 4.6 What-if 시뮬레이션 — `/simulate/[taskId]`

**목적**: 변수 값 조절 → 예측값 변화 확인

```
┌─────────────────────────────────────────────────────┐
│ [Header] What-if 시뮬레이션        Task: task_abc123 │
├─────────────────────────────────────────────────────┤
│                                                      │
│ ┌ 변수 조절 ─────────────────────────────────────┐  │
│ │                                                  │  │
│ │  income:  ◄────────●────────────► 75,000        │  │
│ │           (원래: 50,000 → +50%)                  │  │
│ │                                                  │  │
│ │  age:     ◄──────●──────────────► 35            │  │
│ │           (원래: 30 → +17%)                      │  │
│ │                                                  │  │
│ │  debt:    ◄────────────────●────► 8,000         │  │
│ │           (원래: 10,000 → -20%)                  │  │
│ │                                                  │  │
│ │  [시나리오 추가] [리셋]                           │  │
│ └────────────────────────────────────────────────┘  │
│                                                      │
│ ┌ 예측 결과 ─────────────────────────────────────┐  │
│ │  원래 예측값:  23.5                              │  │
│ │  조절 후 예측: 31.2  (▲ +7.7, +32.8%)           │  │
│ └────────────────────────────────────────────────┘  │
│                                                      │
│ ┌ 시나리오 비교 ─────────────────────────────────┐  │
│ │  ┌──────────┬──────────┬──────────┬──────────┐ │  │
│ │  │          │ 기본     │ 시나리오1│ 시나리오2│ │  │
│ │  │ income   │ 50,000   │ 75,000   │ 60,000   │ │  │
│ │  │ age      │ 30       │ 35       │ 30       │ │  │
│ │  │ 예측 Y   │ 23.5     │ 31.2     │ 27.8     │ │  │
│ │  │ 변화율   │ -        │ +32.8%   │ +18.3%   │ │  │
│ │  └──────────┴──────────┴──────────┴──────────┘ │  │
│ └────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

**API 연동 (1개)**:
- `POST /v1/simulate` → 시나리오별 예측값 계산

**컴포넌트**:
- `VariableSlider` — 레인지 슬라이더 (min/max/step)
- `PredictionCard` — 예측값 + 변화율
- `ScenarioCompareTable` — 시나리오 비교 테이블

---

### 4.7 행동 시나리오 — `/actions/[taskId]`

**목적**: IF-THEN 행동 규칙 생성 + 이력 관리

```
┌─────────────────────────────────────────────────────┐
│ [Header] 행동 시나리오              [시나리오 생성]    │
├─────────────────────────────────────────────────────┤
│                                                      │
│ ┌ IF-THEN 카드 (우선순위순) ─────────────────────┐  │
│ │                                                  │  │
│ │  ┌ Priority 1 ───────────────────────────────┐  │  │
│ │  │ IF income > 60,000 AND debt < 5,000       │  │  │
│ │  │ THEN 프리미엄 서비스 추천                  │  │  │
│ │  │ 영향: Y +28%  |  신뢰도: 92%              │  │  │
│ │  └───────────────────────────────────────────┘  │  │
│ │                                                  │  │
│ │  ┌ Priority 2 ───────────────────────────────┐  │  │
│ │  │ IF age > 40 AND education > 16            │  │  │
│ │  │ THEN 투자 상품 안내                        │  │  │
│ │  │ 영향: Y +15%  |  신뢰도: 85%              │  │  │
│ │  └───────────────────────────────────────────┘  │  │
│ └────────────────────────────────────────────────┘  │
│                                                      │
│ ┌ 이력 ──────────────────────────────────────────┐  │
│ │  2026-03-12 14:30  시나리오 3건 생성            │  │
│ │  2026-03-12 10:15  시나리오 2건 생성 + Webhook  │  │
│ └────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

**API 연동 (3개)**:
- `POST /v1/actions/{task_id}` → 시나리오 생성
- `GET /v1/actions/{task_id}` → 시나리오 조회
- `GET /v1/actions/{task_id}/history` → 이력 조회

**컴포넌트**:
- `ActionCard` — IF-THEN 규칙 카드 (우선순위 배지)
- `ActionHistory` — 이력 타임라인
- `WebhookConfig` — Webhook URL 설정

---

### 4.8 AI Q&A — `/qa/[taskId]`

**목적**: 분석 결과에 대한 자연어 질의응답

```
┌─────────────────────────────────────────────────────┐
│ [Header] AI Q&A                    Task: task_abc123 │
├─────────────────────────────────────────────────────┤
│                                                      │
│ ┌ 추천 질문 ─────────────────────────────────────┐  │
│ │ [매출에 가장 큰 영향?] [모델 신뢰도는?]          │  │
│ │ [debt를 줄이면?] [알고리즘 비교 설명]            │  │
│ └────────────────────────────────────────────────┘  │
│                                                      │
│ ┌ 채팅 영역 ─────────────────────────────────────┐  │
│ │                                                  │  │
│ │  🧑 매출에 가장 큰 영향을 미치는 변수는?        │  │
│ │                                                  │  │
│ │  🤖 분석 결과에 따르면, income 변수가 42%로     │  │
│ │     가장 큰 양(+)의 영향을 미칩니다. income이    │  │
│ │     1단위 증가하면 Y가 평균 0.42 증가합니다.     │  │
│ │                                                  │  │
│ │  🧑 debt를 줄이면 어떻게 되나요?                 │  │
│ │                                                  │  │
│ │  🤖 debt는 15%의 음(-) 방향 기여도를 가집니다.   │  │
│ │     debt를 10% 줄이면 Y가 약 1.5% 개선될 것으로 │  │
│ │     예측됩니다. 시뮬레이션에서 정확한 수치를     │  │
│ │     확인해보세요.                                 │  │
│ │                                                  │  │
│ └────────────────────────────────────────────────┘  │
│                                                      │
│ ┌──────────────────────────────────────┐ [전송]     │
│ │ 질문을 입력하세요...                  │            │
│ └──────────────────────────────────────┘            │
└─────────────────────────────────────────────────────┘
```

**API 연동 (1개)**:
- `POST /v1/qa/{task_id}` → 질문 전송 + 답변 수신

**컴포넌트**:
- `SuggestedQuestions` — 추천 질문 칩
- `ChatMessage` — 사용자/AI 메시지 버블
- `ChatInput` — 입력 필드 + 전송 버튼

---

## 5. 데이터 흐름 다이어그램

### 5.1 핵심 분석 플로우

```
사용자 → /data (업로드)
         ↓ POST /v1/upload
         ↓ POST /v1/whatdata (추천)
         ↓ POST /v1/eda (시각화)
       → /analyze (실행)
         ↓ POST /v1/analyze → task_id
         ↓ GET /v1/status/{id} (폴링, 3초)
         ↓ status === 'completed'
       → /report/{taskId} (결과 ★)
         ↓ GET /v1/report/{id}
         ↓ winner, formula, feature_importance, xai, nlg
       → /simulate/{taskId} (시뮬레이션)
       → /actions/{taskId} (행동 시나리오)
       → /qa/{taskId} (AI Q&A)
```

### 5.2 진행률 폴링 로직

```typescript
// hooks/useTaskPolling.ts
function useTaskPolling(taskId: string) {
  const [status, setStatus] = useState<StatusResponse | null>(null);

  useEffect(() => {
    if (!taskId) return;
    const interval = setInterval(async () => {
      const result = await getTaskStatus(taskId);
      setStatus(result);
      if (result.status === 'completed' || result.status === 'failed') {
        clearInterval(interval);
      }
    }, 3000);
    return () => clearInterval(interval);
  }, [taskId]);

  return status;
}
```

---

## 6. 구현 순서

| Phase | 내용 | 컴포넌트 수 | API 수 |
|-------|------|:-----------:|:------:|
| **Phase 1** | 프로젝트 초기화 + 레이아웃 + API 클라이언트 | 6 | 1 |
| **Phase 2** | B2B 커넥터 관리 | 4 | 8 |
| **Phase 3** | 데이터 업로드 + WhatData + EDA | 6 | 3 |
| **Phase 4** | 분석 실행 + 진행률 | 4 | 2 |
| **Phase 5** | 분석 결과 & 근거 (★핵심) | 6 | 1 |
| **Phase 6** | 시뮬레이션 + 시나리오 + Q&A + 대시보드 | 8 | 5 |

**총계**: 34개 컴포넌트, 22개 API 연동 (2개 추가: health, threshold)

---

## 7. 에러 처리 전략

| 상황 | 처리 |
|------|------|
| API 서버 미응답 | "서버에 연결할 수 없습니다" 토스트 + 재시도 버튼 |
| 401 Unauthorized | "API Key가 유효하지 않습니다" + 설정 페이지 안내 |
| 403 Forbidden | "IP 접근이 차단되었습니다" (B2B 커넥터) |
| 404 Not Found | "리소스를 찾을 수 없습니다" + 목록으로 이동 |
| 분석 실패 | "분석이 실패했습니다: {message}" + 재시도 |
| 네트워크 오류 | 자동 재시도 (최대 3회, exponential backoff) |

---

## 8. 성능 최적화

- **React Server Components**: 정적 데이터는 서버에서 렌더링
- **폴링 최적화**: `completed`/`failed` 시 폴링 즉시 중단
- **차트 지연 로딩**: `dynamic(() => import('recharts'), { ssr: false })`
- **데이터 캐싱**: `fetch` 옵션으로 리포트 데이터 캐시 (revalidate: 60)

---

## Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2026-03-12 | Initial frontend design | Claude Code |
