import { useEffect, useState } from 'react'
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer
} from 'recharts'
import { api } from '../lib/api'
import type { ChartData } from '../types'

interface Props {
  runIds: string[]
  metric: string
}

export function MetricChart({ runIds, metric }: Props) {
  const [data, setData] = useState<ChartData | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!runIds.length || !metric) return
    setError('')
    api.runs.chart(runIds, metric)
      .then(setData)
      .catch(e => setError(e.message))
  }, [runIds.join(','), metric])

  if (error) return <p className="text-danger text-sm">{error}</p>
  if (!data) return <p className="text-muted text-sm animate-pulse">Loading chart…</p>

  // Merge all runs into unified step-keyed rows
  const stepMap: Record<number, Record<string, number>> = {}
  for (const run of data.runs) {
    for (const pt of run.data) {
      if (!stepMap[pt.step]) stepMap[pt.step] = { step: pt.step }
      stepMap[pt.step][run.name] = pt.value
    }
  }
  const rows = Object.values(stepMap).sort((a, b) => a.step - b.step)

  return (
    <div className="w-full">
      <p className="text-xs text-muted mb-3 mono">{metric}</p>
      <ResponsiveContainer width="100%" height={240}>
        <LineChart data={rows} margin={{ top: 4, right: 16, left: -10, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1e1e2e" />
          <XAxis dataKey="step" tick={{ fill: '#6b6b8a', fontSize: 11 }} />
          <YAxis tick={{ fill: '#6b6b8a', fontSize: 11 }} />
          <Tooltip
            contentStyle={{ background: '#13131a', border: '1px solid #1e1e2e', borderRadius: 8 }}
            labelStyle={{ color: '#6b6b8a', fontSize: 11 }}
            itemStyle={{ fontSize: 12 }}
          />
          <Legend wrapperStyle={{ fontSize: 12, color: '#e2e2f0' }} />
          {data.runs.map(run => (
            <Line
              key={run.id}
              type="monotone"
              dataKey={run.name}
              stroke={run.color}
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 4 }}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
