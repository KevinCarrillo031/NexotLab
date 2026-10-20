import { useState } from 'react'
import Logo from './Logo'
import type { User, Screen, NavigateFn } from '../types'

interface NavbarProps {
  user: User
  currentScreen: Screen
  navigate: NavigateFn
  unreadCount: number
  onLogout: () => void
}

const userNav: { screen: Screen; label: string }[] = [
  { screen: 'dashboard', label: 'Inicio' },
  { screen: 'my-teams', label: 'Mis equipos' },
  { screen: 'notifications', label: 'Notificaciones' },
  { screen: 'profile', label: 'Perfil' },
]

const adminNav: { screen: Screen; label: string }[] = [
  { screen: 'admin', label: 'Panel' },
]

export default function Navbar({ user, currentScreen, navigate, unreadCount, onLogout }: NavbarProps) {
  const [open, setOpen] = useState(false)
  const items = user.isAdmin ? adminNav : userNav

  const goTo = (screen: Screen) => {
    navigate(screen)
    setOpen(false)
  }

  return (
    <nav className="bg-white border-b border-gray-100 sticky top-0 z-40">
      <div className="max-w-5xl mx-auto px-4 h-14 flex items-center justify-between">
        <button onClick={() => goTo(user.isAdmin ? 'admin' : 'dashboard')} className="flex items-center">
          <Logo size="sm" />
        </button>

        {/* Desktop */}
        <div className="hidden md:flex items-center gap-0.5">
          {items.map(item => (
            <button
              key={item.screen}
              onClick={() => goTo(item.screen)}
              className={`relative px-3.5 py-2 rounded-xl text-sm font-medium transition-colors ${
                currentScreen === item.screen
                  ? 'bg-brand-light text-brand-dark'
                  : 'text-gray-500 hover:text-gray-800 hover:bg-gray-50'
              }`}
            >
              {item.label}
              {item.screen === 'notifications' && unreadCount > 0 && (
                <span className="absolute top-1.5 right-1.5 w-1.5 h-1.5 rounded-full bg-brand-mid" />
              )}
            </button>
          ))}
          {!user.isAdmin && (
            <button
              onClick={() => goTo('create-proposal')}
              className="ml-2 bg-brand-mid text-white rounded-xl px-4 py-2 text-sm font-medium hover:bg-brand-dark transition-colors"
            >
              + Nueva propuesta
            </button>
          )}
          <div className="ml-3 pl-3 border-l border-gray-100 flex items-center gap-2">
            <div className="w-7 h-7 rounded-full bg-brand-light flex items-center justify-center text-xs font-medium text-brand-dark">
              {user.name.charAt(0)}
            </div>
            <button
              onClick={onLogout}
              className="text-xs text-gray-400 hover:text-gray-600 transition-colors"
            >
              Salir
            </button>
          </div>
        </div>

        {/* Mobile hamburger */}
        <div className="md:hidden flex items-center gap-2">
          {!user.isAdmin && unreadCount > 0 && (
            <span className="w-2 h-2 rounded-full bg-brand-mid" />
          )}
          <button
            className="p-2 rounded-xl hover:bg-gray-50 transition-colors"
            onClick={() => setOpen(!open)}
            aria-label="Menú"
          >
            {open ? (
              <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
                <path d="M4 4L14 14M14 4L4 14" stroke="#374151" strokeWidth="1.5" strokeLinecap="round" />
              </svg>
            ) : (
              <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
                <path d="M2 4.5H16M2 9H16M2 13.5H16" stroke="#374151" strokeWidth="1.5" strokeLinecap="round" />
              </svg>
            )}
          </button>
        </div>
      </div>

      {/* Mobile menu */}
      {open && (
        <div className="md:hidden border-t border-gray-100 bg-white px-4 py-3 space-y-1">
          {items.map(item => (
            <button
              key={item.screen}
              onClick={() => goTo(item.screen)}
              className={`w-full text-left px-3.5 py-2.5 rounded-xl text-sm font-medium transition-colors flex items-center justify-between ${
                currentScreen === item.screen
                  ? 'bg-brand-light text-brand-dark'
                  : 'text-gray-600 hover:bg-gray-50'
              }`}
            >
              {item.label}
              {item.screen === 'notifications' && unreadCount > 0 && (
                <span className="bg-brand-mid text-white text-[10px] rounded-full w-4 h-4 flex items-center justify-center shrink-0">
                  {unreadCount}
                </span>
              )}
            </button>
          ))}
          {!user.isAdmin && (
            <button
              onClick={() => goTo('create-proposal')}
              className="w-full text-left bg-brand-mid text-white rounded-xl px-3.5 py-2.5 text-sm font-medium hover:bg-brand-dark transition-colors"
            >
              + Nueva propuesta
            </button>
          )}
          <div className="pt-2 mt-2 border-t border-gray-100 flex items-center justify-between px-3.5">
            <span className="text-sm text-gray-600">{user.name}</span>
            <button onClick={() => { onLogout(); setOpen(false) }} className="text-xs text-gray-400 hover:text-red-500 transition-colors">
              Cerrar sesión
            </button>
          </div>
        </div>
      )}
    </nav>
  )
}
