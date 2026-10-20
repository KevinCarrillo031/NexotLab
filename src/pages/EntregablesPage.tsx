import { useState, useEffect } from 'react'
import { Card } from '../components/ui'

const BASE = 'http://localhost:8000/api/v1'

interface DocEntry {
  id: string
  subject: string
  subject_key: 'electiva' | 'mining' | 'simulation'
  aporte: number
  title: string
  description: string
  path: string
  icon: string
  tags: string[]
  available: boolean
}

interface Catalog {
  total: number
  subjects: string[]
  documents: DocEntry[]
}

const SUBJECT_META: Record<string, { label: string; color: string; bg: string; border: string; dot: string }> = {
  electiva: {
    label: 'Electiva VI – Gestión de Producto Digital',
    color: 'text-purple-700',
    bg: 'bg-purple-50',
    border: 'border-purple-200',
    dot: 'bg-purple-500',
  },
  mining: {
    label: 'Minería de Datos',
    color: 'text-blue-700',
    bg: 'bg-blue-50',
    border: 'border-blue-200',
    dot: 'bg-blue-500',
  },
  simulation: {
    label: 'Modelado y Simulación',
    color: 'text-emerald-700',
    bg: 'bg-emerald-50',
    border: 'border-emerald-200',
    dot: 'bg-emerald-500',
  },
}

const SUBJECT_ORDER = ['electiva', 'mining', 'simulation']

