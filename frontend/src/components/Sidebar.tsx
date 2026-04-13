import { NavLink } from 'react-router-dom'
import { FlaskConical, BarChart2, GitCompare, Settings, Activity } from 'lucide-react'
import clsx from 'clsx'

const NAV = [
  { to: '/',        icon: Activity,    label: 'Dashboard' },
  { to: '/runs',    icon: FlaskConical, label: 'Runs' },
  { to: '/compare', icon: GitCompare,  label: 'Compare' },
  { to: '/charts',  icon: BarChart2,   label: 'Charts' },
  { to: '/settings',icon: Settings,    label: 'Settings' },
]

export function Sidebar() {
  return (
    <aside className="w-52 flex-shrink-0 flex flex-col border-r border-border bg-surface">
      {/* Logo */}
      <div className="px-5 py-5 border-b border-border">
        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 rounded-lg bg-accent/20 border border-accent/40 flex items-center justify-center">
            <FlaskConical size={14} className="text-accent" />
          </div>
          <div>
            <p className="text-sm font-semibold text-text leading-none">ExpTracker</p>
            <p className="text-[10px] text-muted mt-0.5">ML Experiment Log</p>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 space-y-0.5">
        {NAV.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) => clsx(
              'flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-all duration-150',
              isActive
                ? 'bg-accent/15 text-accent font-medium'
                : 'text-muted hover:text-text hover:bg-white/5'
            )}
          >
            <Icon size={15} />
            {label}
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div className="px-5 py-4 border-t border-border">
        <p className="text-[10px] text-muted mono">v0.1.0 · Phase 1 MVP</p>
      </div>
    </aside>
  )
}
