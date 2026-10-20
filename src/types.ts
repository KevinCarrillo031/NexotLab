export type ProfileType = 'entrepreneur' | 'company' | 'researcher' | 'citizen'
export type ProposalStatus = 'good' | 'needs-improvement' | 'evaluating'
export type ProposalCategory =
  | 'digital-transformation'
  | 'digital-economy'
  | 'sustainability'
  | 'health-tech'
  | 'edtech'
  | 'agritech'
  | 'smart-cities'
  | 'fintech'
  | 'circular-economy'
  | 'open-data'
export type NotificationType = 'positive' | 'improvement' | 'social'
export type Screen =
  | 'login'
  | 'dashboard'
  | 'create-proposal'
  | 'edit-proposal'
  | 'proposal-detail'
  | 'my-teams'
  | 'notifications'
  | 'profile'
  | 'admin'

export interface User {
  id: string
  name: string
  email: string
  profileType: ProfileType
  isAdmin: boolean
  joinedAt: string
}

export interface Collaborator {
  id: string
  name: string
  profileType: ProfileType
  status: 'pending' | 'accepted'
  appliedAt: string
}

export interface Proposal {
  id: string
  title: string
  category: ProposalCategory
  description: string
  deliverable: string
  authorId: string
  authorName: string
  authorProfile: ProfileType
  status: ProposalStatus
  weeklyScores: number[]
  currentScore: number
  collaborators: Collaborator[]
  createdAt: string
  evaluationsCount: number
}

export interface AppNotification {
  id: string
  type: NotificationType
  message: string
  proposalTitle?: string
  date: string
  read: boolean
}

export interface PlatformUser {
  id: string
  name: string
  email: string
  profileType: ProfileType
  active: boolean
  joinedAt: string
  proposalsCount: number
}

export type NavigateFn = (screen: Screen, proposalId?: string) => void
