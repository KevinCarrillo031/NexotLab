import type { ProposalStatus, ProfileType, NotificationType } from '../types'

// ── Button ─────────────────────────────────────────────────────────────────

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger'
  size?: 'sm' | 'md' | 'lg'
}

export function Button({ variant = 'primary', size = 'md', className = '', children, ...props }: ButtonProps) {
  const base = 'inline-flex items-center justify-center gap-1.5 rounded-xl font-medium transition-colors duration-150 focus:outline-none focus:ring-2 focus:ring-brand-mid focus:ring-offset-1 disabled:opacity-50 disabled:cursor-not-allowed'
  const sizes = { sm: 'px-3 py-1.5 text-xs', md: 'px-4 py-2 text-sm', lg: 'px-5 py-2.5 text-sm' }
  const variants = {
    primary: 'bg-brand-mid text-white hover:bg-brand-dark',
    secondary: 'border border-brand-mid text-brand-mid hover:bg-brand-light',
    ghost: 'text-brand-mid hover:bg-brand-light',
    danger: 'bg-red-500 text-white hover:bg-red-600',
  }
  return (
    <button className={`${base} ${sizes[size]} ${variants[variant]} ${className}`} {...props}>
      {children}
    </button>
  )
}

// ── StatusBadge ─────────────────────────────────────────────────────────────

const statusCfg: Record<ProposalStatus, { label: string; cls: string; dot: string }> = {
  good: { label: 'Buen proyecto', cls: 'bg-brand-light text-brand-dark', dot: 'bg-brand-mid' },
  'needs-improvement': { label: 'Necesita mejoras', cls: 'bg-amber-100 text-amber-600', dot: 'bg-amber-500' },
  evaluating: { label: 'En evaluación', cls: 'bg-gray-100 text-gray-500', dot: 'bg-gray-400' },
}

export function StatusBadge({ status }: { status: ProposalStatus }) {
  const { label, cls, dot } = statusCfg[status]
  return (
    <span className={`inline-flex items-center gap-1.5 text-xs font-medium px-2.5 py-1 rounded-full ${cls}`}>
      <span className={`w-1.5 h-1.5 rounded-full shrink-0 ${dot}`} />
      {label}
    </span>
  )
}

// ── RoleBadge ───────────────────────────────────────────────────────────────

const roleLabels: Record<ProfileType, string> = {
  entrepreneur: 'Emprendedor/a',
  company: 'Empresa',
  researcher: 'Investigador/a',
  citizen: 'Ciudadano/a',
}

export function RoleBadge({ profileType }: { profileType: ProfileType }) {
  return (
    <span className="inline-flex items-center text-xs font-medium px-2 py-0.5 rounded-full bg-gray-100 text-gray-600">
      {roleLabels[profileType]}
    </span>
  )
}

// ── MetricCard ──────────────────────────────────────────────────────────────

interface MetricCardProps {
  value: string | number
  label: string
  accent?: boolean
  subtitle?: string
}

export function MetricCard({ value, label, accent, subtitle }: MetricCardProps) {
  return (
    <div className={`rounded-xl border border-gray-100 p-4 ${accent ? 'bg-brand-light' : 'bg-white'}`}>
      <div className={`text-3xl font-medium leading-none ${accent ? 'text-brand-dark' : 'text-brand-mid'}`}>
        {value}
      </div>
      <div className="text-xs text-gray-500 mt-2">{label}</div>
      {subtitle && <div className="text-[10px] text-gray-400 mt-0.5">{subtitle}</div>}
    </div>
  )
}

// ── ScoreBarChart ────────────────────────────────────────────────────────────

export function ScoreBarChart({ scores }: { scores: number[] }) {
  if (scores.length === 0) return (
    <div className="h-20 flex items-center justify-center text-xs text-gray-400">
      Sin datos de semanas anteriores
    </div>
  )
  const MAX = 5
  const W = 300
  const H = 90
  const PT = 18, PB = 22, PL = 8, PR = 8
  const chartW = W - PL - PR
  const chartH = H - PT - PB
  const slot = chartW / scores.length

  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full" style={{ maxHeight: 90 }} aria-label="Evolución semanal del score">
      {[1, 2, 3, 4, 5].map(v => {
        const y = PT + chartH - (v / MAX) * chartH
        return <line key={v} x1={PL} x2={W - PR} y1={y} y2={y} stroke="#F3F4F6" strokeWidth={1} />
      })}
      {scores.map((score, i) => {
        const barW = slot * 0.55
        const gapW = slot * 0.45
        const x = PL + i * slot + gapW / 2
        const barH = Math.max((score / MAX) * chartH, 2)
        const y = PT + chartH - barH
        const isLast = i === scores.length - 1
        return (
          <g key={i}>
            <rect x={x} y={y} width={barW} height={barH} fill={isLast ? '#27500A' : '#639922'} rx={2} opacity={isLast ? 1 : 0.65} />
            <text x={x + barW / 2} y={H - 5} textAnchor="middle" fontSize={8} fill="#9CA3AF" fontFamily="Outfit, sans-serif">
              S{i + 1}
            </text>
            <text x={x + barW / 2} y={y - 4} textAnchor="middle" fontSize={9} fill={isLast ? '#27500A' : '#639922'} fontWeight={500} fontFamily="Outfit, sans-serif">
              {score.toFixed(1)}
            </text>
          </g>
        )
      })}
    </svg>
  )
}

// ── RatingSlider ─────────────────────────────────────────────────────────────

interface RatingSliderProps {
  label: string
  value: number
  onChange: (v: number) => void
}

