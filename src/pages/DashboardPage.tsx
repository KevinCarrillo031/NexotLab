import { useState } from 'react'
import ProposalCard from '../components/ProposalCard'
import { MetricCard, Button } from '../components/ui'
import type { Proposal, User, NavigateFn, ProposalStatus, ProposalCategory } from '../types'

interface DashboardPageProps {
  user: User
  proposals: Proposal[]
  navigate: NavigateFn
  appliedIds: string[]
  onApply: (id: string) => void
}

export default function DashboardPage({ user, proposals, navigate, appliedIds, onApply }: DashboardPageProps) {
  const [statusFilter, setStatusFilter] = useState<'all' | ProposalStatus>('all')
  const [catFilter, setCatFilter] = useState<'all' | ProposalCategory>('all')

  const myProposals = proposals.filter(p => p.authorId === user.id)
  const myCollabs = proposals.filter(p => p.collaborators.some(c => c.id === user.id && c.status === 'accepted'))
  const weeklyAvg = myProposals.length
    ? (myProposals.reduce((s, p) => s + p.currentScore, 0) / myProposals.length).toFixed(1)
    : '–'

  const filtered = proposals.filter(p => {
    if (statusFilter !== 'all' && p.status !== statusFilter) return false
    if (catFilter !== 'all' && p.category !== catFilter) return false
    return true
  })

  const statusFilters: { value: 'all' | ProposalStatus; label: string }[] = [
    { value: 'all', label: 'Todos' },
    { value: 'good', label: 'Buen proyecto' },
    { value: 'evaluating', label: 'En evaluación' },
    { value: 'needs-improvement', label: 'Necesita mejoras' },
  ]

  const catFilters: { value: 'all' | ProposalCategory; label: string }[] = [
    { value: 'all', label: 'Todas las categorías' },
    { value: 'digital-transformation', label: 'Transformación digital' },
    { value: 'digital-economy', label: 'Economía digital' },
  ]

  const hour = new Date().getHours()
  const greeting = hour < 12 ? 'Buenos días' : hour < 18 ? 'Buenas tardes' : 'Buenas noches'

  // Calcula el rango de la semana actual (lunes a domingo) y días para el cierre
  const weekLabel = (() => {
    const now = new Date()
    const day = now.getDay() // 0=dom, 1=lun ... 6=sab
    const diffToMonday = (day === 0 ? -6 : 1 - day)
    const monday = new Date(now)
    monday.setDate(now.getDate() + diffToMonday)
    monday.setHours(0, 0, 0, 0)
    const sunday = new Date(monday)
    sunday.setDate(monday.getDate() + 6)
    sunday.setHours(23, 59, 59, 999)

    const meses = ['enero','febrero','marzo','abril','mayo','junio','julio','agosto','septiembre','octubre','noviembre','diciembre']
    const diaLunes = monday.getDate()
    const diaDomingo = sunday.getDate()
    const mesLunes = meses[monday.getMonth()]
    const mesDomingo = meses[sunday.getMonth()]

    const rango = monday.getMonth() === sunday.getMonth()
      ? `${diaLunes} al ${diaDomingo} de ${mesLunes}`
      : `${diaLunes} de ${mesLunes} al ${diaDomingo} de ${mesDomingo}`

    // días restantes hasta el domingo a medianoche
    const msRestantes = sunday.getTime() - now.getTime()
    const diasRestantes = Math.ceil(msRestantes / (1000 * 60 * 60 * 24))
    const cierreTexto = diasRestantes <= 0
      ? 'Cierre hoy'
      : diasRestantes === 1
      ? 'Cierre mañana'
      : `Cierre en ${diasRestantes} días`

    return `Semana del ${rango} · ${cierreTexto}`
  })()

  return (
    <div className="max-w-5xl mx-auto px-4 py-6">
      {/* Greeting */}
      <div className="mb-7">
        <h1 className="text-xl font-medium text-brand-dark">
          {greeting}, {user.name.split(' ')[0]}
        </h1>
        <p className="text-sm text-gray-500 mt-0.5">
          {weekLabel}
        </p>
      </div>

      {/* Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-8">
        <MetricCard value={myProposals.length} label="Mis propuestas" accent />
        <MetricCard value={myCollabs.length} label="Colaboraciones activas" />
        <MetricCard value={weeklyAvg} label="Score promedio" subtitle="Esta semana" />
        <MetricCard value={proposals.length} label="Propuestas en plataforma" />
      </div>

      {/* Feed header */}
      <div className="flex items-center justify-between mb-5 flex-wrap gap-3">
        <h2 className="text-base font-medium text-gray-800">Propuestas de la comunidad</h2>
        <Button variant="primary" size="sm" onClick={() => navigate('create-proposal')}>
          + Nueva propuesta
        </Button>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-1.5 mb-5">
        {statusFilters.map(f => (
          <button
            key={f.value}
            onClick={() => setStatusFilter(f.value)}
            className={`text-xs px-3 py-1.5 rounded-full border transition-colors ${
              statusFilter === f.value
                ? 'bg-brand-dark text-white border-brand-dark'
                : 'border-gray-200 text-gray-500 hover:border-brand-mid hover:text-brand-mid'
            }`}
          >
            {f.label}
          </button>
        ))}
        <div className="w-px bg-gray-200 mx-0.5 self-stretch" />
        {catFilters.map(f => (
          <button
            key={f.value}
            onClick={() => setCatFilter(f.value)}
            className={`text-xs px-3 py-1.5 rounded-full border transition-colors ${
              catFilter === f.value
                ? 'bg-gray-800 text-white border-gray-800'
                : 'border-gray-200 text-gray-500 hover:border-gray-400'
            }`}
          >
            {f.label}
          </button>
        ))}
      </div>

      {/* Grid */}
      <div className="grid md:grid-cols-2 gap-4">
        {filtered.map(p => (
          <ProposalCard
            key={p.id}
            proposal={p}
            navigate={navigate}
            onApply={onApply}
            applied={appliedIds.includes(p.id)}
            showApply={p.authorId !== user.id}
          />
        ))}
        {filtered.length === 0 && (
          <div className="md:col-span-2 text-center py-16">
            <p className="text-sm text-gray-400">No hay propuestas que coincidan con los filtros seleccionados.</p>
          </div>
        )}
      </div>
    </div>
  )
}
