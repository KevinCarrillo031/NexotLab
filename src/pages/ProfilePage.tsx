import { StatusBadge, RoleBadge, Card, PageHeader, MetricCard, Avatar } from '../components/ui'
import type { User, Proposal, NavigateFn } from '../types'

interface ProfilePageProps {
  user: User
  proposals: Proposal[]
  navigate: NavigateFn
}

const catLabels: Record<string, string> = {
  'digital-transformation': 'Transformación digital',
  'digital-economy': 'Economía digital',
}

const profileDescriptions: Record<string, string> = {
  entrepreneur: 'Construye soluciones innovadoras desde la base',
  company: 'Impulsa la transformación desde la industria',
  researcher: 'Genera conocimiento que transforma realidades',
  citizen: 'Participa y co-crea para tu comunidad',
}

export default function ProfilePage({ user, proposals, navigate }: ProfilePageProps) {
  const myProposals = proposals.filter(p => p.authorId === user.id)
  const goodCount = myProposals.filter(p => p.status === 'good').length
  const avgScore = myProposals.length
    ? (myProposals.reduce((s, p) => s + p.currentScore, 0) / myProposals.length).toFixed(1)
    : '–'

  return (
    <div className="max-w-3xl mx-auto px-4 py-6">
      <PageHeader title="Mi perfil" />

      {/* Profile header card */}
      <Card className="p-6 mb-5">
        <div className="flex items-start gap-5">
          <Avatar name={user.name} size="lg" />
          <div className="flex-1 min-w-0">
            <div className="flex items-start justify-between gap-2 flex-wrap">
              <div>
                <h2 className="text-lg font-medium text-gray-900">{user.name}</h2>
                <p className="text-xs text-gray-500 mt-0.5">{profileDescriptions[user.profileType]}</p>
              </div>
              <RoleBadge profileType={user.profileType} />
            </div>
            <div className="mt-3 flex items-center gap-4 flex-wrap">
              <div className="flex items-center gap-1.5 text-sm text-gray-500">
                <svg width="14" height="14" viewBox="0 0 14 14" fill="none" aria-hidden="true">
                  <path d="M1 12l.5-2L9 2.5l2 2L3 12.5 1 12Z" stroke="#9CA3AF" strokeWidth="1.2" strokeLinejoin="round" />
                </svg>
                {user.email}
              </div>
              <div className="flex items-center gap-1.5 text-sm text-gray-500">
                <svg width="14" height="14" viewBox="0 0 14 14" fill="none" aria-hidden="true">
                  <rect x="1" y="2.5" width="12" height="10" rx="1.5" stroke="#9CA3AF" strokeWidth="1.2" />
                  <path d="M4.5 1v3M9.5 1v3M1 6.5h12" stroke="#9CA3AF" strokeWidth="1.2" strokeLinecap="round" />
                </svg>
                Miembro desde {new Date(user.joinedAt).toLocaleDateString('es-CO', { month: 'long', year: 'numeric' })}
              </div>
            </div>
          </div>
        </div>
      </Card>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
        <MetricCard value={myProposals.length} label="Propuestas creadas" accent />
        <MetricCard value={12} label="Evaluaciones enviadas" />
        <MetricCard value={avgScore} label="Score promedio" subtitle="Mis propuestas" />
        <MetricCard value={goodCount} label="Con calificación alta" />
      </div>

      {/* Proposals history */}
      <div>
        <h2 className="text-base font-medium text-gray-700 mb-3">Historial de propuestas</h2>
        {myProposals.length === 0 ? (
          <Card className="p-8 text-center">
            <p className="text-sm text-gray-400">Aún no has publicado propuestas.</p>
            <p className="text-xs text-gray-400 mt-1">Comparte tu primera idea con la comunidad.</p>
          </Card>
        ) : (
          <div className="space-y-2">
            {myProposals.map(p => (
              <button key={p.id} className="w-full text-left" onClick={() => navigate('proposal-detail', p.id)}>
                <Card className="p-4 hover:border-brand-light transition-colors">
                  <div className="flex items-center gap-4">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1 flex-wrap">
                        <span className="text-[11px] text-gray-400 bg-gray-50 px-2 py-0.5 rounded-full">
                          {catLabels[p.category]}
                        </span>
                      </div>
                      <p className="text-sm font-medium text-gray-900 truncate">{p.title}</p>
                      <p className="text-xs text-gray-400 mt-0.5">
                        {p.evaluationsCount} evaluaciones · {p.collaborators.filter(c => c.status === 'accepted').length} colaboradores
                      </p>
                    </div>
                    <div className="shrink-0 flex items-center gap-3">
                      <div className="text-right">
                        <div className="text-lg font-medium text-brand-mid leading-none">{p.currentScore.toFixed(1)}</div>
                        <div className="text-[10px] text-gray-400">/ 5.0</div>
                      </div>
                      <StatusBadge status={p.status} />
                    </div>
                  </div>
                </Card>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Activity summary */}
      <div className="mt-6">
        <h2 className="text-base font-medium text-gray-700 mb-3">Actividad reciente</h2>
        <Card className="p-4">
          {[
            { action: 'Evaluaste la propuesta "Marketplace de servicios para microempresarios rurales"', date: '2026-09-10' },
            { action: 'Publicaste "Sistema de trazabilidad agrícola con blockchain"', date: '2026-09-08' },
            { action: 'Evaluaste la propuesta "Red de innovación ciudadana para movilidad sostenible"', date: '2026-09-05' },
            { action: 'Evaluaste la propuesta "Asistente de IA para diagnóstico de suelos"', date: '2026-09-03' },
          ].map((item, i) => (
            <div key={i} className={`flex items-start gap-3 py-3 ${i > 0 ? 'border-t border-gray-50' : ''}`}>
              <div className="w-1.5 h-1.5 rounded-full bg-brand-mid mt-1.5 shrink-0" />
              <div className="flex-1 min-w-0">
                <p className="text-xs text-gray-600 leading-snug">{item.action}</p>
              </div>
              <span className="text-[10px] text-gray-400 shrink-0">
                {new Date(item.date).toLocaleDateString('es-CO', { month: 'short', day: 'numeric' })}
              </span>
            </div>
          ))}
        </Card>
      </div>
    </div>
  )
}
