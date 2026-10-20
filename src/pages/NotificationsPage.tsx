import { useState } from 'react'
import { NotificationIcon, Button, PageHeader } from '../components/ui'
import type { AppNotification, NotificationType, NavigateFn } from '../types'

interface NotificationsPageProps {
  notifications: AppNotification[]
  navigate: NavigateFn
  onMarkRead: (id: string) => void
  onMarkAllRead: () => void
}

const typeLabels: Record<NotificationType, string> = {
  positive: 'Calificación destacada',
  improvement: 'Oportunidad de mejora',
  social: 'Actividad en tu equipo',
}

const typeColors: Record<NotificationType, string> = {
  positive: 'text-brand-mid',
  improvement: 'text-amber-600',
  social: 'text-gray-500',
}

export default function NotificationsPage({ notifications, navigate, onMarkRead, onMarkAllRead }: NotificationsPageProps) {
  const [filter, setFilter] = useState<'all' | NotificationType>('all')
  const unread = notifications.filter(n => !n.read).length

  const filtered = filter === 'all' ? notifications : notifications.filter(n => n.type === filter)

  return (
    <div className="max-w-2xl mx-auto px-4 py-6">
      <PageHeader
        title="Notificaciones"
        subtitle={unread > 0 ? `${unread} sin leer` : 'Estás al día'}
        action={
          unread > 0 ? (
            <Button variant="ghost" size="sm" onClick={onMarkAllRead}>
              Marcar todas como leídas
            </Button>
          ) : undefined
        }
      />

      {/* Filter tabs */}
      <div className="flex gap-1.5 mb-5 flex-wrap">
        {([
          { value: 'all', label: 'Todas' },
          { value: 'positive', label: 'Destacadas' },
          { value: 'improvement', label: 'Mejoras' },
          { value: 'social', label: 'Sociales' },
        ] as const).map(f => (
          <button
            key={f.value}
            onClick={() => setFilter(f.value)}
            className={`text-xs px-3 py-1.5 rounded-full border transition-colors ${
              filter === f.value
                ? 'bg-brand-dark text-white border-brand-dark'
                : 'border-gray-200 text-gray-500 hover:border-brand-mid hover:text-brand-mid'
            }`}
          >
            {f.label}
          </button>
        ))}
      </div>

      {filtered.length === 0 ? (
        <div className="text-center py-16">
          <div className="w-12 h-12 rounded-2xl bg-gray-50 flex items-center justify-center mx-auto mb-3">
            <svg width="22" height="22" viewBox="0 0 22 22" fill="none" aria-hidden="true">
              <path d="M11 2.5C7.686 2.5 5 5.186 5 8.5v5L3 16h16l-2-2.5V8.5c0-3.314-2.686-6-6-6Z" stroke="#9CA3AF" strokeWidth="1.3" strokeLinejoin="round" />
              <path d="M9 16c0 1.105.895 2 2 2s2-.895 2-2" stroke="#9CA3AF" strokeWidth="1.3" strokeLinecap="round" />
            </svg>
          </div>
          <p className="text-sm text-gray-400">Sin notificaciones en esta categoría.</p>
        </div>
      ) : (
        <div className="space-y-2">
          {filtered.map(n => (
            <button
              key={n.id}
              className={`w-full text-left rounded-xl border p-4 flex items-start gap-3 transition-colors ${
                !n.read
                  ? 'bg-white border-gray-100 hover:border-brand-light'
                  : 'bg-gray-50/80 border-gray-100 opacity-65 hover:opacity-90 hover:border-gray-200'
              }`}
              onClick={() => onMarkRead(n.id)}
            >
              <NotificationIcon type={n.type} />
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-0.5">
                  <span className={`text-xs font-medium ${typeColors[n.type]}`}>
                    {typeLabels[n.type]}
                  </span>
                  {!n.read && (
                    <span className="w-1.5 h-1.5 rounded-full bg-brand-mid shrink-0" />
                  )}
                </div>
                <p className="text-sm text-gray-700 leading-snug">{n.message}</p>
                {n.proposalTitle && (
                  <p className="text-xs text-gray-400 mt-1 truncate">
                    Propuesta: "{n.proposalTitle}"
                  </p>
                )}
              </div>
              <div className="shrink-0 text-right">
                <span className="text-xs text-gray-400">
                  {new Date(n.date).toLocaleDateString('es-CO', { month: 'short', day: 'numeric' })}
                </span>
              </div>
            </button>
          ))}
        </div>
      )}

      {unread === 0 && notifications.length > 0 && (
        <p className="text-center text-xs text-gray-400 mt-6">
          Todas las notificaciones han sido leídas.
        </p>
      )}
    </div>
  )
}
