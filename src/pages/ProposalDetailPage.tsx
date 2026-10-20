import { useState } from 'react'
import { Button, StatusBadge, RoleBadge, ScoreBarChart, RatingSlider, Card, Avatar } from '../components/ui'
import type { Proposal, User, NavigateFn } from '../types'

interface ProposalDetailPageProps {
  proposal: Proposal
  currentUser: User
  navigate: NavigateFn
  onApply: (id: string) => void
  applied: boolean
  onAcceptCollaborator: (proposalId: string, collaboratorId: string) => void
  onRejectCollaborator: (proposalId: string, collaboratorId: string) => void
}

const catLabels: Record<string, string> = {
  'digital-transformation': 'Transformación digital e inteligencia organizacional',
  'digital-economy': 'Economía digital, emprendimiento e innovación',
}

const statusAlerts = {
  good: {
    title: '¡Muy buen proyecto esta semana!',
    body: 'Esta propuesta superó el umbral alto de calificación. NexotLab la está monitoreando de cerca para posibles alianzas.',
    cls: 'bg-brand-light border-brand-mid/20',
    textCls: 'text-brand-dark',
  },
  'needs-improvement': {
    title: 'La propuesta necesita mejoras',
    body: 'El score no alcanzó el umbral mínimo esta semana. Revisa especialmente los criterios de innovación e impacto.',
    cls: 'bg-amber-100 border-amber-300/40',
    textCls: 'text-amber-700',
  },
  evaluating: {
    title: 'En evaluación activa',
    body: 'La comunidad está evaluando esta propuesta. Los resultados se publicarán al cierre de la semana (domingo a medianoche).',
    cls: 'bg-gray-50 border-gray-200',
    textCls: 'text-gray-600',
  },
}

