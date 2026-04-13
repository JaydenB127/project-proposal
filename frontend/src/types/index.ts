export type RunStatus = 'created' | 'running' | 'completed' | 'failed' | 'paused'

export interface RunSummary {
  id: string
  name: string
  experiment_id: string
  status: RunStatus
  params: Record<string, unknown>
  git_commit: string | null
  data_version: string | null
  created_at: string
  completed_at: string | null
}

export interface MetricPoint {
  step: number
  value: number
  timestamp: string
}

export interface RunDetail extends RunSummary {
  metadata_: Record<string, unknown>
  started_at: string | null
  updated_at: string
  metrics: Array<{
    id: number
    key: string
    value: number
    step: number | null
    timestamp: string
  }>
}

export interface CompareResult {
  run_id: string
  run_name: string
  params: Record<string, unknown>
  data_version: string | null
  metrics_summary: Record<string, {
    min: number; max: number; last: number; count: number
  }>
  data_version_warning: boolean
}

export interface ComparisonReport {
  run_ids: string[]
  metrics_compared: string[]
  results: CompareResult[]
  warnings: string[]
}

export interface ChartSeries {
  id: string
  name: string
  color: string
  data: MetricPoint[]
}

export interface ChartData {
  metric: string
  runs: ChartSeries[]
}

export interface APIResponse<T> {
  success: boolean
  data: T
  meta: Record<string, unknown>
  errors: string[]
}
