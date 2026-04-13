import { useEffect, useState, useCallback } from 'react'
import { Link } from 'react-router-dom'
import { Search, RefreshCw, Download } from 'lucide-react'
import { api } from '../lib/api'
import { StatusBadge } from '../components/StatusBadge'
import type { RunSummary, RunStatus } from '../types'

const STATUSES: Array<RunStatus | ''> = ['', 'running', 'completed', 'failed', 'created', 'paused']

function exportCSV(runs: RunSummary[]) {
  const rows = [
    ['id', 'name', 'status', 'created_at', 'completed_at', 'git_commit', 'data_version', 'params'],
    ...(runs || []).map(r => [
      r.id, r.name, r.status, r.created_at, r.completed_at ?? '',
      r.git_commit ?? '', r.data_version ?? '', JSON.stringify(r.params || {}),
    ]),
  ]
  const csv = rows.map(r => r.map(c => `"${String(c).replace(/"/g, '""')}"`).join(',')).join('\n')
  const a = document.createElement('a')
  a.href = URL.createObjectURL(new Blob([csv], { type: 'text/csv' }))
  a.download = `runs_${Date.now()}.csv`
  a.click()
}

export function RunsList() {
  const [runs, setRuns] = useState<RunSummary[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState<RunStatus | ''>('')
  const [experiment, setExperiment] = useState('')

  const load = useCallback(() => {
    setLoading(true)
    setError('')

    const params: Record<string, string> = { limit: '100' }
    if (statusFilter) params.status = statusFilter
    if (experiment) params.experiment_name = experiment

    api.runs.list(params)
      .then((res: any) => {
        console.log("API runs:", res)

        // 🔥 FIX QUAN TRỌNG
        setRuns(res?.data || [])
      })
      .catch(e => {
        console.error(e)
        setError(e.message || 'Failed to load runs')
        setRuns([])
      })
      .finally(() => setLoading(false))
  }, [statusFilter, experiment])

  useEffect(() => { load() }, [load])

  const filtered = (runs || []).filter(r =>
    !search || r.name.toLowerCase().includes(search.toLowerCase())
  )

  return (
    <div className="fade-in space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-text">Runs</h1>
          <p className="text-sm text-muted mt-0.5">{filtered.length} runs</p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => exportCSV(filtered)}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs text-muted border border-border rounded-lg hover:text-text hover:border-muted transition-all"
          >
            <Download size={13} /> Export CSV
          </button>

          <button
            onClick={load}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs text-muted border border-border rounded-lg hover:text-text hover:border-muted transition-all"
          >
            <RefreshCw size={13} className={loading ? 'animate-spin' : ''} /> Refresh
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="flex gap-3">
        <div className="flex-1 relative">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted" />
          <input
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Search by run name…"
            className="w-full pl-9 pr-4 py-2 text-sm bg-surface border border-border rounded-lg text-text placeholder-muted focus:outline-none focus:border-accent transition-colors"
          />
        </div>

        <input
          value={experiment}
          onChange={e => setExperiment(e.target.value)}
          placeholder="Experiment name"
          className="w-48 px-3 py-2 text-sm bg-surface border border-border rounded-lg text-text placeholder-muted focus:outline-none focus:border-accent transition-colors"
        />

        <select
          value={statusFilter}
          onChange={e => setStatusFilter(e.target.value as RunStatus | '')}
          className="px-3 py-2 text-sm bg-surface border border-border rounded-lg text-text focus:outline-none focus:border-accent transition-colors"
        >
          {STATUSES.map(s => (
            <option key={s} value={s}>{s || 'All statuses'}</option>
          ))}
        </select>
      </div>

      {/* Table */}
      <div className="bg-surface border border-border rounded-xl overflow-hidden">
        {loading && (
          <div className="p-8 text-center text-sm text-muted animate-pulse">
            Loading…
          </div>
        )}

        {error && (
          <div className="p-6 text-sm text-danger">
            {error}
          </div>
        )}

        {!loading && !error && (
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border">
                {['Run Name', 'Status', 'Params', 'Git', 'Data Ver', 'Created', ''].map(h => (
                  <th key={h} className="px-4 py-3 text-left text-xs font-medium text-muted">
                    {h}
                  </th>
                ))}
              </tr>
            </thead>

            <tbody>
              {filtered.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-4 py-10 text-center text-muted text-sm">
                    No runs found
                  </td>
                </tr>
              ) : (
                (filtered || []).map(run => (
                  <tr key={run.id} className="border-b border-border/50 hover:bg-white/[0.02] transition-colors group">
                    <td className="px-4 py-3">
                      <Link
                        to={`/runs/${run.id}`}
                        className="mono text-xs text-text hover:text-accent transition-colors"
                      >
                        {run.name}
                      </Link>
                      <p className="text-[10px] text-muted mt-0.5 mono">
                        {run.id.slice(0, 12)}…
                      </p>
                    </td>

                    <td className="px-4 py-3">
                      <StatusBadge status={run.status} />
                    </td>

                    <td className="px-4 py-3">
                      <div className="flex flex-wrap gap-x-2 gap-y-0.5 max-w-[200px]">
                        {Object.entries(run.params || {}).slice(0, 4).map(([k, v]) => (
                          <span key={k} className="text-xs">
                            <span className="text-accent/70">{k}</span>
                            <span className="text-border mx-0.5">=</span>
                            <span className="text-text">{String(v)}</span>
                          </span>
                        ))}
                      </div>
                    </td>

                    <td className="px-4 py-3 text-muted mono text-xs">
                      {run.git_commit?.slice(0, 7) ?? '—'}
                    </td>

                    <td className="px-4 py-3 text-muted text-xs">
                      {run.data_version ?? '—'}
                    </td>

                    <td className="px-4 py-3 text-muted text-xs">
                      {new Date(run.created_at).toLocaleDateString()}
                    </td>

                    <td className="px-4 py-3">
                      <Link
                        to={`/runs/${run.id}`}
                        className="text-xs text-muted group-hover:text-accent transition-colors opacity-0 group-hover:opacity-100"
                      >
                        View →
                      </Link>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}