export default function ProposalDetailPage({
  proposal,
  currentUser,
  navigate,
  onApply,
  applied,
  onAcceptCollaborator,
  onRejectCollaborator,
}: ProposalDetailPageProps) {
  const [ratings, setRatings] = useState({ viability: 3, innovation: 3, impact: 3, clarity: 3 })
  const [ratingSubmitted, setRatingSubmitted] = useState(false)
  const isAuthor = proposal.authorId === currentUser.id
  const alert = statusAlerts[proposal.status]
  const avgRating = ((ratings.viability + ratings.innovation + ratings.impact + ratings.clarity) / 4).toFixed(1)
  const accepted = proposal.collaborators.filter(c => c.status === 'accepted')
  const pending = proposal.collaborators.filter(c => c.status === 'pending')

  return (
    <div className="max-w-4xl mx-auto px-4 py-6">
      {/* Back */}
      <button
        onClick={() => navigate('dashboard')}
        className="flex items-center gap-1.5 text-sm text-gray-500 hover:text-brand-mid mb-6 transition-colors"
      >
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true">
          <path d="M10 3L5 8L10 13" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
        Volver al inicio
      </button>

      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center gap-2 mb-3 flex-wrap">
          <span className="text-xs text-gray-400 bg-gray-50 px-2.5 py-1 rounded-full">
            {catLabels[proposal.category]}
          </span>
          <StatusBadge status={proposal.status} />
        </div>
        <h1 className="text-xl font-medium text-gray-900 leading-snug mb-3">{proposal.title}</h1>
        <div className="flex items-center gap-3 flex-wrap text-sm text-gray-500">
          <div className="flex items-center gap-2">
            <Avatar name={proposal.authorName} size="sm" />
            <span>{proposal.authorName}</span>
            <RoleBadge profileType={proposal.authorProfile} />
          </div>
          <span className="text-gray-300">·</span>
          <span className="text-xs text-gray-400">
            {new Date(proposal.createdAt).toLocaleDateString('es-CO', { year: 'numeric', month: 'long', day: 'numeric' })}
          </span>
          <span className="text-gray-300">·</span>
          <span className="text-xs text-gray-400">{proposal.evaluationsCount} evaluaciones</span>
        </div>
      </div>

      <div className="grid md:grid-cols-3 gap-5">
        {/* Main content */}
        <div className="md:col-span-2 space-y-4">
          {/* Status alert */}
          <div className={`rounded-xl border p-4 ${alert.cls}`}>
            <p className={`text-sm font-medium mb-0.5 ${alert.textCls}`}>{alert.title}</p>
            <p className="text-xs text-gray-600 leading-relaxed">{alert.body}</p>
          </div>

          {/* Description */}
          <Card className="p-5">
            <h2 className="text-sm font-medium text-gray-700 mb-2.5">Descripción</h2>
            <p className="text-sm text-gray-600 leading-relaxed">{proposal.description}</p>
          </Card>

          {/* Deliverable */}
          <Card className="p-5">
            <h2 className="text-sm font-medium text-gray-700 mb-2.5">Producto a entregar</h2>
            <p className="text-sm text-gray-600 leading-relaxed">{proposal.deliverable}</p>
          </Card>

          {/* Score chart */}
          <Card className="p-5">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-sm font-medium text-gray-700">Evolución del score semanal</h2>
              <div className="text-right">
                <span className="text-2xl font-medium text-brand-mid">{proposal.currentScore.toFixed(1)}</span>
                <span className="text-sm text-gray-400"> / 5.0</span>
              </div>
            </div>
            <ScoreBarChart scores={proposal.weeklyScores} />
            <div className="flex items-center gap-4 mt-3 pt-3 border-t border-gray-50">
              <div className="flex items-center gap-1.5 text-xs text-gray-400">
                <span className="w-2.5 h-2.5 rounded-sm bg-brand-mid opacity-65 inline-block" />
                Semanas anteriores
              </div>
              <div className="flex items-center gap-1.5 text-xs text-gray-400">
                <span className="w-2.5 h-2.5 rounded-sm bg-brand-dark inline-block" />
                Semana actual
              </div>
            </div>
          </Card>

          {/* Rating form */}
          {!isAuthor && (
            <Card className="p-5">
              <h2 className="text-sm font-medium text-gray-700 mb-0.5">Evaluar esta propuesta</h2>
              <p className="text-xs text-gray-400 mb-5">Tu calificación es anónima y contribuye al score semanal acumulado</p>

              {ratingSubmitted ? (
                <div className="text-center py-5">
                  <div className="w-11 h-11 rounded-full bg-brand-light flex items-center justify-center mx-auto mb-3">
                    <svg width="20" height="20" viewBox="0 0 20 20" fill="none" aria-hidden="true">
                      <path d="M4 10.5L8 14.5L16 6.5" stroke="#639922" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                  </div>
                  <p className="text-sm font-medium text-brand-dark">¡Evaluación enviada!</p>
                  <p className="text-xs text-gray-500 mt-0.5">Gracias por contribuir a la comunidad NexotLab</p>
                </div>
              ) : (
                <div className="space-y-5">
                  <RatingSlider label="Viabilidad" value={ratings.viability} onChange={v => setRatings(r => ({ ...r, viability: v }))} />
                  <RatingSlider label="Innovación" value={ratings.innovation} onChange={v => setRatings(r => ({ ...r, innovation: v }))} />
                  <RatingSlider label="Impacto" value={ratings.impact} onChange={v => setRatings(r => ({ ...r, impact: v }))} />
                  <RatingSlider label="Claridad" value={ratings.clarity} onChange={v => setRatings(r => ({ ...r, clarity: v }))} />
                  <div className="flex items-center justify-between pt-1 border-t border-gray-50">
                    <span className="text-xs text-gray-500">
                      Promedio de tu evaluación: <strong className="text-brand-mid">{avgRating}</strong> / 5.0
                    </span>
                    <Button variant="primary" size="sm" onClick={() => setRatingSubmitted(true)}>
                      Enviar evaluación
                    </Button>
                  </div>
                </div>
              )}
            </Card>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-4">
          {/* Score + apply */}
          <Card className="p-5 text-center">
            <div className="text-4xl font-medium text-brand-mid leading-none">{proposal.currentScore.toFixed(1)}</div>
            <div className="text-xs text-gray-400 mt-1 mb-3">Score actual / 5.0</div>
            <div className="w-full bg-gray-100 rounded-full h-1.5 mb-4">
              <div
                className="bg-brand-mid h-1.5 rounded-full transition-all"
                style={{ width: `${(proposal.currentScore / 5) * 100}%` }}
              />
            </div>
            {!isAuthor && !applied && (
              <Button variant="primary" size="md" className="w-full" onClick={() => onApply(proposal.id)}>
                Postularme como colaborador
              </Button>
            )}
            {!isAuthor && applied && (
              <Button variant="secondary" size="md" className="w-full" disabled>
                Postulación enviada
              </Button>
            )}
            {isAuthor && (
              <Button variant="secondary" size="sm" className="w-full" onClick={() => navigate('edit-proposal', proposal.id)}>
                Editar propuesta
              </Button>
            )}
          </Card>

          {/* Collaborators */}
          <Card className="p-4">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-medium text-gray-700">Equipo</h3>
              {isAuthor && pending.length > 0 && (
                <span className="text-[10px] font-medium px-2 py-0.5 rounded-full bg-amber-100 text-amber-600">
                  {pending.length} pendiente{pending.length > 1 ? 's' : ''}
                </span>
              )}
            </div>

            {proposal.collaborators.length === 0 && (
              <p className="text-xs text-gray-400 py-1">Sin colaboradores aún.</p>
            )}

            <div className="space-y-3">
              {accepted.map(c => (
                <div key={c.id} className="flex items-center justify-between gap-2">
                  <div className="flex items-center gap-2 min-w-0">
                    <Avatar name={c.name} size="sm" />
                    <div className="min-w-0">
                      <p className="text-xs font-medium text-gray-800 truncate">{c.name}</p>
                      <RoleBadge profileType={c.profileType} />
                    </div>
                  </div>
                  <span className="text-[10px] text-brand-mid shrink-0">Activo</span>
                </div>
              ))}

              {isAuthor && pending.length > 0 && (
                <>
                  <div className="border-t border-gray-50 pt-2">
                    <p className="text-[10px] text-gray-400 mb-2">Postulaciones pendientes</p>
                  </div>
                  {pending.map(c => (
                    <div key={c.id} className="flex items-center justify-between gap-2">
                      <div className="flex items-center gap-2 min-w-0">
                        <Avatar name={c.name} size="sm" />
                        <div className="min-w-0">
                          <p className="text-xs font-medium text-gray-700 truncate">{c.name}</p>
                          <RoleBadge profileType={c.profileType} />
                        </div>
                      </div>
                      <div className="flex gap-1 shrink-0">
                        <button
                          onClick={() => onAcceptCollaborator(proposal.id, c.id)}
                          className="w-6 h-6 rounded-lg bg-brand-light text-brand-mid flex items-center justify-center hover:bg-brand-mid hover:text-white transition-colors"
                          title="Aceptar"
                        >
                          <svg width="10" height="10" viewBox="0 0 10 10" fill="none" aria-hidden="true">
                            <path d="M1.5 5L4 7.5L8.5 2" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round" strokeLinejoin="round" />
                          </svg>
                        </button>
                        <button
                          onClick={() => onRejectCollaborator(proposal.id, c.id)}
                          className="w-6 h-6 rounded-lg bg-red-50 text-red-400 flex items-center justify-center hover:bg-red-500 hover:text-white transition-colors"
                          title="Rechazar"
                        >
                          <svg width="10" height="10" viewBox="0 0 10 10" fill="none" aria-hidden="true">
                            <path d="M2 2L8 8M8 2L2 8" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round" />
                          </svg>
                        </button>
                      </div>
                    </div>
                  ))}
                </>
              )}

              {!isAuthor && pending.filter(c => c.id === currentUser.id).length > 0 && (
                <div className="border-t border-gray-50 pt-2">
                  <p className="text-[10px] text-gray-400">Tu postulación está pendiente de revisión.</p>
                </div>
              )}
            </div>
          </Card>
        </div>
      </div>
    </div>
  )
}
