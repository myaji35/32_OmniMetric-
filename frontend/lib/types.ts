// === Health ===
interface HealthResponse {
  status: "healthy" | "unhealthy";
  version: string;
  environment: string;
  timestamp: string;
}

// === Connector ===
interface Connector {
  connector_id: string;
  tenant_name: string;
  status: "active" | "inactive" | "suspended";
  created_at: string;
  scopes: string[];
  api_key?: string;
}

interface ConnectorDetail extends Connector {
  callback_url: string;
  ip_whitelist: string[] | null;
  last_sync?: string;
  audit_log?: AuditEntry[];
}

interface AuditEntry {
  timestamp: string;
  action: string;
  detail: string;
}

interface CreateConnectorReq {
  tenant_name: string;
  callback_url: string;
  scopes: string[];
  ip_whitelist?: string[];
}

interface VerifyResult {
  connector_id: string;
  valid: boolean;
  message: string;
}

interface SyncResult {
  connector_id: string;
  status: string;
  records_synced?: number;
  message: string;
}

interface SchemaResult {
  connector_id: string;
  schema: SchemaColumn[];
}

interface SchemaColumn {
  column_name: string;
  data_type: string;
  nullable: boolean;
}

interface RenewResult {
  connector_id: string;
  new_api_key: string;
  message: string;
}

interface DeleteResult {
  connector_id: string;
  message: string;
}

// === Upload & Data ===
interface WhatDataReq {
  data: Record<string, unknown>[];
  target_column: string;
}

interface WhatDataResult {
  recommended_task_type: string;
  data_characteristics: {
    numeric_columns: number;
    categorical_columns: number;
    total_rows: number;
    missing_ratio: number;
  };
  quality_score: number;
}

interface EDAReq {
  data: Record<string, unknown>[];
  target_column: string;
}

interface EDAResult {
  summary_statistics: Record<string, Record<string, number>>;
  distribution: Record<string, { bins: number[]; counts: number[] }>;
  correlation_matrix: Record<string, Record<string, number>>;
  missing_analysis: Record<string, { count: number; ratio: number }>;
  outlier_analysis: Record<string, { count: number; indices: number[] }>;
}

// === Analysis ===
interface AnalyzeReq {
  data: Record<string, unknown>[];
  target_column: string;
  task_type: "regression" | "classification" | "multiclass" | "timeseries";
  enable_xai: boolean;
  webhook_url?: string;
}

interface AnalysisResponse {
  task_id: string;
  status: "pending" | "processing" | "completed" | "failed";
  message: string;
  created_at: string;
}

interface StatusResponse {
  task_id: string;
  status: "pending" | "processing" | "completed" | "failed";
  progress: number | null;
  message: string;
}

// === Report ===
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
  status: "completed" | "failed";
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

interface SimulateResult {
  task_id: string;
  predictions: {
    scenario: Record<string, number>;
    predicted_value: number;
  }[];
}

// === Optimize ===
interface OptimizeReq {
  task_id: string;
  target_value: number;
  constraints: Record<string, { min?: number; max?: number }>;
  maximize: boolean;
}

interface OptimizeResult {
  task_id: string;
  optimal_values: Record<string, number>;
  predicted_outcome: number;
}

// === Actions ===
interface ActionReq {
  thresholds?: Record<string, number>;
  webhook_url?: string;
}

interface ActionRule {
  priority: number;
  condition: string;
  action: string;
  impact: string;
  confidence: number;
}

interface ActionResult {
  task_id: string;
  scenarios: ActionRule[];
}

interface ActionHistoryEntry {
  timestamp: string;
  scenario_count: number;
  webhook_sent: boolean;
}

interface ActionHistory {
  task_id: string;
  history: ActionHistoryEntry[];
}

// === Q&A ===
interface QAReq {
  question: string;
  context?: string;
}

interface QAResult {
  task_id: string;
  question: string;
  answer: string;
}

// === Threshold ===
interface ThresholdResponse {
  error_threshold: number;
  min_r2_score: number;
  updated_at: string;
}

interface ThresholdUpdateReq {
  error_threshold?: number;
  min_r2_score?: number;
}
