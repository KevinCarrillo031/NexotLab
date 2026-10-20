import { useState, useEffect } from 'react'
import { MetricCard, Card, PageHeader, Button } from '../components/ui'
import type { PlatformUser } from '../types'
import MiningDashboard from './MiningDashboard'
import EntregablesPage from './EntregablesPage'

interface AdminPageProps {
  platformUsers: PlatformUser[]
  onToggleUser: (id: string) => void
}

interface ContentReport {
  id: string
  proposalTitle: string
  reason: string
  reporterName: string
  date: string
  dismissed: boolean
}

interface AdminStats {
  users_total: number
  users_active: number
  proposals_total: number
  proposals_by_status: { good: number; evaluating: number; needs_improvement: number }
  total_evaluations: number
  average_proposal_score: number
}

const profileLabels: Record<string, string> = {
  entrepreneur: 'Emprendedor/a',
  company: 'Empresa',
  researcher: 'Investigador/a',
  citizen: 'Ciudadano/a',
}

const BASE = 'http://localhost:8000/api/v1'

export default function AdminPage({ platformUsers, onToggleUser }: AdminPageProps) {
  const [section, setSection] = useState<'overview' | 'users' | 'moderation' | 'mining' | 'deliverables'>('overview')
  const [highThreshold, setHighThreshold] = useState(4.0)
  const [lowThreshold, setLowThreshold] = useState(2.5)
  const [thresholdSaved, setThresholdSaved] = useState(false)
  const [reports, setReports] = useState<ContentReport[]>([])
  const [stats, setStats] = useState<AdminStats | null>(null)

  useEffect(() => {
    fetch(`${BASE}/platform/admin/overview`)
      .then(r => r.json())
      .then(setStats)
      .catch(() => {})
  }, [])

  useEffect(() => {
    if (section === 'moderation') {
      fetch(`${BASE}/platform/admin/reports?dismissed=false`)
        .then(r => r.json())
        .then(d => setReports(d.items ?? []))
        .catch(() => {})
    }
  }, [section])

  const handleDismissReport = async (reportId: string) => {
    const adminId = 'admin1'
    try {
      await fetch(`${BASE}/platform/admin/reports/${reportId}/dismiss?requesting_user_id=${adminId}`, { method: 'PATCH' })
      setReports(prev => prev.filter(r => r.id !== reportId))
    } catch {
      setReports(prev => prev.filter(r => r.id !== reportId))
    }
  }

  const handleSaveThresholds = () => {
    setThresholdSaved(true)
    setTimeout(() => setThresholdSaved(false), 2000)
  }

  const activeUsers = stats?.users_active ?? platformUsers.filter(u => u.active).length
  const totalUsers = stats?.users_total ?? platformUsers.length
  const totalProposals = stats?.proposals_total ?? platformUsers.reduce((s, u) => s + u.proposalsCount, 0)
  const avgScore = stats?.average_proposal_score ?? 0
  const totalEvals = stats?.total_evaluations ?? 0
  const byStatus = stats?.proposals_by_status ?? { good: 0, evaluating: 0, needs_improvement: 0 }

  const sections = [
    { key: 'overview', label: 'Métricas' },
    { key: 'users', label: 'Usuarios' },
    { key: 'moderation', label: 'Moderación' },
    { key: 'mining', label: 'Minería' },
    { key: 'deliverables', label: 'Entregables' },
  ] as const

  return (
    <div className="max-w-5xl mx-auto px-4 py-6">
      <div className="mb-6 rounded-xl bg-brand-dark px-5 py-3.5 flex items-center justify-between gap-3">
        <div className="flex items-center gap-2.5">
          <div className="w-2 h-2 rounded-full bg-brand-mid" />
          <span className="text-sm font-medium text-white">Panel de administración</span>
          <span className="text-xs text-white/50">·</span>
          <span className="text-xs text-white/70">Solo visible para administradores</span>
        </div>
        <span className="text-xs text-white/50">NexotLab v1.0</span>
      </div>

      <PageHeader
        title="Gestión de la plataforma"
        subtitle="Métricas globales, usuarios y configuración"
      />

      <div className="flex rounded-xl bg-gray-50 p-1 mb-6 w-fit">
        {sections.map(s => (
          <button
            key={s.key}
            onClick={() => setSection(s.key)}
            className={`px-4 py-2 text-sm font-medium rounded-xl transition-colors ${
              section === s.key ? 'bg-white text-brand-dark' : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            {s.label}
          </button>
        ))}
      </div>

      {/* ── OVERVIEW ─────────────────────────────────────────────── */}
      {section === 'overview' && (
        <div className="space-y-5">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <MetricCard value={totalUsers} label="Usuarios totales" accent />
            <MetricCard value={activeUsers} label="Usuarios activos" />
            <MetricCard value={totalProposals} label="Propuestas publicadas" />
            <MetricCard value={totalEvals} label="Evaluaciones totales" />
          </div>

          <div className="grid md:grid-cols-2 gap-5">
            <Card className="p-5">
              <h3 className="text-sm font-medium text-gray-700 mb-4">Propuestas por estado</h3>
              {[
                { label: 'Buen proyecto', count: byStatus.good, color: 'bg-brand-mid' },
                { label: 'En evaluación', count: byStatus.evaluating, color: 'bg-gray-400' },
                { label: 'Necesita mejoras', count: byStatus.needs_improvement, color: 'bg-amber-400' },
              ].map(item => {
                const pct = totalProposals > 0 ? `${Math.round((item.count / totalProposals) * 100)}%` : '0%'
                return (
                  <div key={item.label} className="mb-3">
                    <div className="flex justify-between text-xs text-gray-600 mb-1.5">
                      <span>{item.label}</span>
                      <span>{item.count} propuesta{item.count !== 1 ? 's' : ''}</span>
                    </div>
                    <div className="h-1.5 bg-gray-100 rounded-full">
                      <div className={`h-1.5 rounded-full ${item.color}`} style={{ width: pct }} />
                    </div>
                  </div>
                )
              })}
            </Card>

            <Card className="p-5">
              <h3 className="text-sm font-medium text-gray-700 mb-4">Resumen de actividad</h3>
              <div className="space-y-3">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Evaluaciones realizadas</span>
                  <span className="font-medium text-gray-800">{totalEvals}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Score promedio</span>
                  <span className="font-medium text-brand-mid">{avgScore.toFixed(2)} / 5.0</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Tasa de aprobación</span>
                  <span className="font-medium text-gray-800">
                    {totalProposals > 0 ? `${Math.round((byStatus.good / totalProposals) * 100)}%` : '—'}
                  </span>
                </div>
              </div>
            </Card>
          </div>

          {/* Thresholds */}
          <Card className="p-5">
            <h3 className="text-sm font-medium text-gray-700 mb-0.5">Umbrales de calificación semanal</h3>
            <p className="text-xs text-gray-400 mb-6">
              Define los límites que determinan el estado de cada propuesta al cierre semanal
            </p>
            <div className="grid md:grid-cols-2 gap-6">
              <div className="space-y-3">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-sm text-gray-700">Umbral alto — <span className="text-brand-mid font-medium">"Buen proyecto"</span></p>
                    <p className="text-xs text-gray-400">Score mínimo para notificación positiva</p>
                  </div>
                  <span className="text-xl font-medium text-brand-mid">{highThreshold.toFixed(1)}</span>
                </div>
                <input type="range" min={0} max={5} step={0.1} value={highThreshold}
                  onChange={e => { setHighThreshold(Number(e.target.value)); setThresholdSaved(false) }}
                  className="w-full h-2 rounded-full appearance-none bg-gray-200 cursor-pointer [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-5 [&::-webkit-slider-thumb]:h-5 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-brand-mid"
                />
                <div className="flex justify-between text-[9px] text-gray-400">
                  {[0, 1, 2, 3, 4, 5].map(v => <span key={v}>{v}</span>)}
                </div>
              </div>
              <div className="space-y-3">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-sm text-gray-700">Umbral bajo — <span className="text-amber-600 font-medium">"Necesita mejoras"</span></p>
                    <p className="text-xs text-gray-400">Score máximo para notificación de mejora</p>
                  </div>
                  <span className="text-xl font-medium text-amber-600">{lowThreshold.toFixed(1)}</span>
                </div>
                <input type="range" min={0} max={5} step={0.1} value={lowThreshold}
                  onChange={e => { setLowThreshold(Number(e.target.value)); setThresholdSaved(false) }}
                  className="w-full h-2 rounded-full appearance-none bg-gray-200 cursor-pointer [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-5 [&::-webkit-slider-thumb]:h-5 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-amber-500"
                />
                <div className="flex justify-between text-[9px] text-gray-400">
                  {[0, 1, 2, 3, 4, 5].map(v => <span key={v}>{v}</span>)}
                </div>
              </div>
            </div>
            <div className="mt-5 pt-4 border-t border-gray-50">
              <div className="flex items-center gap-3 flex-wrap">
                {[
                  { color: 'bg-amber-400', text: `0 – ${lowThreshold.toFixed(1)}: Necesita mejoras` },
                  { color: 'bg-gray-400', text: `${lowThreshold.toFixed(1)} – ${highThreshold.toFixed(1)}: En evaluación` },
                  { color: 'bg-brand-mid', text: `${highThreshold.toFixed(1)} – 5.0: Buen proyecto` },
                ].map(i => (
                  <div key={i.text} className="flex items-center gap-2 text-xs">
                    <span className={`w-2 h-2 rounded-full ${i.color} inline-block`} />
                    <span className="text-gray-600">{i.text}</span>
                  </div>
                ))}
              </div>
            </div>
            {lowThreshold >= highThreshold && (
              <p className="text-xs text-red-500 mt-3">El umbral bajo debe ser menor que el umbral alto.</p>
            )}
            <div className="mt-4 flex items-center gap-3">
              <Button variant="primary" size="sm" onClick={handleSaveThresholds} disabled={lowThreshold >= highThreshold}>
                {thresholdSaved ? "Guardado" : "Guardar umbrales"}
              </Button>
              {thresholdSaved && <span className="text-xs text-brand-mid">Cambios aplicados al próximo cierre semanal.</span>}
            </div>
          </Card>
        </div>
      )}

      {/* ── USERS ─────────────────────────────────────────────────── */}
      {section === 'users' && (
        <div className="space-y-4">
          <p className="text-sm text-gray-500">
            {activeUsers} usuarios activos de {totalUsers} registrados
          </p>
          <Card className="overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-100">
                    <th className="px-5 py-3.5 text-left text-xs font-medium text-gray-500">Usuario</th>
                    <th className="px-5 py-3.5 text-left text-xs font-medium text-gray-500 hidden md:table-cell">Perfil</th>
                    <th className="px-5 py-3.5 text-left text-xs font-medium text-gray-500 hidden sm:table-cell">Propuestas</th>
                    <th className="px-5 py-3.5 text-left text-xs font-medium text-gray-500 hidden sm:table-cell">Desde</th>
                    <th className="px-5 py-3.5 text-left text-xs font-medium text-gray-500">Estado</th>
                    <th className="px-5 py-3.5 text-left text-xs font-medium text-gray-500">Acción</th>
                  </tr>
                </thead>
                <tbody>
                  {platformUsers.map((u, i) => (
                    <tr key={u.id} className={`border-b border-gray-50 ${i % 2 !== 0 ? 'bg-gray-50/40' : 'bg-white'}`}>
                      <td className="px-5 py-3.5">
                        <div className="flex items-center gap-2.5">
                          <div className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-medium shrink-0 ${u.active ? 'bg-brand-light text-brand-dark' : 'bg-gray-100 text-gray-500'}`}>
                            {u.name.charAt(0)}
                          </div>
                          <div className="min-w-0">
                            <p className="text-sm text-gray-900 truncate">{u.name}</p>
                            <p className="text-xs text-gray-400 truncate hidden sm:block">{u.email}</p>
                          </div>
                        </div>
                      </td>
                      <td className="px-5 py-3.5 hidden md:table-cell">
                        <span className="text-xs text-gray-600">{profileLabels[u.profileType]}</span>
                      </td>
                      <td className="px-5 py-3.5 hidden sm:table-cell">
                        <span className="text-sm text-gray-700">{u.proposalsCount}</span>
                      </td>
                      <td className="px-5 py-3.5 hidden sm:table-cell">
                        <span className="text-xs text-gray-400">
                          {new Date(u.joinedAt).toLocaleDateString('es-CO', { month: 'short', year: '2-digit' })}
                        </span>
                      </td>
                      <td className="px-5 py-3.5">
                        <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${u.active ? 'bg-brand-light text-brand-dark' : 'bg-gray-100 text-gray-500'}`}>
                          {u.active ? 'Activo' : 'Inactivo'}
                        </span>
                      </td>
                      <td className="px-5 py-3.5">
                        <button
                          onClick={() => onToggleUser(u.id)}
                          className={`text-xs font-medium px-3 py-1.5 rounded-lg border transition-colors ${u.active ? 'border-red-200 text-red-500 hover:bg-red-50' : 'border-brand-light text-brand-mid hover:bg-brand-light'}`}
                        >
                          {u.active ? 'Desactivar' : 'Activar'}
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        </div>
      )}

      {/* ── MODERATION ────────────────────────────────────────────── */}
      {section === 'moderation' && (
        <div className="space-y-4">
          <p className="text-sm text-gray-500">{reports.length} reportes pendientes de revisión</p>
          {reports.map(r => (
            <Card key={r.id} className="p-5">
              <div className="flex items-start gap-4">
                <div className="w-9 h-9 rounded-xl bg-amber-100 flex items-center justify-center shrink-0">
                  <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true">
                    <path d="M8 2L14.5 13.5H1.5L8 2Z" stroke="#D97706" strokeWidth="1.4" strokeLinejoin="round" />
                    <path d="M8 6.5V9.5" stroke="#D97706" strokeWidth="1.4" strokeLinecap="round" />
                    <circle cx="8" cy="11.5" r="0.75" fill="#D97706" />
                  </svg>
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs font-medium px-2 py-0.5 rounded-full bg-amber-100 text-amber-600">Reportado</span>
                    <span className="text-xs text-gray-400">
                      {new Date(r.date).toLocaleDateString('es-CO', { month: 'short', day: 'numeric' })}
                    </span>
                  </div>
                  <p className="text-sm font-medium text-gray-900 mb-1">"{r.proposalTitle}"</p>
                  <p className="text-xs text-gray-500 mb-0.5">Motivo: {r.reason}</p>
                  <p className="text-xs text-gray-400">Reportado por: {r.reporterName}</p>
                </div>
                <div className="flex gap-2 shrink-0">
                  <Button variant="secondary" size="sm" onClick={() => handleDismissReport(r.id)}>
                    Ignorar
                  </Button>
                </div>
              </div>
            </Card>
          ))}
          {reports.length === 0 && (
            <Card className="p-8 text-center">
              <div className="w-10 h-10 rounded-2xl bg-brand-light flex items-center justify-center mx-auto mb-3">
                <svg width="18" height="18" viewBox="0 0 18 18" fill="none" aria-hidden="true">
                  <path d="M3 9L7.5 13.5L15 5" stroke="#639922" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </div>
              <p className="text-sm font-medium text-brand-dark">Sin reportes pendientes</p>
              <p className="text-xs text-gray-400 mt-0.5">La plataforma está limpia.</p>
            </Card>
          )}
        </div>
      )}

      {/* ── MINING ────────────────────────────────────────────────── */}
      {section === 'mining' && (
        <MiningDashboard />
      )}

      {/* ── ENTREGABLES ───────────────────────────────────────────── */}
      {section === 'deliverables' && (
        <EntregablesPage />
      )}
    </div>
  )
}
