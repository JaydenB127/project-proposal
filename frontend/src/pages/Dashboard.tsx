import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Activity, CheckCircle2, XCircle, Clock, TrendingUp } from 'lucide-react'
import { api } from '../lib/api'
import { StatusBadge } from '../components/StatusBadge'
import type { RunSummary } from '../types'

export function Dashboard() {
  const [runs, setRuns] = useState<RunSummary[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    api.runs.list({ limit: 50 })
      .then(data => setRuns(Array.isArray(data) ? data : []))
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  const stats = {
    total: runs.length,
    completed: runs.filter(r => r.status === 'completed').length,
    running: runs.filter(r => r.status === 'running').length,
    failed: runs.filter(r => r.status === 'failed').length,
  }

  const STAT_CARDS = [
    { label: 'Total Runs',  value: stats.total,     icon: Activity,      color: 'text-accent',   bg: 'bg-accent/10' },
    { label: 'Completed',   value: stats.completed, icon: CheckCircle2,  color: 'text-success',  bg: 'bg-success/10' },
    { label: 'Running',     value: stats.running,   icon: Clock,         color: 'text-warn',     bg: 'bg-warn/10' },
    { label: 'Failed',      value: stats.failed,    icon: XCircle,       color: 'text-danger',   bg: 'bg-danger/10' },
  ]

  return (
    <div className="fade-in space-y-8">
      <div>
        <h1 className="text-xl font-semibold text-text">Dashboard</h1>
        <p className="text-sm text-muted mt-1">Overview of your ML experiment runs</p>
      </div>

      {/* Stat cards */}
      <div className="grid grid-cols-4 gap-4">
        {STAT_CARDS.map(({ label, value, icon: Icon, color, bg }) => (
          <div key={label} className="bg-surface border border-border rounded-xl p-4">
            <div className={`w-9 h-9 rounded-lg ${bg} flex items-center justify-center mb-3`}>
              <Icon size={16} className={color} />
            </div>
            <p className="text-2xl font-semibold text-text">{value}</p>
            <p className="text-xs text-muted mt-0.5">{label}</p>
          </div>
        ))}
      </div>

      {/* Recent runs */}
      <div className="bg-surface border border-border rounded-xl overflow-hidden">
        <div className="px-5 py-4 border-b border-border flex items-center justify-between">
          <h2 className="text-sm font-semibold text-text">Recent Runs</h2>
          <Link to="/runs" className="text-xs text-accent hover:text-accent/80 transition-colors">
            View all →
          </Link>
        </div>

        {loading && (
          <div className="px-5 py-8 text-center text-sm text-muted animate-pulse">Loading runs…</div>
        )}
        {error && (
          <div className="px-5 py-6 text-sm text-danger">{error}</div>
        )}
        {!loading && !error && runs.length === 0 && (
          <div className="px-5 py-10 text-center">
            <TrendingUp size={32} className="text-border mx-auto mb-3" />
            <p className="text-sm text-muted">No runs yet. Start tracking with the SDK or API.</p>
            <code className="text-xs text-accent mt-2 block">POST /api/v1/runs</code>
          </div>
        )}
        {!loading && runs.length > 0 && (
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border">
                {['Name', 'Status', 'Experiment', 'Params', 'Created'].map(h => (
                  <th key={h} className="px-5 py-3 text-left text-xs font-medium text-muted">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {runs.slice(0, 10).map(run => (
                <tr key={run.id} className="border-b border-border/50 hover:bg-white/[0.02] transition-colors">
                  <td className="px-5 py-3">
                    <Link to={`/runs/${run.id}`} className="text-text hover:text-accent transition-colors mono text-xs">
                      {run.name}
                    </Link>
                  </td>
                  <td className="px-5 py-3">
                    <StatusBadge status={run.status} />
                  </td>
                  <td className="px-5 py-3 text-muted text-xs mono">
                    {run.experiment_id.slice(0, 8)}…
                  </td>
                  <td className="px-5 py-3 text-muted text-xs">
                    {Object.entries(run.params || {}).slice(0, 3).map(([k, v]) => (
                      <span key={k} className="inline-block mr-2">
                        <span className="text-accent/70">{k}</span>=<span className="text-text">{String(v)}</span>
                      </span>
                    ))}
                  </td>
                  <td className="px-5 py-3 text-muted text-xs">
                    {new Date(run.created_at).toLocaleDateString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