export function RatingSlider({ label, value, onChange }: RatingSliderProps) {
  return (
    <div className="space-y-1.5">
      <div className="flex justify-between items-center">
        <span className="text-sm text-gray-600">{label}</span>
        <span className="text-sm font-medium text-brand-dark w-5 text-right">{value}</span>
      </div>
      <input
        type="range"
        min={1}
        max={5}
        step={1}
        value={value}
        onChange={e => onChange(Number(e.target.value))}
        className="w-full h-1.5 rounded-full appearance-none bg-gray-200 cursor-pointer [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-4 [&::-webkit-slider-thumb]:h-4 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-brand-mid"
      />
      <div className="flex justify-between text-[9px] text-gray-400 px-0.5">
        {[1, 2, 3, 4, 5].map(v => <span key={v}>{v}</span>)}
      </div>
    </div>
  )
}

// ── Input ────────────────────────────────────────────────────────────────────

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
}

export function Input({ label, error, className = '', id, ...props }: InputProps) {
  return (
    <div className="space-y-1.5">
      {label && <label htmlFor={id} className="block text-sm font-medium text-gray-700">{label}</label>}
      <input
        id={id}
        className={`w-full rounded-xl border px-3.5 py-2.5 text-sm text-gray-800 placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-brand-mid focus:border-transparent transition-colors bg-white ${error ? 'border-red-400' : 'border-gray-200'} ${className}`}
        {...props}
      />
      {error && <p className="text-xs text-red-500">{error}</p>}
    </div>
  )
}

// ── Textarea ─────────────────────────────────────────────────────────────────

interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string
  error?: string
}

export function Textarea({ label, error, className = '', id, ...props }: TextareaProps) {
  return (
    <div className="space-y-1.5">
      {label && <label htmlFor={id} className="block text-sm font-medium text-gray-700">{label}</label>}
      <textarea
        id={id}
        className={`w-full rounded-xl border px-3.5 py-2.5 text-sm text-gray-800 placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-brand-mid focus:border-transparent transition-colors bg-white resize-none ${error ? 'border-red-400' : 'border-gray-200'} ${className}`}
        {...props}
      />
      {error && <p className="text-xs text-red-500">{error}</p>}
    </div>
  )
}

// ── Select ───────────────────────────────────────────────────────────────────

interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label?: string
  options: { value: string; label: string }[]
}

export function Select({ label, options, className = '', id, ...props }: SelectProps) {
  return (
    <div className="space-y-1.5">
      {label && <label htmlFor={id} className="block text-sm font-medium text-gray-700">{label}</label>}
      <select
        id={id}
        className={`w-full rounded-xl border border-gray-200 px-3.5 py-2.5 text-sm text-gray-800 focus:outline-none focus:ring-2 focus:ring-brand-mid focus:border-transparent bg-white ${className}`}
        {...props}
      >
        {options.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
      </select>
    </div>
  )
}

// ── Card ─────────────────────────────────────────────────────────────────────

export function Card({ children, className = '' }: { children: React.ReactNode; className?: string }) {
  return (
    <div className={`bg-white rounded-xl border border-gray-100 ${className}`}>
      {children}
    </div>
  )
}

// ── PageHeader ────────────────────────────────────────────────────────────────

export function PageHeader({ title, subtitle, action }: { title: string; subtitle?: string; action?: React.ReactNode }) {
  return (
    <div className="flex items-start justify-between mb-6 gap-3">
      <div>
        <h1 className="text-xl font-medium text-brand-dark">{title}</h1>
        {subtitle && <p className="text-sm text-gray-500 mt-0.5">{subtitle}</p>}
      </div>
      {action && <div className="shrink-0">{action}</div>}
    </div>
  )
}

// ── NotificationIcon ──────────────────────────────────────────────────────────

export function NotificationIcon({ type }: { type: NotificationType }) {
  if (type === 'positive') return (
    <div className="w-9 h-9 rounded-xl bg-brand-light flex items-center justify-center shrink-0">
      <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true">
        <path d="M2.5 8.5L6 12L13.5 4.5" stroke="#639922" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    </div>
  )
  if (type === 'improvement') return (
    <div className="w-9 h-9 rounded-xl bg-amber-100 flex items-center justify-center shrink-0">
      <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true">
        <path d="M8 2L14.5 13.5H1.5L8 2Z" stroke="#D97706" strokeWidth="1.5" strokeLinejoin="round" />
        <path d="M8 6V9" stroke="#D97706" strokeWidth="1.5" strokeLinecap="round" />
        <circle cx="8" cy="11.5" r="0.75" fill="#D97706" />
      </svg>
    </div>
  )
  return (
    <div className="w-9 h-9 rounded-xl bg-gray-100 flex items-center justify-center shrink-0">
      <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true">
        <circle cx="8" cy="5.5" r="2.5" stroke="#6B7280" strokeWidth="1.4" />
        <path d="M2.5 14c0-3.038 2.462-5.5 5.5-5.5s5.5 2.462 5.5 5.5" stroke="#6B7280" strokeWidth="1.4" strokeLinecap="round" />
      </svg>
    </div>
  )
}

// ── Avatar ────────────────────────────────────────────────────────────────────

export function Avatar({ name, size = 'sm' }: { name: string; size?: 'sm' | 'md' | 'lg' }) {
  const sz = size === 'sm' ? 'w-7 h-7 text-xs' : size === 'md' ? 'w-9 h-9 text-sm' : 'w-14 h-14 text-xl'
  return (
    <div className={`${sz} rounded-full bg-brand-light flex items-center justify-center font-medium text-brand-dark shrink-0`}>
      {name.charAt(0).toUpperCase()}
    </div>
  )
}
