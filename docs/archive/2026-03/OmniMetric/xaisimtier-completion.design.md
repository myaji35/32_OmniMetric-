# XAISimTier (OmniMetric) 설계 문서

> **Feature**: xaisimtier-completion
> **Phase**: Design
> **Author**: CTO Lead Agent
> **Date**: 2026-03-12
> **Plan Reference**: `docs/01-plan/features/xaisimtier-completion.plan.md`

---

## 1. Architecture Overview

### 1.1 목표 아키텍처 (Phase 1~7 완료 후)

```
app/
├── core/
│   ├── engine.py              # TournamentOrchestrator (오케스트레이터)
│   ├── parallel.py            # ParallelTournament (병렬 실행)
│   ├── preprocessor.py        # DataPreprocessor (전처리)
│   ├── evaluator.py           # ModelEvaluator (Train/Test Split)
│   ├── storage.py             # TaskStorage (Redis)
│   └── config.py              # Settings (환경변수)
├── models/
│   ├── algorithms/
│   │   ├── base.py            # BaseAlgorithm, ClassificationAlgorithm, TimeSeriesAlgorithm
│   │   ├── registry.py        # AlgorithmRegistry (4유형 지원)
│   │   ├── regression/        # 기존 회귀 알고리즘 (유지)
│   │   ├── classification/    # 분류 17종
│   │   │   └── classifiers.py
│   │   ├── multiclass/        # 다중분류 17종
│   │   │   └── multiclass_classifiers.py
│   │   └── timeseries/        # 시계열 61종
│   │       └── ts_models.py
│   └── schemas.py             # 전체 스키마 (확장)
├── services/
│   ├── xai.py                 # XAIEngine (분류 지원 추가)
│   ├── simulator.py           # WhatIfSimulator
│   ├── optimizer.py           # GoalOptimizer
│   ├── whatdata.py            # WhatDataAnalyzer
│   ├── actions.py             # ActionScenarioConverter
│   ├── nlg.py                 # NLGReportGenerator
│   ├── feature_engineering.py # 시계열 파생변수 생성
│   ├── connector.py           # B2BConnectorService
│   ├── mlops.py               # MLOpsEngine (완성)
│   └── webhook.py             # WebhookService
├── api/v1/
│   ├── __init__.py            # api_router (모든 라우터 등록)
│   ├── dependencies.py        # API Key 검증, Rate Limiting
│   └── endpoints/
│       ├── analyze.py         # POST /v1/analyze (4유형)
│       ├── report.py          # GET /v1/report/{task_id}
│       ├── simulate.py        # POST /v1/simulate
│       ├── optimize.py        # POST /v1/optimize
│       ├── whatdata.py        # GET /v1/whatdata/{task_id}
│       ├── actions.py         # POST/GET /v1/actions/{task_id}
│       ├── upload.py          # POST /v1/upload
│       ├── connectors.py      # B2B 커넥터 7개 엔드포인트
│       └── threshold.py       # PATCH /v1/threshold
└── security/
    ├── rate_limiter.py        # slowapi 기반
    ├── input_validator.py     # 입력 크기 제한
    └── ssrf_guard.py          # Webhook SSRF 방어
```

---

## 2. Phase 1: Train/Test Split + 보안 + 리팩토링

### 2.1 ModelEvaluator (`app/core/evaluator.py`)

```python
class ModelEvaluator:
    """Train/Test Split 및 모델 평가"""

    def split_data(X, y, test_size=0.2, random_state=42):
        """80:20 Split"""
        return train_test_split(X, y, test_size=test_size, random_state=random_state)

    def evaluate_regression(y_true, y_pred, n_features):
        """회귀 평가: R2, Adj R2, MAE, RMSE"""

    def evaluate_classification(y_true, y_pred, y_prob=None):
        """분류 평가: Accuracy, Precision, Recall, F1, AUC-ROC"""

    def cross_validate(model, X, y, cv=5):
        """K-Fold Cross Validation"""
```

**핵심 변경**: `BaseAlgorithm.execute()`에서 전체 데이터로 학습+평가하던 로직을 Split 기반으로 변경.

### 2.2 DataPreprocessor (`app/core/preprocessor.py`)

TournamentEngine.prepare_data()를 독립 모듈로 분리.

### 2.3 NLGReportGenerator (`app/services/nlg.py`)

TournamentEngine.generate_nlg_report(), extract_formula(), calculate_feature_importance()를 분리.

### 2.4 보안 모듈 (`app/security/`)

- **rate_limiter.py**: slowapi 기반, 설정 가능한 분당 요청 제한
- **input_validator.py**: 최대 행 수(100,000), 최대 열 수(500), 최대 파일 크기(50MB)
- **ssrf_guard.py**: Webhook URL의 private IP (10.x, 172.16-31.x, 192.168.x, localhost) 차단

### 2.5 config.py 보안 강화

- `db_password` 기본값 "changeme" 제거, 환경변수 필수
- CORS `allow_origins` 환경변수화
- Rate Limiting 설정 추가

---

## 3. Phase 2: 분류/다중분류 분석

### 3.1 ClassificationAlgorithm 베이스 클래스

```python
class ClassificationAlgorithm(BaseAlgorithm):
    """분류 알고리즘 베이스"""

    def execute(self, X, y) -> Dict:
        # Train/Test Split 적용
        X_train, X_test, y_train, y_test = ModelEvaluator.split_data(X, y)
        model = self.fit(X_train, y_train)
        y_pred = self.predict(model, X_test)
        y_prob = self.predict_proba(model, X_test)  # 확률 예측
        metrics = ModelEvaluator.evaluate_classification(y_test, y_pred, y_prob)
        return {"metrics": metrics, "model": model, ...}
```

