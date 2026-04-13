import { useEffect, useState } from 'react'
import { AlertTriangle, GitCompare, X } from 'lucide-react'
import { api } from '../lib/api'
import { MetricChart } from '../components/MetricChart'
import type { RunSummary, ComparisonReport } from '../types'

export function ComparePage() {
  const [runs, setRuns] = useState<RunSummary[]>([])
  const [selected, setSelected] = useState<string[]>([])
  const [metrics, setMetrics] = useState('train_loss,val_loss')
  const [report, setReport] = useState<ComparisonReport | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    api.runs.list({ limit: 100, status: 'completed' }).then(setRuns)
  }, [])

  const toggle = (id: string) => {
    setSelected(prev =>
      prev.includes(id) ? prev.filter(x => x !== id) : prev.length < 6 ? [...prev, id] : prev
    )
    setReport(null)
  }

  const compare = async () => {
    if (selected.length < 2) return
    setLoading(true)
    setError('')
    try {
      const metricList = metrics.split(',').map(s => s.trim()).filter(Boolean)
      setReport(await api.runs.compare(selected, metricList))
    } catch (e: any) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  const metricList = metrics.split(',').map(s => s.trim()).filter(Boolean)

  return (
    <div className="fade-in space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-text">Compare Runs</h1>
        <p className="text-sm text-muted mt-1">Select 2–6 completed runs to compare side-by-side</p>
      </div>

      {/* Run selector */}
      <div className="bg-surface border border-border rounded-xl overflow-hidden">
        <div className="px-5 py-4 border-b border-border">
          <p className="text-sm font-medium text-text">Select Runs ({selected.length}/6 selected)</p>
        </div>
        <div className="divide-y divide-border/50 max-h-64 overflow-y-auto">
          {runs.length === 0 && (
            <p className="px-5 py-6 text-sm text-muted">No completed runs found</p>
          )}
          {runs.map(run => {
            const isSelected = selected.includes(run.id)
            return (
              <div
                key={run.id}
                onClick={() => toggle(run.id)}
                className={`flex items-center gap-3 px-5 py-3 cursor-pointer transition-colors ${
                  isSelected ? 'bg-accent/10' : 'hover:bg-white/[0.02]'
                }`}
              >
                <div className={`w-4 h-4 rounded border flex items-center justify-center flex-shrink-0 transition-all ${
                  isSelected ? 'bg-accent border-accent' : 'border-border'
                }`}>
                  {isSelected && <div className="w-2 h-2 bg-white rounded-sm" />}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-xs text-text mono truncate">{run.name}</p>
                  <p className="text-[10px] text-muted">
                    {Object.entries(run.params).slice(0, 3).map(([k, v]) => `${k}=${v}`).join(' · ')}
                  </p>
                </div>
                {run.data_version && (
                  <span className="text-[10px] text-muted px-2 py-0.5 bg-border/50 rounded">{run.data_version}</span>
                )}
              </div>
            )
          })}
        </div>
      </div>

      {/* Metrics input + compare button */}
      <div className="flex gap-3">
        <div className="flex-1">
          <label className="block text-xs text-muted mb-1.5">Metrics to compare (comma-separated)</label>
          <input
            value={metrics}
            onChange={e => setMetrics(e.target.value)}
            placeholder="e.g. train_loss,val_loss,train_acc"
            className="w-full px-3 py-2 text-sm bg-surface border border-border rounded-lg text-text placeholder-muted focus:outline-none focus:border-accent transition-colors mono"
          />
        </div>
        <div className="flex items-end">
          <button
            onClick={compare}
            disabled={selected.length < 2 || loading}
            className="flex items-center gap-2 px-5 py-2 bg-accent text-white text-sm font-medium rounded-lg hover:bg-accent/90 disabled:opacity-40 disabled:cursor-not-allowed transition-all"
          >
            <GitCompare size={14} />
            {loading ? 'Comparing…' : 'Compare'}
          </button>
        </div>
      </div>

      {error && <p className="text-sm text-danger">{error}</p>}

      {/* Report */}
      {report && (
        <div className="space-y-5 fade-in">
          {/* Warnings */}
          {report.warnings.map((w, i) => (
            <div key={i} className="flex items-start gap-2.5 px-4 py-3 bg-warn/10 border border-warn/30 rounded-lg">
              <AlertTriangle size={14} className="text-warn flex-shrink-0 mt-0.5" />
              <p className="text-xs text-warn">{w}</p>
            </div>
          ))}

          {/* Side-by-side table */}
          <div className="bg-surface border border-border rounded-xl overflow-hidden">
            <div className="px-5 py-4 border-b border-border">
              <p className="text-sm font-medium text-text">Comparison Report</p>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-xs">
                <thead>
                  <tr className="border-b border-border">
                    <th className="px-4 py-3 text-left text-muted font-medium">Metric</th>
                    {report.results.map(r => (
                      <th key={r.run_id} className="px-4 py-3 text-left font-medium">
                        <p className="text-text mono truncate max-w-[160px]">{r.run_name}</p>
                        <p className="text-muted font-normal mt-0.5">
                          {Object.entries(r.params).slice(0, 2).map(([k, v]) => `${k}=${v}`).join(', ')}
                        </p>
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {metricList.map(metric => (
                    <tr key={metric} className="border-b border-border/50">
                      <td className="px-4 py-3 text-accent mono">{metric}</td>
                      {report.results.map(r => {
                        const s = r.metrics_summary[metric]
                        return (
                          <td key={r.run_id} className="px-4 py-3">
                            {s && s.last != null ? (
                              <div>
                                <span className="text-text font-medium">{s.last.toFixed(4)}</span>
                                <span className="text-muted ml-2">last</span>
                                <div className="text-muted mt-0.5">
                                  min {s.min.toFixed(4)} · max {s.max.toFixed(4)} · {s.count} steps
                                </div>
                              </div>
                            ) : (
                              <span className="text-muted">—</span>
                            )}
                          </td>
                        )
                      })}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Charts for each metric */}
          {metricList.map(metric => (
            <div key={metric} className="bg-surface border border-border rounded-xl p-5">
              <MetricChart runIds={selected} metric={metric} />
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
