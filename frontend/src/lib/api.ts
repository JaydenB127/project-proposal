import type { APIResponse, RunSummary, RunDetail, ComparisonReport, ChartData } from '../types'

const BASE = import.meta.env.VITE_API_BASE_URL ?? ''

function getKey(): string {
  return localStorage.getItem('exp_api_key') ?? ''
}

async function req<T>(path: string, opts: RequestInit = {}): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    ...opts,
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': getKey(),
      ...(opts.headers ?? {}),
    },
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ errors: [res.statusText] }))
    throw new Error(err.errors?.[0] ?? err.detail ?? `HTTP ${res.status}`)
  }
  const json: APIResponse<T> = await res.json()
  if (!json.success) throw new Error(json.errors?.[0] ?? 'API error')
  return json.data
}

export const api = {
  setKey(key: string) { localStorage.setItem('exp_api_key', key) },
  getKey,

  health: () => fetch(`${BASE}/health`).then(r => r.json()),

  register: (username: string, email: string, password: string) =>
    req<{ api_key: string; username: string }>('/api/v1/auth/register', {
      method: 'POST',
      body: JSON.stringify({ username, email, password }),
    }),

  runs: {
    list: async (params: Record<string, string | number> = {}) => {
      const qs = new URLSearchParams(params as Record<string, string>).toString()
      const result = await req<RunSummary[]>(`/api/v1/runs${qs ? '?' + qs : ''}`)
      return Array.isArray(result) ? result : []
    },
    get: (id: string) => req<RunDetail>(`/api/v1/runs/${id}`),
    finish: (id: string) => req<{ status: string }>(`/api/v1/runs/${id}/finish`, { method: 'POST', body: '{}' }),
    fail: (id: string) => req<{ status: string }>(`/api/v1/runs/${id}/fail`, { method: 'POST', body: '{}' }),
    compare: (ids: string[], metrics: string[]) =>
      req<ComparisonReport>(`/api/v1/runs/compare?ids=${ids.join(',')}&metrics=${metrics.join(',')}`),
    chart: (ids: string[], metric: string) =>
      req<ChartData>(`/api/v1/runs/chart?ids=${ids.join(',')}&metric=${metric}`),
  },
}
