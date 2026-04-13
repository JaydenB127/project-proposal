import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, GitCommit, Database, Clock } from 'lucide-react'
import { api } from '../lib/api'
import { StatusBadge } from '../components/StatusBadge'
import { MetricChart } from '../components/MetricChart'
import type { RunDetail } from '../types'

export function RunDetailPage() {
  const { id } = useParams<{ id: string }>()
  const [run, setRun] = useState<RunDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [selectedMetric, setSelectedMetric] = useState<string>('')

  useEffect(() => {
    if (!id) return
    api.runs.get(id)
      .then(r => {
        setRun(r)
        const keys = [...new Set((r.metrics || []).map(m => m.key))]
        if (keys.length) setSelectedMetric(keys[0])
      })
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [id])

  if (loading) return <div className="text-muted text-sm animate-pulse p-8">Loading run…</div>
  if (error)   return <div className="text-danger text-sm p-8">{error}</div>
  if (!run)    return null

  const metricKeys = [...new Set((run.metrics || []).map(m => m.key))]

  const metricSummary: Record<string, { min: number; max: number; last: number; count: number }> = {}
  for (const m of (run.metrics || [])) {
    const v = m.value
    if (!metricSummary[m.key]) {
      metricSummary[m.key] = { min: v, max: v, last: v, count: 0 }
    }
    const s = metricSummary[m.key]
    s.min = Math.min(s.min, v)
    s.max = Math.max(s.max, v)
    s.last = v
    s.count++
  }

  return (
    <div className="fade-in space-y-6">
      <div>
        <Link to="/runs" className="inline-flex items-center gap-1.5 text-xs text-muted hover:text-text transition-colors mb-4">
          <ArrowLeft size={12} /> Back to runs
        </Link>
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-lg font-semibold text-text mono">{run.name}</h1>
            <p className="text-xs text-muted mt-1 mono">{run.id}</p>
          </div>
          <StatusBadge status={run.status} />
        </div>
      </div>

      <div className="flex gap-4 flex-wrap">
        {run.git_commit && (
          <div className="flex items-center gap-1.5 text-xs text-muted">
            <GitCommit size={12} className="text-accent" />
            <span className="mono">{run.git_commit.slice(0, 10)}</span>
          </div>
        )}
        {run.data_version && (
          <div className="flex items-center gap-1.5 text-xs text-muted">
            <Database size={12} className="text-accent" />
            <span>{run.data_version}</span>
          </div>
        )}
        <div className="flex items-center gap-1.5 text-xs text-muted">
          <Clock size={12} className="text-accent" />
          <span>{new Date(run.created_at).toLocaleString()}</span>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="bg-surface border border-border rounded-xl p-5">
          <h2 className="text-xs font-semibold text-muted mb-3 uppercase tracking-wider">Parameters</h2>
          <div className="space-y-2">
            {Object.entries(run.params || {}).length === 0 && (
              <p className="text-xs text-muted">No params logged</p>
            )}
            {Object.entries(run.params || {}).map(([k, v]) => (
              <div key={k} className="flex justify-between items-center">
                <span className="text-xs text-muted">{k}</span>
                <span className="text-xs text-text mono">{String(v)}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-surface border border-border rounded-xl p-5">
          <h2 className="text-xs font-semibold text-muted mb-3 uppercase tracking-wider">Metrics Summary</h2>
          {Object.keys(metricSummary).length === 0 ? (
            <p className="text-xs text-muted">No metrics logged yet</p>
          ) : (
            <table className="w-full text-xs">
              <thead>
                <tr className="border-b border-border">
                  {['Key', 'Last', 'Min', 'Max', 'Steps'].map(h => (
                    <th key={h} className="pb-2 text-left text-muted font-medium">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {Object.entries(metricSummary).map(([key, s]) => (
                  <tr key={key} className="border-b border-border/30">
                    <td className="py-1.5 text-accent mono">{key}</td>
                    <td className="py-1.5 text-text font-medium">{s.last.toFixed(4)}</td>
                    <td className="py-1.5 text-muted">{s.min.toFixed(4)}</td>
                    <td className="py-1.5 text-muted">{s.max.toFixed(4)}</td>
                    <td className="py-1.5 text-muted">{s.count}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>

      {metricKeys.length > 0 && id && (
        <div className="bg-surface border border-border rounded-xl p-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xs font-semibold text-muted uppercase tracking-wider">Metric Chart</h2>
            <div className="flex gap-1">
              {metricKeys.map(k => (
                <button
                  key={k}
                  onClick={() => setSelectedMetric(k)}
                  className={`px-3 py-1 text-xs rounded-md transition-all ${
                    selectedMetric === k
                      ? 'bg-accent/20 text-accent'
                      : 'text-muted hover:text-text'
                  }`}
                >
                  {k}
                </button>
              ))}
            </div>
          </div>
          {selectedMetric && <MetricChart runIds={[id]} metric={selectedMetric} />}
        </div>
      )}
    </div>
  )
}