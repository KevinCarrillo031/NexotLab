import { StatusBadge, RoleBadge, Button, Avatar } from './ui'
import type { Proposal, NavigateFn } from '../types'

const catLabels: Record<string, string> = {
  'digital-transformation': 'Transformación digital',
  'digital-economy': 'Economía digital',
}

interface ProposalCardProps {
  proposal: Proposal
  navigate: NavigateFn
  onApply?: (id: string) => void
  applied?: boolean
  showApply?: boolean
}

export default function ProposalCard({ proposal, navigate, onApply, applied = false, showApply = true }: ProposalCardProps) {
  return (
    <div className="bg-white rounded-xl border border-gray-100 p-5 hover:border-brand-light transition-colors">
      <div className="flex items-start justify-between gap-3 mb-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-2 flex-wrap">
            <span className="text-[11px] text-gray-400 bg-gray-50 px-2 py-0.5 rounded-full">
              {catLabels[proposal.category]}
            </span>
            <StatusBadge status={proposal.status} />
          </div>
          <h3 className="text-sm font-medium text-gray-900 leading-snug line-clamp-2">
            {proposal.title}
          </h3>
        </div>
        <div className="shrink-0 text-right">
          <div className="text-xl font-medium text-brand-mid leading-none">{proposal.currentScore.toFixed(1)}</div>
          <div className="text-[10px] text-gray-400 mt-0.5">/ 5.0</div>
        </div>
      </div>

      <p className="text-xs text-gray-500 line-clamp-2 mb-4 leading-relaxed">{proposal.description}</p>

      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-1.5 min-w-0">
          <Avatar name={proposal.authorName} size="sm" />
          <span className="text-xs text-gray-500 truncate">{proposal.authorName}</span>
          <RoleBadge profileType={proposal.authorProfile} />
        </div>
        <div className="flex items-center gap-1.5 shrink-0">
          <Button variant="ghost" size="sm" onClick={() => navigate('proposal-detail', proposal.id)}>
            Ver detalle
          </Button>
          {showApply && (
            <Button
              variant={applied ? 'secondary' : 'primary'}
              size="sm"
              onClick={() => onApply?.(proposal.id)}
              disabled={applied}
            >
              {applied ? 'Postulado' : 'Postularme'}
            </Button>
          )}
        </div>
      </div>

      <div className="mt-3 pt-3 border-t border-gray-50 flex items-center gap-4 text-[11px] text-gray-400">
        <span>{proposal.evaluationsCount} evaluaciones</span>
        <span>{proposal.collaborators.filter(c => c.status === 'accepted').length} colaboradores</span>
        <span>{new Date(proposal.createdAt).toLocaleDateString('es-CO', { month: 'short', day: 'numeric' })}</span>
      </div>
    </div>
  )
}