export default function EntregablesPage() {
  const [catalog, setCatalog] = useState<Catalog | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [activeSubject, setActiveSubject] = useState<string>('electiva')
  const [openDoc, setOpenDoc] = useState<DocEntry | null>(null)

  useEffect(() => {
    fetch(`${BASE}/docs/catalog`)
      .then(r => r.json())
      .then(d => { setCatalog(d); setLoading(false) })
      .catch(() => {
        setError('No se pudo cargar el catálogo. Verifica que el backend esté corriendo en http://localhost:8443')
        setLoading(false)
      })
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 border-2 border-brand-mid border-t-transparent rounded-full animate-spin" />
          <span className="text-sm text-gray-400">Cargando entregables…</span>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <Card className="p-8 text-center">
        <div className="w-12 h-12 rounded-2xl bg-amber-100 flex items-center justify-center mx-auto mb-3">
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none" aria-hidden="true">
            <path d="M10 3L17.5 16.5H2.5L10 3Z" stroke="#D97706" strokeWidth="1.5" strokeLinejoin="round"/>
            <path d="M10 8V11.5" stroke="#D97706" strokeWidth="1.5" strokeLinecap="round"/>
            <circle cx="10" cy="14" r="0.75" fill="#D97706"/>
          </svg>
        </div>
        <p className="text-sm font-medium text-gray-800 mb-1">Backend no disponible</p>
        <p className="text-xs text-gray-400 max-w-sm mx-auto">{error}</p>
      </Card>
    )
  }

  if (!catalog) return null

  const bySubject = SUBJECT_ORDER.reduce<Record<string, DocEntry[]>>((acc, key) => {
    acc[key] = catalog.documents.filter(d => d.subject_key === key)
    return acc
  }, {})

  const activeDocs = bySubject[activeSubject] ?? []
  const meta = SUBJECT_META[activeSubject]

  return (
    <div className="space-y-5">
      {/* stat strip */}
      <div className="grid grid-cols-3 gap-3">
        {SUBJECT_ORDER.map(key => {
          const m = SUBJECT_META[key]
          const docs = bySubject[key] ?? []
          const available = docs.filter(d => d.available).length
          return (
            <button
              key={key}
              onClick={() => { setActiveSubject(key); setOpenDoc(null) }}
              className={`rounded-xl border p-4 text-left transition-all ${
                activeSubject === key
                  ? `${m.bg} ${m.border} ring-1 ring-offset-0 ring-current`
                  : 'bg-white border-gray-100 hover:border-gray-200'
              }`}
            >
              <div className="flex items-center gap-2 mb-2">
                <div className={`w-2 h-2 rounded-full ${m.dot}`} />
                <span className={`text-xs font-semibold ${activeSubject === key ? m.color : 'text-gray-500'}`}>
                  {available}/{docs.length} docs
                </span>
              </div>
              <p className={`text-xs leading-tight ${activeSubject === key ? m.color : 'text-gray-600'}`}>
                {m.label}
              </p>
            </button>
          )
        })}
      </div>

      {/* subject header */}
      <div className={`rounded-xl border ${meta.border} ${meta.bg} px-4 py-3 flex items-center gap-2`}>
        <div className={`w-2.5 h-2.5 rounded-full ${meta.dot}`} />
        <span className={`text-sm font-semibold ${meta.color}`}>{meta.label}</span>
        <span className="text-xs text-gray-400 ml-auto">
          {activeDocs.filter(d => d.available).length} de {activeDocs.length} disponibles
        </span>
      </div>

      {openDoc ? (
        /* ── VISOR INLINE ──────────────────────────────────────── */
        <div className="space-y-3">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setOpenDoc(null)}
              className="flex items-center gap-1.5 text-xs text-gray-500 hover:text-gray-800 transition-colors"
            >
              <svg width="14" height="14" viewBox="0 0 14 14" fill="none" aria-hidden="true">
                <path d="M9 2L4 7L9 12" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
              Volver al listado
            </button>
            <span className="text-gray-200">|</span>
            <span className="text-xs text-gray-400">{openDoc.icon} Aporte {openDoc.aporte}</span>
            <span className="text-sm font-medium text-gray-800 truncate">{openDoc.title}</span>
            <a
              href={`${BASE}/docs/file/${openDoc.id}`}
              target="_blank"
              rel="noopener noreferrer"
              download
              className="ml-auto flex items-center gap-1.5 text-xs font-medium text-brand-mid hover:text-brand-dark transition-colors shrink-0"
            >
              <svg width="13" height="13" viewBox="0 0 13 13" fill="none" aria-hidden="true">
                <path d="M6.5 1v7M3.5 5.5L6.5 8.5L9.5 5.5M2 11h9" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
              Descargar PDF
            </a>
          </div>

          <Card className="overflow-hidden p-0">
            <iframe
              src={`${BASE}/docs/file/${openDoc.id}#toolbar=1&navpanes=0&view=FitH`}
              title={openDoc.title}
              className="w-full border-0"
              style={{ height: '75vh', minHeight: 480 }}
            />
          </Card>
        </div>
      ) : (
        /* ── LISTA DE TARJETAS ────────────────────────────────── */
        <div className="grid gap-3">
          {activeDocs.map(doc => (
            <div
              key={doc.id}
              className={`bg-white rounded-xl border border-gray-100 p-5 transition-all ${doc.available ? 'cursor-pointer hover:shadow-md hover:-translate-y-px' : 'opacity-50'}`}
              onClick={() => doc.available && setOpenDoc(doc)}
            >
              <div className="flex items-start gap-4">
                {/* número de aporte */}
                <div className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 text-lg ${meta.bg}`}>
                  {doc.icon}
                </div>

                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1 flex-wrap">
                    <span className={`text-[11px] font-medium px-2 py-0.5 rounded-full ${meta.bg} ${meta.color}`}>
                      Aporte {doc.aporte}
                    </span>
                    {doc.available ? (
                      <span className="text-[11px] font-medium px-2 py-0.5 rounded-full bg-green-50 text-green-600">PDF disponible</span>
                    ) : (
                      <span className="text-[11px] font-medium px-2 py-0.5 rounded-full bg-gray-100 text-gray-400">No disponible</span>
                    )}
                  </div>
                  <p className="text-sm font-semibold text-gray-900 mb-1">{doc.title}</p>
                  <p className="text-xs text-gray-500 leading-relaxed">{doc.description}</p>
                  {doc.tags.length > 0 && (
                    <div className="flex flex-wrap gap-1 mt-2">
                      {doc.tags.map(tag => (
                        <span key={tag} className="text-[10px] px-1.5 py-0.5 rounded bg-gray-100 text-gray-500">{tag}</span>
                      ))}
                    </div>
                  )}
                </div>

                {doc.available && (
                  <div className="flex flex-col items-end gap-2 shrink-0">
                    <button
                      onClick={e => { e.stopPropagation(); setOpenDoc(doc) }}
                      className={`flex items-center gap-1.5 text-xs font-medium px-3 py-1.5 rounded-lg border transition-colors ${meta.border} ${meta.color} ${meta.bg} hover:opacity-80`}
                    >
                      <svg width="12" height="12" viewBox="0 0 12 12" fill="none" aria-hidden="true">
                        <rect x="1" y="1" width="10" height="10" rx="2" stroke="currentColor" strokeWidth="1.3" />
                        <path d="M4 6h4M4 4h2" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round" />
                      </svg>
                      Ver informe
                    </button>
                    <a
                      href={`${BASE}/docs/file/${doc.id}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      download
                      onClick={e => e.stopPropagation()}
                      className="text-[11px] text-gray-400 hover:text-gray-600 transition-colors"
                    >
                      ↓ Descargar
                    </a>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
