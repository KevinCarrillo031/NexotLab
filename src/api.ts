/**
 * api.ts — capa de servicio que conecta el frontend con el backend FastAPI.
 * Base URL: http://localhost:8443/api/v1
 *
 * Todas las funciones retornan datos en el formato que espera el frontend (tipos de types.ts).
 * Si el servidor no responde, los errores se propagan para que el componente los maneje.
 */

import type { User, Proposal, AppNotification, PlatformUser, ProfileType, ProposalCategory } from './types'

const BASE = 'http://localhost:8000/api/v1'

// ─── helper ─────────────────────────────────────────────────────────────────

async function http<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...init?.headers },
    ...init,
  })
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw new Error(body?.detail ?? `HTTP ${res.status}`)
  }
  return res.json() as Promise<T>
}

// ─── tipos de respuesta del backend ─────────────────────────────────────────

interface BackendUser {
  id: string
  name: string
  email: string
  profile_type: ProfileType
  sector?: string
  is_admin: boolean
  active: boolean
  joined_at: string
  proposals_count: number
}

interface BackendProposal {
  id: string
  title: string
  category: ProposalCategory
  sector: string
  description: string
  deliverable: string
  authorId: string
  authorName: string
  authorProfile: ProfileType
  status: string
  weeklyScores: number[]
  currentScore: number
  collaborators: Array<{
    id: string
    name: string
    profileType: ProfileType
    status: 'pending' | 'accepted'
    appliedAt: string
  }>
  createdAt: string
  evaluationsCount: number
}

interface BackendNotification {
  id: string
  userId?: string
  user_id?: string
  type: 'positive' | 'improvement' | 'social'
  message: string
  proposalTitle?: string
  proposal_title?: string
  date: string
  read: boolean
}

// ─── mappers ─────────────────────────────────────────────────────────────────

function mapUser(u: BackendUser): User {
  return {
    id: u.id,
    name: u.name,
    email: u.email,
    profileType: u.profile_type,
    isAdmin: u.is_admin,
    joinedAt: u.joined_at,
  }
}

function mapProposal(p: BackendProposal): Proposal {
  return {
    id: p.id,
    title: p.title,
    category: p.category as ProposalCategory,
    description: p.description,
    deliverable: p.deliverable,
    authorId: p.authorId,
    authorName: p.authorName,
    authorProfile: p.authorProfile,
    status: p.status as Proposal['status'],
    weeklyScores: p.weeklyScores ?? [],
    currentScore: p.currentScore ?? 0,
    collaborators: (p.collaborators ?? []).map(c => ({
      id: c.id,
      name: c.name,
      profileType: c.profileType,
      status: c.status,
      appliedAt: c.appliedAt,
    })),
    createdAt: p.createdAt,
    evaluationsCount: p.evaluationsCount ?? 0,
  }
}

function mapNotification(n: BackendNotification): AppNotification {
  return {
    id: n.id,
    type: n.type,
    message: n.message,
    proposalTitle: n.proposalTitle ?? n.proposal_title,
    date: n.date,
    read: n.read,
  }
}

function mapPlatformUser(u: BackendUser): PlatformUser {
  return {
    id: u.id,
    name: u.name,
    email: u.email,
    profileType: u.profile_type,
    active: u.active,
    joinedAt: u.joined_at,
    proposalsCount: u.proposals_count ?? 0,
  }
}

// ─── AUTH ────────────────────────────────────────────────────────────────────

export async function apiLogin(email: string, _password: string): Promise<User> {
  const data = await http<{ authenticated: boolean; user: BackendUser }>(
    '/platform/auth/login',
    { method: 'POST', body: JSON.stringify({ email, password: _password }) }
  )
  return mapUser(data.user)
}

export async function apiRegister(
  name: string,
  email: string,
  _password: string,
  profileType: ProfileType,
  sector: string = 'government'
): Promise<User> {
  const data = await http<BackendUser>('/platform/users', {
    method: 'POST',
    body: JSON.stringify({ name, email, profile_type: profileType, sector, password: _password }),
  })
  return mapUser(data)
}

// ─── PROPOSALS ───────────────────────────────────────────────────────────────

export async function apiGetProposals(): Promise<Proposal[]> {
  const data = await http<{ items: BackendProposal[] }>('/platform/proposals?limit=1000')
  return data.items.map(mapProposal)
}

export async function apiGetProposal(id: string): Promise<Proposal> {
  const data = await http<BackendProposal>(`/platform/proposals/${id}`)
  return mapProposal(data)
}

export async function apiCreateProposal(
  payload: Pick<Proposal, 'title' | 'category' | 'description' | 'deliverable'> & { authorId: string; sector?: string }
): Promise<Proposal> {
  const data = await http<BackendProposal>('/platform/proposals', {
    method: 'POST',
    body: JSON.stringify({
      title: payload.title,
      category: payload.category,
      sector: payload.sector ?? 'government',
      description: payload.description,
      deliverable: payload.deliverable,
      author_id: payload.authorId,
    }),
  })
  return mapProposal(data)
}

// ─── COLLABORATORS ───────────────────────────────────────────────────────────

export async function apiApplyCollaborator(proposalId: string, userId: string): Promise<void> {
  await http('/platform/collaborators/apply', {
    method: 'POST',
    body: JSON.stringify({ proposal_id: proposalId, user_id: userId }),
  })
}

export async function apiAcceptCollaborator(proposalId: string, userId: string, requestingUserId: string): Promise<void> {
  await http(`/platform/collaborators/${proposalId}/${userId}/accept?requesting_user_id=${requestingUserId}`, {
    method: 'PATCH',
  })
}

export async function apiRejectCollaborator(proposalId: string, userId: string, requestingUserId: string): Promise<void> {
  await http(`/platform/collaborators/${proposalId}/${userId}/reject?requesting_user_id=${requestingUserId}`, {
    method: 'PATCH',
  })
}

// ─── NOTIFICATIONS ───────────────────────────────────────────────────────────

export async function apiGetNotifications(userId?: string): Promise<AppNotification[]> {
  const q = userId ? `?user_id=${userId}` : ''
  const data = await http<{ items: BackendNotification[] }>(`/platform/notifications${q}`)
  return data.items.map(mapNotification)
}

export async function apiMarkRead(notificationId: string): Promise<void> {
  await http(`/platform/notifications/${notificationId}/read`, { method: 'PATCH' })
}

export async function apiMarkAllRead(userId: string): Promise<void> {
  await http(`/platform/notifications/read-all?user_id=${userId}`, { method: 'PATCH' })
}

// ─── USERS (admin) ───────────────────────────────────────────────────────────

export async function apiGetPlatformUsers(): Promise<PlatformUser[]> {
  const data = await http<{ items: BackendUser[] }>('/platform/users?limit=1000')
  return data.items.map(mapPlatformUser)
}

export async function apiToggleUser(userId: string): Promise<void> {
  await http(`/platform/users/${userId}/toggle-active`, { method: 'PATCH' })
}

// ─── ADMIN OVERVIEW ──────────────────────────────────────────────────────────

export async function apiAdminOverview(): Promise<Record<string, unknown>> {
  return http('/platform/admin/overview')
}