### 3.2 분류 17종 알고리즘 목록

LogisticRegression, SVM(Linear/RBF/Poly), RandomForestClassifier,
ExtraTreesClassifier, GradientBoostingClassifier, XGBClassifier,
LGBMClassifier, CatBoostClassifier, KNeighborsClassifier,
DecisionTreeClassifier, AdaBoostClassifier, BaggingClassifier,
MLPClassifier, NaiveBayes(Gaussian/Multinomial),
HistGradientBoostingClassifier, RidgeClassifier

### 3.3 다중분류 17종

동일 알고리즘을 multi_class 파라미터로 확장 (OvR/OvO).
평가지표: Macro F1, Micro F1, Weighted F1, Confusion Matrix.

### 3.4 AlgorithmRegistry 확장

```python
def get_all_algorithms(self, task_type: str) -> List:
    if task_type == "regression": return self._regression_algorithms
    elif task_type == "classification": return self._classification_algorithms
    elif task_type == "multiclass": return self._multiclass_algorithms
    elif task_type == "timeseries": return self._timeseries_algorithms
```

---

## 4. Phase 3: What-if 시뮬레이션 + 최적화

### 4.1 WhatIfSimulator (`app/services/simulator.py`)

```python
class WhatIfSimulator:
    def simulate(self, task_id, scenarios: List[Dict]) -> List[SimulationResult]:
        """
        저장된 모델에 가상 입력값 주입 -> 예측값 반환
        scenarios: [{"var_1": 10, "var_2": 20}, {"var_1": 15, "var_2": 25}]
        """
```

### 4.2 GoalOptimizer (`app/services/optimizer.py`)

```python
class GoalOptimizer:
    def optimize(self, task_id, target_value, constraints) -> OptimizationResult:
        """
        scipy.optimize.minimize 기반
        목표(Y) 달성을 위한 최적 X 조합 탐색
        constraints: {"var_1": {"min": 0, "max": 100}, ...}
        """
```

---

## 5. Phase 4: 시계열분석

### 5.1 TimeSeriesAlgorithm 베이스

시계열 전용 베이스 클래스. fit/predict가 시간축 기반.

### 5.2 자동 파생변수 엔진

```python
class FeatureEngineer:
    def generate_time_features(df, date_column) -> pd.DataFrame:
        """
        lag(1~30), rolling_mean(7,14,30), rolling_std,
        diff(1,2), pct_change, day_of_week, month, quarter,
        is_weekend, hour, seasonal_decompose 등 ~500개
        """
```

---

## 6. Phase 5: WhatDataAI + 행동 시나리오 + CSV

### 6.1 WhatDataAnalyzer

데이터 특성 자동 분석 후 적합 분석유형 추천.

### 6.2 ActionScenarioConverter

분석 결과를 IF-THEN 규칙으로 변환. 우선순위 = Impact x Probability.

### 6.3 CSV Upload

multipart/form-data, pandas.read_csv, 크기 제한.

---

## 7. Phase 6: Sim4Brief + AI Q&A + MLOps

### 7.1 NLG 강화

분석유형별 맞춤 리포트 템플릿.

### 7.2 AI Q&A

LLM API 연동. 분석 결과 컨텍스트 + 사용자 질문 -> 답변.

### 7.3 MLOps 완성

trigger_retrain()에서 실제 토너먼트 재실행.

---

## 8. Phase 7: B2B 데이터 커넥터

### 8.1 B2BConnectorService

```python
class B2BConnectorService:
    def create_connector(tenant_name, callback_url, scopes) -> ConnectorInfo:
        """API Key 생성 (SHA-256 해시 저장), 고객사 등록"""

    def verify_key(connector_id, api_key) -> bool:
        """갑↔을 API Key 유효성 검증"""

    def sync_data(connector_id) -> SyncResult:
        """을의 데이터 수집 트리거"""

    def discover_schema(connector_id) -> SchemaInfo:
        """을의 데이터 스키마 자동 탐색"""
```

### 8.2 API 엔드포인트 (7개)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/v1/connectors` | 고객사 연동 등록 + API Key 발행 |
| GET | `/v1/connectors` | 연동 목록 조회 |
| GET | `/v1/connectors/{id}` | 연동 상세 조회 |
| POST | `/v1/connectors/{id}/verify` | API Key 검증 |
| POST | `/v1/connectors/{id}/sync` | 데이터 수집 트리거 |
| GET | `/v1/connectors/{id}/schema` | 스키마 탐색 |
| DELETE | `/v1/connectors/{id}` | 연동 해제 + Key 폐기 |

### 8.3 보안

- API Key: SHA-256 해시 저장
- TLS 1.3 통신 (인프라 레벨)
- IP 화이트리스트
- 고객사별 Rate Limiting
- 감사 로그 전체 이력

---

## 9. 구현 순서 요약

| Phase | 주요 파일 | 의존성 |
|-------|----------|--------|
| 1 | evaluator.py, preprocessor.py, nlg.py, security/ | 없음 (기반) |
| 2 | classification/, multiclass/, registry.py 확장 | Phase 1 |
| 3 | simulator.py, optimizer.py, simulate.py, optimize.py | Phase 1 |
| 4 | timeseries/, feature_engineering.py | Phase 1,2 |
| 5 | whatdata.py, actions.py, upload.py | Phase 1 |
| 6 | nlg.py 강화, ai_qa.py, mlops.py 완성 | Phase 1~5 |
| 7 | connector.py, connectors.py | Phase 1 (보안) |

---

## Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2026-03-12 | 전체 Phase 1~7 설계 | CTO Lead Agent |
