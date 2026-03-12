const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface ApiOptions {
  method?: string;
  body?: unknown;
  headers?: Record<string, string>;
}

async function apiClient<T>(path: string, options: ApiOptions = {}): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    method: options.method || "GET",
    headers: {
      "Content-Type": "application/json",
      ...(process.env.NEXT_PUBLIC_API_KEY
        ? { "X-API-Key": process.env.NEXT_PUBLIC_API_KEY }
        : {}),
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
export const getHealth = () => apiClient<HealthResponse>("/health");

// === Connectors (7+1) ===
export const listConnectors = () => apiClient<Connector[]>("/v1/connectors");
export const getConnector = (id: string) =>
  apiClient<ConnectorDetail>(`/v1/connectors/${id}`);
export const createConnector = (data: CreateConnectorReq) =>
  apiClient<Connector>("/v1/connectors", { method: "POST", body: data });
export const verifyConnectorKey = (id: string, apiKey: string) =>
  apiClient<VerifyResult>(`/v1/connectors/${id}/verify`, {
    method: "POST",
    body: { api_key: apiKey },
  });
export const syncConnector = (id: string) =>
  apiClient<SyncResult>(`/v1/connectors/${id}/sync`, { method: "POST" });
export const getConnectorSchema = (id: string) =>
  apiClient<SchemaResult>(`/v1/connectors/${id}/schema`);
export const renewConnectorKey = (id: string) =>
  apiClient<RenewResult>(`/v1/connectors/${id}/renew`, { method: "POST" });
export const deleteConnector = (id: string) =>
  apiClient<DeleteResult>(`/v1/connectors/${id}`, { method: "DELETE" });

// === Upload & Data (3) ===
export const uploadCSV = async (file: File, targetColumn: string) => {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("target_column", targetColumn);
  const res = await fetch(`${BASE_URL}/v1/upload`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `Upload Error: ${res.status}`);
  }
  return res.json();
};
export const postWhatData = (data: WhatDataReq) =>
  apiClient<WhatDataResult>("/v1/whatdata", { method: "POST", body: data });
export const postEDA = (data: EDAReq) =>
  apiClient<EDAResult>("/v1/eda", { method: "POST", body: data });

// === Analysis (3) ===
export const startAnalysis = (data: AnalyzeReq) =>
  apiClient<AnalysisResponse>("/v1/analyze", { method: "POST", body: data });
export const getTaskStatus = (taskId: string) =>
  apiClient<StatusResponse>(`/v1/status/${taskId}`);
export const getReport = (taskId: string) =>
  apiClient<ReportResponse>(`/v1/report/${taskId}`);

// === Simulation & Optimize (2) ===
export const simulate = (data: SimulateReq) =>
  apiClient<SimulateResult>("/v1/simulate", { method: "POST", body: data });
export const optimize = (data: OptimizeReq) =>
  apiClient<OptimizeResult>("/v1/optimize", { method: "POST", body: data });

// === Actions (3) ===
export const generateActions = (taskId: string, data: ActionReq) =>
  apiClient<ActionResult>(`/v1/actions/${taskId}`, {
    method: "POST",
    body: data,
  });
export const getActions = (taskId: string) =>
  apiClient<ActionResult>(`/v1/actions/${taskId}`);
export const getActionHistory = (taskId: string) =>
  apiClient<ActionHistory>(`/v1/actions/${taskId}/history`);

// === AI Q&A (1) ===
export const askQuestion = (taskId: string, data: QAReq) =>
  apiClient<QAResult>(`/v1/qa/${taskId}`, { method: "POST", body: data });

// === Threshold (2) ===
export const getThreshold = () =>
  apiClient<ThresholdResponse>("/v1/threshold");
export const updateThreshold = (data: ThresholdUpdateReq) =>
  apiClient<ThresholdResponse>("/v1/threshold", {
    method: "PATCH",
    body: data,
  });
