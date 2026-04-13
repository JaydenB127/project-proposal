import { useState } from 'react'
import { Key, CheckCircle2, Eye, EyeOff } from 'lucide-react'
import { api } from '../lib/api'

export function SettingsPage() {
  const [apiKey, setApiKey] = useState(api.getKey())
  const [saved, setSaved] = useState(false)
  const [showKey, setShowKey] = useState(false)

  // Register form
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [regResult, setRegResult] = useState<{ api_key?: string; error?: string } | null>(null)
  const [regLoading, setRegLoading] = useState(false)

  const saveKey = () => {
    api.setKey(apiKey)
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  const register = async () => {
    setRegLoading(true)
    setRegResult(null)
    try {
      const res = await api.register(username, email, password)
      setRegResult({ api_key: res.api_key })
      setApiKey(res.api_key)
      api.setKey(res.api_key)
    } catch (e: any) {
      setRegResult({ error: e.message })
    } finally {
      setRegLoading(false)
    }
  }

  return (
    <div className="fade-in space-y-8 max-w-xl">
      <div>
        <h1 className="text-xl font-semibold text-text">Settings</h1>
        <p className="text-sm text-muted mt-1">Configure your API key and account</p>
      </div>

      {/* API Key */}
      <div className="bg-surface border border-border rounded-xl p-5 space-y-4">
        <div className="flex items-center gap-2">
          <Key size={15} className="text-accent" />
          <h2 className="text-sm font-semibold text-text">API Key</h2>
        </div>
        <p className="text-xs text-muted">
          Set your API key to authenticate requests. It's stored locally in your browser.
        </p>
        <div className="flex gap-2">
          <div className="relative flex-1">
            <input
              type={showKey ? 'text' : 'password'}
              value={apiKey}
              onChange={e => setApiKey(e.target.value)}
              placeholder="Paste your API key…"
              className="w-full px-3 py-2 pr-9 text-sm bg-bg border border-border rounded-lg text-text placeholder-muted focus:outline-none focus:border-accent transition-colors mono"
            />
            <button
              onClick={() => setShowKey(v => !v)}
              className="absolute right-2.5 top-1/2 -translate-y-1/2 text-muted hover:text-text transition-colors"
            >
              {showKey ? <EyeOff size={14} /> : <Eye size={14} />}
            </button>
          </div>
          <button
            onClick={saveKey}
            className="flex items-center gap-1.5 px-4 py-2 text-sm bg-accent text-white rounded-lg hover:bg-accent/90 transition-all"
          >
            {saved ? <><CheckCircle2 size={14} /> Saved</> : 'Save'}
          </button>
        </div>
      </div>

      {/* Register */}
      <div className="bg-surface border border-border rounded-xl p-5 space-y-4">
        <h2 className="text-sm font-semibold text-text">Register New User</h2>
        <p className="text-xs text-muted">
          Create a new account. Your API key will be returned and saved automatically.
        </p>
        <div className="space-y-2.5">
          <input
            value={username}
            onChange={e => setUsername(e.target.value)}
            placeholder="Username"
            className="w-full px-3 py-2 text-sm bg-bg border border-border rounded-lg text-text placeholder-muted focus:outline-none focus:border-accent transition-colors"
          />
          <input
            value={email}
            onChange={e => setEmail(e.target.value)}
            placeholder="Email"
            type="email"
            className="w-full px-3 py-2 text-sm bg-bg border border-border rounded-lg text-text placeholder-muted focus:outline-none focus:border-accent transition-colors"
          />
          <input
            value={password}
            onChange={e => setPassword(e.target.value)}
            placeholder="Password"
            type="password"
            className="w-full px-3 py-2 text-sm bg-bg border border-border rounded-lg text-text placeholder-muted focus:outline-none focus:border-accent transition-colors"
          />
          <button
            onClick={register}
            disabled={regLoading || !username || !email || !password}
            className="w-full py-2 text-sm bg-accent text-white rounded-lg hover:bg-accent/90 disabled:opacity-40 disabled:cursor-not-allowed transition-all"
          >
            {regLoading ? 'Registering…' : 'Register'}
          </button>
        </div>
        {regResult?.api_key && (
          <div className="mt-2 p-3 bg-success/10 border border-success/30 rounded-lg">
            <p className="text-xs text-success font-medium mb-1">✓ Registered! API key saved automatically.</p>
            <p className="text-xs text-muted mono break-all">{regResult.api_key}</p>
          </div>
        )}
        {regResult?.error && (
          <p className="text-xs text-danger mt-1">{regResult.error}</p>
        )}
      </div>

      {/* API info */}
      <div className="bg-surface border border-border rounded-xl p-5 space-y-3">
        <h2 className="text-sm font-semibold text-text">API Reference</h2>
        <div className="space-y-2 text-xs">
          {[
            ['POST', '/api/v1/runs', 'Create a run'],
            ['POST', '/api/v1/runs/{id}/metrics', 'Log metrics batch'],
            ['GET',  '/api/v1/runs', 'List / filter runs'],
            ['GET',  '/api/v1/runs/{id}', 'Run detail + metrics'],
            ['GET',  '/api/v1/runs/compare', 'Compare runs'],
            ['GET',  '/api/v1/runs/chart', 'Chart data'],
            ['POST', '/api/v1/runs/{id}/finish', 'Complete a run'],
            ['GET',  '/health', 'Health check (no auth)'],
          ].map(([method, path, desc]) => (
            <div key={path} className="flex items-center gap-3">
              <span className={`w-10 text-right text-[10px] font-semibold ${method === 'POST' ? 'text-warn' : 'text-success'}`}>
                {method}
              </span>
              <span className="mono text-text">{path}</span>
              <span className="text-muted">{desc}</span>
            </div>
          ))}
        </div>
        <a
          href="/docs"
          target="_blank"
          className="inline-block text-xs text-accent hover:underline mt-1"
        >
          Open Swagger docs →
        </a>
      </div>
    </div>
  )
}
