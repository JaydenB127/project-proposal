import { useEffect, useState } from 'react'
import { api } from '../lib/api'
import { MetricChart } from '../components/MetricChart'
import type { RunSummary } from '../types'

export function ChartsPage() {
  const [runs, setRuns] = useState<RunSummary[]>([])
  const [selectedRuns, setSelectedRuns] = useState<string[]>([])
  const [metric, setMetric] = useState('train_loss')
  const [allMetrics, setAllMetrics] = useState<string[]>([])

  useEffect(() => {
    api.runs.list({ limit: 50 }).then(data => {
      setRuns(data)
      if (data.length > 0) {
        setSelectedRuns([data[0].id])
        // Fetch metrics for first run to populate metric picker
        api.runs.get(data[0].id).then(detail => {
          const keys = [...new Set((detail.metrics || []).map(m => m.key))]

          setAllMetrics(keys)
          if (keys.length) setMetric(keys[0])
        })
      }
    })
  }, [])

  const toggle = (id: string) => {
    setSelectedRuns(prev =>
      prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]
    )
  }

  return (
    <div className="fade-in space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-text">Charts</h1>
        <p className="text-sm text-muted mt-1">Visualize metric curves across runs</p>
      </div>

      <div className="grid grid-cols-3 gap-5">
        {/* Run + metric selector */}
        <div className="space-y-4">
          <div className="bg-surface border border-border rounded-xl overflow-hidden">
            <div className="px-4 py-3 border-b border-border">
              <p className="text-xs font-semibold text-muted uppercase tracking-wider">Runs</p>
            </div>
            <div className="divide-y divide-border/50 max-h-96 overflow-y-auto">
              {runs.map(run => (
                <div
                  key={run.id}
                  onClick={() => toggle(run.id)}
                  className={`flex items-center gap-2.5 px-4 py-2.5 cursor-pointer transition-colors ${
                    selectedRuns.includes(run.id) ? 'bg-accent/10' : 'hover:bg-white/[0.02]'
                  }`}
                >
                  <div className={`w-3 h-3 rounded-sm border flex-shrink-0 transition-all ${
                    selectedRuns.includes(run.id) ? 'bg-accent border-accent' : 'border-border'
                  }`} />
                  <p className="text-xs text-text mono truncate">{run.name}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-surface border border-border rounded-xl overflow-hidden">
            <div className="px-4 py-3 border-b border-border">
              <p className="text-xs font-semibold text-muted uppercase tracking-wider">Metric</p>
            </div>
            <div className="p-3 space-y-1">
              {allMetrics.length === 0 && (
                <p className="text-xs text-muted px-1">Select a run to see metrics</p>
              )}
              {allMetrics.map(k => (
                <button
                  key={k}
                  onClick={() => setMetric(k)}
                  className={`w-full text-left px-3 py-1.5 text-xs rounded-md mono transition-all ${
                    metric === k ? 'bg-accent/15 text-accent' : 'text-muted hover:text-text hover:bg-white/5'
                  }`}
                >
                  {k}
                </button>
              ))}
              {allMetrics.length === 0 && (
                <div className="mt-2">
                  <input
                    value={metric}
                    onChange={e => setMetric(e.target.value)}
                    placeholder="Type metric key…"
                    className="w-full px-3 py-1.5 text-xs bg-bg border border-border rounded-md text-text placeholder-muted focus:outline-none focus:border-accent mono"
                  />
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Chart area */}
        <div className="col-span-2">
          <div className="bg-surface border border-border rounded-xl p-5 h-full min-h-[360px] flex flex-col">
            {selectedRuns.length === 0 ? (
              <div className="flex-1 flex items-center justify-center text-muted text-sm">
                Select at least one run to plot
              </div>
            ) : (
              <MetricChart runIds={selectedRuns} metric={metric} />
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
