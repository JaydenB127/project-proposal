import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Sidebar } from './components/Sidebar'
import { Dashboard } from './pages/Dashboard'
import { RunsList } from './pages/RunsList'
import { RunDetailPage } from './pages/RunDetail'
import { ComparePage } from './pages/Compare'
import { ChartsPage } from './pages/Charts'
import { SettingsPage } from './pages/Settings'

export default function App() {
  return (
    <BrowserRouter>
      <div className="flex h-full">
        <Sidebar />
        <main className="flex-1 overflow-y-auto grid-bg">
          <div className="max-w-6xl mx-auto px-8 py-8">
            <Routes>
              <Route path="/"         element={<Dashboard />} />
              <Route path="/runs"     element={<RunsList />} />
              <Route path="/runs/:id" element={<RunDetailPage />} />
              <Route path="/compare"  element={<ComparePage />} />
              <Route path="/charts"   element={<ChartsPage />} />
              <Route path="/settings" element={<SettingsPage />} />
            </Routes>
          </div>
        </main>
      </div>
    </BrowserRouter>
  )
}
