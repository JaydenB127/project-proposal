import type { RunStatus } from '../types'

const STATUS_CONFIG: Record<RunStatus, { label: string; dot: string; bg: string; text: string }> = {
  created:   { label: 'Created',   dot: 'bg-blue-400',   bg: 'bg-blue-500/10',   text: 'text-blue-300' },
  running:   { label: 'Running',   dot: 'bg-yellow-400', bg: 'bg-yellow-500/10', text: 'text-yellow-300' },
  completed: { label: 'Completed', dot: 'bg-emerald-400', bg: 'bg-emerald-500/10', text: 'text-emerald-300' },
  failed:    { label: 'Failed',    dot: 'bg-red-400',    bg: 'bg-red-500/10',    text: 'text-red-300' },
  paused:    { label: 'Paused',    dot: 'bg-purple-400', bg: 'bg-purple-500/10', text: 'text-purple-300' },
}

export function StatusBadge({ status }: { status: RunStatus }) {
  const c = STATUS_CONFIG[status] ?? STATUS_CONFIG.created
  return (
    <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs font-medium ${c.bg} ${c.text}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${c.dot} ${status === 'running' ? 'pulse-dot' : ''}`} />
      {c.label}
    </span>
  )
}
