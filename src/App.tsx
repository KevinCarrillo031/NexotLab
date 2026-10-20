import { useState, useEffect } from 'react'
import Navbar from './components/Navbar'
import LoginPage from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'
import CreateProposalPage from './pages/CreateProposalPage'
import ProposalDetailPage from './pages/ProposalDetailPage'
import MyTeamsPage from './pages/MyTeamsPage'
import NotificationsPage from './pages/NotificationsPage'
import ProfilePage from './pages/ProfilePage'
import AdminPage from './pages/AdminPage'
import { mockProposals, mockNotifications, mockPlatformUsers } from './data/mock'
import {
  apiLogin,
  apiRegister,
  apiGetProposals,
  apiGetNotifications,
  apiGetPlatformUsers,
  apiCreateProposal,
  apiApplyCollaborator,
  apiAcceptCollaborator,
  apiRejectCollaborator,
  apiMarkRead,
  apiMarkAllRead,
  apiToggleUser,
} from './api'
import type { User, Screen, Proposal, AppNotification, PlatformUser, ProfileType } from './types'

// Expuesto globalmente para que LoginPage lo invoque
export type LoginFn = (email: string, password: string) => Promise<User>
export type RegisterFn = (name: string, email: string, password: string, profile: ProfileType) => Promise<User>

const SESSION_KEY = 'nexotlab_user'

function loadSavedUser(): User | null {
  try {
    const raw = localStorage.getItem(SESSION_KEY)
    return raw ? (JSON.parse(raw) as User) : null
  } catch {
    return null
  }
}

