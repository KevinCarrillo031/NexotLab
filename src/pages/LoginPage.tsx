import { useState } from 'react'
import Logo from '../components/Logo'
import { Button, Input, Select } from '../components/ui'
import { apiLogin, apiRegister } from '../api'
import type { User, ProfileType } from '../types'

interface LoginPageProps {
  onLogin: (user: User) => void
  backendOnline?: boolean | null
}

const profileOptions = [
  { value: 'entrepreneur', label: 'Emprendedor/a' },
  { value: 'company', label: 'Empresa' },
  { value: 'researcher', label: 'Investigador/a' },
  { value: 'citizen', label: 'Ciudadano/a' },
]

const sectorOptions = [
  { value: 'agro', label: 'Agro' },
  { value: 'health', label: 'Salud' },
  { value: 'education', label: 'Educación' },
  { value: 'energy', label: 'Energía' },
  { value: 'mobility', label: 'Movilidad' },
  { value: 'fintech', label: 'Fintech' },
  { value: 'government', label: 'Gobierno' },
  { value: 'environment', label: 'Medio ambiente' },
]

export default function LoginPage({ onLogin, backendOnline }: LoginPageProps) {
  const [tab, setTab] = useState<'login' | 'register'>('login')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [name, setName] = useState('')
  const [profile, setProfile] = useState<ProfileType>('entrepreneur')
  const [sector, setSector] = useState('agro')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleLogin = async () => {
    setError('')
    if (!email || !password) { setError('Completa todos los campos'); return }
    setLoading(true)
    try {
      const user = await apiLogin(email.trim(), password)
      onLogin(user)
    } catch (err: unknown) {
      // fallback demo si backend está offline
      if (backendOnline === false) {
        if (email.trim() === 'admin@nexotlab.com') {
          onLogin({ id: 'admin1', name: 'Diego Martínez', email, profileType: 'company', isAdmin: true, joinedAt: '2026-01-01' })
        } else {
          onLogin({ id: 'user1', name: 'Camila Rodríguez', email, profileType: 'entrepreneur', isAdmin: false, joinedAt: '2026-03-15' })
        }
      } else {
        setError(err instanceof Error ? err.message : 'Correo o contraseña incorrectos')
      }
    } finally {
      setLoading(false)
    }
  }

  const handleRegister = async () => {
    setError('')
    if (!name.trim() || !email.trim() || !password) { setError('Completa todos los campos'); return }
    if (password.length < 6) { setError('La contraseña debe tener al menos 6 caracteres'); return }
    setLoading(true)
    try {
      const user = await apiRegister(name.trim(), email.trim(), password, profile, sector)
      onLogin(user)
    } catch (err: unknown) {
      if (backendOnline === false) {
        onLogin({ id: `u_${Date.now()}`, name: name.trim(), email: email.trim(), profileType: profile, isAdmin: false, joinedAt: new Date().toISOString().split('T')[0] })
      } else {
        setError(err instanceof Error ? err.message : 'No se pudo crear la cuenta')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-full bg-brand-light flex flex-col items-center justify-center p-4">
      <div className="w-full max-w-sm">
        <div className="flex justify-center mb-8">
          <Logo size="lg" />
        </div>

        <div className="bg-white rounded-2xl border border-gray-100 p-6 shadow-none">
          <div className="flex rounded-xl bg-gray-50 p-1 mb-6">
            {(['login', 'register'] as const).map(t => (
              <button
                key={t}
                onClick={() => { setTab(t); setError('') }}
                className={`flex-1 text-sm font-medium py-2 rounded-xl transition-colors ${
                  tab === t ? 'bg-white text-brand-dark' : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                {t === 'login' ? 'Iniciar sesión' : 'Registrarse'}
              </button>
            ))}
          </div>

          <div className="space-y-4">
            {tab === 'register' && (
              <Input
                label="Nombre completo"
                id="reg-name"
                type="text"
                placeholder="Ej: Camila Rodríguez"
                value={name}
                onChange={e => setName(e.target.value)}
              />
            )}
            <Input
              label="Correo electrónico"
              id="email"
              type="email"
              placeholder="tu@correo.com"
              value={email}
              onChange={e => setEmail(e.target.value)}
            />
            <Input
              label="Contraseña"
              id="password"
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={e => setPassword(e.target.value)}
            />
            {tab === 'register' && (
              <Select
                label="Tipo de perfil"
                id="profile"
                options={profileOptions}
                value={profile}
                onChange={e => setProfile(e.target.value as ProfileType)}
              />
            )}
            {tab === 'register' && (
              <Select
                label="Sector"
                id="sector"
                options={sectorOptions}
                value={sector}
                onChange={e => setSector(e.target.value)}
              />
            )}

            {error && (
              <p className="text-xs text-red-500 bg-red-50 rounded-xl px-3 py-2">{error}</p>
            )}

            <Button
              variant="primary"
              size="lg"
              className="w-full"
              onClick={tab === 'login' ? handleLogin : handleRegister}
              disabled={loading}
            >
              {loading ? 'Cargando...' : tab === 'login' ? 'Entrar a NexotLab' : 'Crear cuenta'}
            </Button>
          </div>

          {tab === 'login' && (
            <div className="mt-4 pt-4 border-t border-gray-50">
              <p className="text-center text-xs text-gray-400 leading-relaxed">
                Contraseña de todos los usuarios: <span className="font-mono text-brand-mid font-semibold">nexotlab123</span>
              </p>
              <div className="mt-2 space-y-1 text-xs text-gray-400">
                <p className="text-center font-medium text-gray-500">Cuentas de ejemplo</p>
                <div className="flex justify-between px-2">
                  <span>Admin</span>
                  <span className="font-mono text-gray-500">admin@nexotlab.com</span>
                </div>
                <div className="flex justify-between px-2">
                  <span>Emprendedor/a</span>
                  <span className="font-mono text-gray-500">camila@nexotlab.com</span>
                </div>
                <div className="flex justify-between px-2">
                  <span>Investigador/a</span>
                  <span className="font-mono text-gray-500">luis@nexotlab.com</span>
                </div>
                <div className="flex justify-between px-2">
                  <span>Empresa</span>
                  <span className="font-mono text-gray-500">vale@nexotlab.com</span>
                </div>
              </div>
            </div>
          )}
        </div>

        <p className="text-center text-xs text-gray-500 mt-5 leading-relaxed">
          NexotLab — Plataforma de innovación abierta
          <br />
          Colombia · Since 2026
        </p>
      </div>
    </div>
  )
}
