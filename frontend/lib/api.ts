// API client — typed fetch wrappers for the backend.

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface FetchOptions extends RequestInit {
  token?: string;
}

async function apiFetch<T>(path: string, options: FetchOptions = {}): Promise<T> {
  const { token, ...fetchOptions } = options;

  const headers: Record<string, string> = {
    ...(fetchOptions.headers as Record<string, string>),
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  if (!(fetchOptions.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
  }

  const res = await fetch(`${API_BASE}${path}`, {
    ...fetchOptions,
    headers,
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(error.detail || "API request failed");
  }

  return res.json();
}

// Types
export interface ContractListItem {
  id: string;
  filename: string;
  status: string;
  risk_score: number | null;
  risk_level: string | null;
  upload_date: string;
}

export interface ClauseResponse {
  id: string;
  clause_type: string;
  clause_text: string;
  risk_level: string | null;
  page_number: number | null;
}

export interface RiskResponse {
  id: string;
  risk_type: string;
  severity: string;
  finding: string;
  explanation: string;
  recommendation: string;
  source_text: string;
  confidence: number | null;
  clause_id: string | null;
}

export interface ContractDetail {
  id: string;
  filename: string;
  file_size: number | null;
  page_count: number | null;
  status: string;
  risk_score: number | null;
  risk_level: string | null;
  summary: string | null;
  error_message: string | null;
  upload_date: string;
  completed_at: string | null;
  clauses: ClauseResponse[];
  risks: RiskResponse[];
}

export interface ContractStatus {
  status: string;
  progress_percent: number;
  error_message: string | null;
}

export interface DashboardStats {
  total_contracts: number;
  risk_distribution: Record<string, number>;
  recent_uploads: ContractListItem[];
  avg_risk_score: number | null;
}

// API functions
export const api = {
  uploadContract: (file: File, token: string) => {
    const formData = new FormData();
    formData.append("file", file);
    return apiFetch<{ contract_id: string; status: string }>(
      "/api/v1/contracts/upload",
      { method: "POST", body: formData, token }
    );
  },

  listContracts: (token: string) =>
    apiFetch<ContractListItem[]>("/api/v1/contracts", { token }),

  getContract: (id: string, token: string) =>
    apiFetch<ContractDetail>(`/api/v1/contracts/${id}`, { token }),

  getContractStatus: (id: string, token: string) =>
    apiFetch<ContractStatus>(`/api/v1/contracts/${id}/status`, { token }),

  deleteContract: (id: string, token: string) =>
    apiFetch<{ detail: string }>(`/api/v1/contracts/${id}`, {
      method: "DELETE",
      token,
    }),

  getDashboardStats: (token: string) =>
    apiFetch<DashboardStats>("/api/v1/dashboard/stats", { token }),
};