export default function App() {
  const savedUser = loadSavedUser()
  const [screen, setScreen] = useState<Screen>(savedUser ? (savedUser.isAdmin ? 'admin' : 'dashboard') : 'login')
  const [currentUser, setCurrentUser] = useState<User | null>(savedUser)
  const [selectedProposalId, setSelectedProposalId] = useState<string | null>(null)
  const [proposals, setProposals] = useState<Proposal[]>([])
  const [notifications, setNotifications] = useState<AppNotification[]>([])
  const [platformUsers, setPlatformUsers] = useState<PlatformUser[]>([])
  const [appliedIds, setAppliedIds] = useState<string[]>([])
  const [backendOnline, setBackendOnline] = useState<boolean | null>(null)

  // ── cargar datos iniciales desde el backend (o mock si no responde) ────────
  useEffect(() => {
    apiGetProposals()
      .then(data => {
        setProposals(data)
        setBackendOnline(true)
      })
      .catch(() => {
        setProposals(mockProposals)
        setBackendOnline(false)
      })
  }, [])

  useEffect(() => {
    if (!currentUser) return
    apiGetNotifications(currentUser.id)
      .then(setNotifications)
      .catch(() => setNotifications(mockNotifications))
  }, [currentUser])

  useEffect(() => {
    if (!currentUser?.isAdmin) return
    apiGetPlatformUsers()
      .then(setPlatformUsers)
      .catch(() => setPlatformUsers(mockPlatformUsers))
  }, [currentUser])

  const navigate = (s: Screen, proposalId?: string) => {
    if (proposalId !== undefined) setSelectedProposalId(proposalId)
    setScreen(s)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  // ── auth ──────────────────────────────────────────────────────────────────
  const handleLogin = async (user: User) => {
    localStorage.setItem(SESSION_KEY, JSON.stringify(user))
    setCurrentUser(user)
    setScreen(user.isAdmin ? 'admin' : 'dashboard')
  }

  const handleLogout = () => {
    localStorage.removeItem(SESSION_KEY)
    setCurrentUser(null)
    setScreen('login')
    setAppliedIds([])
    setNotifications([])
  }

  // ── propuestas ────────────────────────────────────────────────────────────
  const handleCreateProposal = async (
    data: Omit<Proposal, 'id' | 'status' | 'weeklyScores' | 'currentScore' | 'collaborators' | 'evaluationsCount'>
  ) => {
    if (!currentUser) return
    try {
      const created = await apiCreateProposal({ ...data, authorId: currentUser.id })
      setProposals(prev => [created, ...prev])
    } catch {
      // fallback local
      const newProposal: Proposal = {
        ...data,
        id: `p_${Date.now()}`,
        status: 'evaluating',
        weeklyScores: [],
        currentScore: 0,
        collaborators: [],
        evaluationsCount: 0,
      }
      setProposals(prev => [newProposal, ...prev])
    }
  }

  // ── colaboradores ─────────────────────────────────────────────────────────
  const handleApply = async (proposalId: string) => {
    if (!currentUser || appliedIds.includes(proposalId)) return
    setAppliedIds(prev => [...prev, proposalId])

    try {
      await apiApplyCollaborator(proposalId, currentUser.id)
      // refrescar propuesta desde backend
      const updated = await apiGetProposals()
      setProposals(updated)
    } catch {
      // optimista local
      setProposals(prev => prev.map(p => {
        if (p.id !== proposalId) return p
        const alreadyIn = p.collaborators.some(c => c.id === currentUser.id)
        if (alreadyIn) return p
        return {
          ...p,
          collaborators: [
            ...p.collaborators,
            { id: currentUser.id, name: currentUser.name, profileType: currentUser.profileType, status: 'pending' as const, appliedAt: new Date().toISOString().split('T')[0] },
          ],
        }
      }))
    }

    setNotifications(prev => [{
      id: `notif_${Date.now()}`,
      type: 'social' as const,
      message: "Te postulaste como colaborador en la propuesta.",
      proposalTitle: proposals.find(p => p.id === proposalId)?.title,
      date: new Date().toISOString().split('T')[0],
      read: true,
    }, ...prev])
  }

  const handleAcceptCollaborator = async (proposalId: string, collaboratorId: string) => {
    if (!currentUser) return
    try {
      await apiAcceptCollaborator(proposalId, collaboratorId, currentUser.id)
    } catch { /* continúa con actualización local */ }
    setProposals(prev => prev.map(p => {
      if (p.id !== proposalId) return p
      return { ...p, collaborators: p.collaborators.map(c => c.id === collaboratorId ? { ...c, status: 'accepted' as const } : c) }
    }))
  }

  const handleRejectCollaborator = async (proposalId: string, collaboratorId: string) => {
    if (!currentUser) return
    try {
      await apiRejectCollaborator(proposalId, collaboratorId, currentUser.id)
    } catch { /* continúa con actualización local */ }
    setProposals(prev => prev.map(p => {
      if (p.id !== proposalId) return p
      return { ...p, collaborators: p.collaborators.filter(c => c.id !== collaboratorId) }
    }))
    setAppliedIds(prev => prev.filter(id => id !== proposalId))
  }

  // ── notificaciones ────────────────────────────────────────────────────────
  const handleMarkRead = async (id: string) => {
    try { await apiMarkRead(id) } catch { /* silent */ }
    setNotifications(prev => prev.map(n => n.id === id ? { ...n, read: true } : n))
  }

  const handleMarkAllRead = async () => {
    if (!currentUser) return
    try { await apiMarkAllRead(currentUser.id) } catch { /* silent */ }
    setNotifications(prev => prev.map(n => ({ ...n, read: true })))
  }

  // ── admin ─────────────────────────────────────────────────────────────────
  const handleToggleUser = async (id: string) => {
    try { await apiToggleUser(id) } catch { /* silent */ }
    setPlatformUsers(prev => prev.map(u => u.id === id ? { ...u, active: !u.active } : u))
  }

  const unreadCount = notifications.filter(n => !n.read).length
  const selectedProposal = proposals.find(p => p.id === selectedProposalId)

  if (!currentUser) {
    return (
      <LoginPage
        onLogin={handleLogin}
        backendOnline={backendOnline}
      />
    )
  }

  return (
    <div className="min-h-full bg-gray-50 flex flex-col">
      {backendOnline === false && (
        <div className="bg-amber-50 border-b border-amber-200 text-amber-800 text-xs text-center py-1.5 px-4">
          Backend no disponible — mostrando datos de demostración. Inicia el servidor en <span className="font-mono">http://localhost:8000</span>
        </div>
      )}
      <Navbar
        user={currentUser}
        currentScreen={screen}
        navigate={navigate}
        unreadCount={unreadCount}
        onLogout={handleLogout}
      />

      <main className="flex-1">
        {screen === 'dashboard' && (
          <DashboardPage
            user={currentUser}
            proposals={proposals}
            navigate={navigate}
            appliedIds={appliedIds}
            onApply={handleApply}
          />
        )}

        {(screen === 'create-proposal' || screen === 'edit-proposal') && (
          <CreateProposalPage
            user={currentUser}
            navigate={navigate}
            onSubmit={handleCreateProposal}
            editingProposal={screen === 'edit-proposal' ? (selectedProposal ?? null) : null}
          />
        )}

        {screen === 'proposal-detail' && selectedProposal && (
          <ProposalDetailPage
            proposal={selectedProposal}
            currentUser={currentUser}
            navigate={navigate}
            onApply={handleApply}
            applied={appliedIds.includes(selectedProposal.id)}
            onAcceptCollaborator={handleAcceptCollaborator}
            onRejectCollaborator={handleRejectCollaborator}
          />
        )}

        {screen === 'my-teams' && (
          <MyTeamsPage
            user={currentUser}
            proposals={proposals}
            navigate={navigate}
          />
        )}

        {screen === 'notifications' && (
          <NotificationsPage
            notifications={notifications}
            navigate={navigate}
            onMarkRead={handleMarkRead}
            onMarkAllRead={handleMarkAllRead}
          />
        )}

        {screen === 'profile' && (
          <ProfilePage
            user={currentUser}
            proposals={proposals}
            navigate={navigate}
          />
        )}

        {screen === 'admin' && currentUser.isAdmin && (
          <AdminPage
            platformUsers={platformUsers}
            onToggleUser={handleToggleUser}
          />
        )}
      </main>
    </div>
  )
}
