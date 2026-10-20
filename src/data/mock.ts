/**
 * mock.ts — archivo vacío. Todos los datos vienen del backend MySQL.
 * Se mantiene para evitar romper importaciones existentes durante la transición.
 */
import type { Proposal, AppNotification, PlatformUser } from '../types'

export const mockProposals: Proposal[] = []
export const mockNotifications: AppNotification[] = []
export const mockPlatformUsers: PlatformUser[] = []
