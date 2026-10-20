import { useState } from 'react'
import { StatusBadge, RoleBadge, Card, PageHeader } from '../components/ui'
import type { Proposal, User, NavigateFn } from '../types'

interface MyTeamsPageProps {
  user: User
  proposals: Proposal[]
  navigate: NavigateFn
}

const catLabels: Record<string, string> = {
  'digital-transformation': 'Transformación digital',
  'digital-economy': 'Economía digital',
}

export default function MyTeamsPage({ user, proposals, navigate }: MyTeamsPageProps) {
  const [tab, setTab] = useState<'my' | 'collaborating'>('my')

  const myProposals = proposals.filter(p => p.authorId === user.id)
  const collaborating = proposals.filter(p =>
    p.collaborators.some(c => c.id === user.id && c.status === 'accepted')
  )
  const list = tab === 'my' ? myProposals : collaborating

  return (
    <div className="max-w-3xl mx-auto px-4 py-6">
      <PageHeader title="Mis equipos" subtitle="Propuestas propias y colaboraciones activas" />

      {/* Tabs */}
      <div className="flex rounded-xl bg-gray-50 p-1 mb-6 w-fit">
        {([
          { key: 'my', label: 'Mis propuestas', count: myProposals.length },
          { key: 'collaborating', label: 'Colaborando', count: collaborating.length },
        ] as const).map(t => (
          <button
            key={t.key}
            onClick={() => setTab(t.key)}
            className={`px-4 py-2 text-sm font-medium rounded-xl transition-colors flex items-center gap-2 ${
              tab === t.key ? 'bg-white text-brand-dark' : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            {t.label}
            <span className={`text-xs px-1.5 py-0.5 rounded-full ${
              tab === t.key ? 'bg-brand-light text-brand-mid' : 'bg-gray-200 text-gray-500'
            }`}>
              {t.count}
            </span>
          </button>
        ))}
      </div>

      {list.length === 0 ? (
        <div className="text-center py-16">
          <div className="w-12 h-12 rounded-2xl bg-gray-50 flex items-center justify-center mx-auto mb-3">
            <svg width="22" height="22" viewBox="0 0 22 22" fill="none" aria-hidden="true">
              <circle cx="7" cy="7" r="3" stroke="#9CA3AF" strokeWidth="1.3" />
              <circle cx="15" cy="7" r="2.5" stroke="#9CA3AF" strokeWidth="1.3" />
              <path d="M1 18c0-3.314 2.686-6 6-6s6 2.686 6 6" stroke="#9CA3AF" strokeWidth="1.3" strokeLinecap="round" />
              <path d="M15 12c2.209 0 4 1.791 4 4" stroke="#9CA3AF" strokeWidth="1.3" strokeLinecap="round" />
            </svg>
          </div>
          <p className="text-sm text-gray-400">
            {tab === 'my'
              ? 'Aún no has publicado propuestas.'
              : 'Aún no colaboras en ninguna propuesta.'}
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {list.map(p => {
            const pendingCount = p.collaborators.filter(c => c.status === 'pending').length
            return (
              <button key={p.id} className="w-full text-left" onClick={() => navigate('proposal-detail', p.id)}>
                <Card className="p-5 hover:border-brand-light transition-colors">
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-2 flex-wrap">
                        <span className="text-[11px] text-gray-400 bg-gray-50 px-2 py-0.5 rounded-full">
                          {catLabels[p.category]}
                        </span>
                        <StatusBadge status={p.status} />
                      </div>
                      <h3 className="text-sm font-medium text-gray-900 leading-snug">{p.title}</h3>
                      {tab === 'collaborating' && (
                        <p className="text-xs text-gray-400 mt-1">Autor: {p.authorName}</p>
                      )}
                    </div>
                    <div className="shrink-0 text-right">
                      <div className="text-xl font-medium text-brand-mid leading-none">{p.currentScore.toFixed(1)}</div>
                      <div className="text-[10px] text-gray-400 mt-0.5">/ 5.0</div>
                    </div>
                  </div>

                  {/* Mini score bar */}
                  <div className="mt-3 mb-3">
                    <div className="w-full bg-gray-100 rounded-full h-1">
                      <div
                        className="bg-brand-mid h-1 rounded-full transition-all"
                        style={{ width: `${(p.currentScore / 5) * 100}%` }}
                      />
                    </div>
                  </div>

                  <div className="flex items-center gap-4 text-[11px] text-gray-400">
                    <span>{p.collaborators.filter(c => c.status === 'accepted').length} colaboradores</span>
                    <span>{p.evaluationsCount} evaluaciones</span>
                    {tab === 'my' && pendingCount > 0 && (
                      <span className="text-amber-600">
                        {pendingCount} postulación{pendingCount > 1 ? 'es' : ''} pendiente{pendingCount > 1 ? 's' : ''}
                      </span>
                    )}
                    <span className="ml-auto flex items-center gap-1 text-brand-mid">
                      Ver detalle
                      <svg width="12" height="12" viewBox="0 0 12 12" fill="none" aria-hidden="true">
                        <path d="M4.5 2.5L8 6L4.5 9.5" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round" />
                      </svg>
                    </span>
                  </div>
                </Card>
              </button>
            )
          })}
        </div>
      )}

      {/* Team members summary */}
      {tab === 'my' && myProposals.length > 0 && (
        <div className="mt-8">
          <h2 className="text-sm font-medium text-gray-700 mb-3">Colaboradores en tus propuestas</h2>
          <div className="space-y-2">
            {myProposals.flatMap(p =>
              p.collaborators.filter(c => c.status === 'accepted').map(c => ({ ...c, proposalTitle: p.title }))
            ).map((c, i) => (
              <Card key={i} className="p-3.5 flex items-center gap-3">
                <div className="w-8 h-8 rounded-full bg-brand-light flex items-center justify-center text-xs font-medium text-brand-dark shrink-0">
                  {c.name.charAt(0)}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-800">{c.name}</p>
                  <p className="text-xs text-gray-400 truncate">{c.proposalTitle}</p>
                </div>
                <RoleBadge profileType={c.profileType} />
              </Card>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
