import { useState, useEffect } from 'react'
import { Card } from '../components/ui'

const BASE = 'http://localhost:8000/api/v1'

// ─── Types ──────────────────────────────────────────────────────────────────
interface PipelineStep {
  step: number
  name: string
  icon: string
  detail: string
  source: string
}

interface ModelResult {
  name: string
  key: string
  accuracy: number
  f1: number
  params: string
  pros: string
  cons: string
  selected: boolean
}

interface Cluster {
  segment: string
  label: string
  color: string
  icon: string
  count: number
  description: string
  nexotlab_action: string
}

interface AssocRule {
  antecedent: string[]
  consequent: string[]
  support: number
  confidence: number
  lift: number
  interpretation: string
  decision: string
}

interface MonthlyTrend {
  month: string
  propuestas: number
  score_medio: number
}

interface FeatureImportance {
  feature: string
  importance: number
}

interface NewKnowledge {
  finding: string
  evidence: string
  implication: string
  source: string
}

interface Insights {
  pipeline_steps: PipelineStep[]
  model_comparison: ModelResult[]
  selected_model: string
  r2_regression: number
  feature_importances: FeatureImportance[]
  user_clusters: Cluster[]
  proposal_clusters: Cluster[]
  user_silhouette: number
  proposal_silhouette: number
  interpreted_rules: AssocRule[]
  monthly_trend: MonthlyTrend[]
  by_sector: { sector: string; mean_score: number; n: number }[]
  by_profile: { author_profile: string; mean_score: number; n: number }[]
  new_knowledge: NewKnowledge[]
  data_source_note: { real_prepared: string; mock_ui: string; distinction: string }
  n_records: number
  n_users: number
  target_variable: string
  train_test_split: string
}

// ─── Helpers ────────────────────────────────────────────────────────────────
function Pct({ value, color }: { value: number; color: string }) {
  const pct = Math.min(100, Math.round(value * 100))
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden">
        <div className="h-2 rounded-full transition-all duration-500" style={{ width: `${pct}%`, backgroundColor: color }} />
      </div>
      <span className="text-xs font-medium text-gray-700 w-10 text-right">{pct}%</span>
    </div>
  )
}

function Badge({ text, color }: { text: string; color: string }) {
  return (
    <span className="inline-flex items-center gap-1 text-xs font-medium px-2 py-0.5 rounded-full" style={{ backgroundColor: color + '22', color }}>
      {text}
    </span>
  )
}

function SourceTag({ source }: { source: string }) {
  const map: Record<string, { label: string; color: string }> = {
    BASE_ORIGINAL: { label: 'Datos originales', color: '#6B7280' },
    BASE_PREPARADA: { label: 'Datos preparados', color: '#10B981' },
    INTERFAZ: { label: 'Integrado en UI', color: '#3B82F6' },
  }
  const info = map[source] ?? { label: source, color: '#6B7280' }
  return <Badge text={info.label} color={info.color} />
}

// ─── Sub-secciones ──────────────────────────────────────────────────────────

function PipelineSection({ steps }: { steps: PipelineStep[] }) {
  return (
    <Card className="p-5">
      <h3 className="text-sm font-semibold text-gray-800 mb-1">
        Pipeline completo: datos → resultados
      </h3>
      <p className="text-xs text-gray-400 mb-4">
        Proceso de 8 pasos desde los datos originales hasta la integración en NexoTLab
      </p>
      <div className="relative">
        <div className="absolute left-5 top-0 bottom-0 w-px bg-gray-100" />
        <div className="space-y-3">
          {steps.map((s, i) => (
            <div key={i} className="flex gap-4 pl-0">
              <div className="relative z-10 w-10 h-10 rounded-xl bg-gray-50 border border-gray-200 flex items-center justify-center text-base shrink-0">
                {s.icon}
              </div>
              <div className="flex-1 pt-1.5 pb-2 min-w-0">
                <div className="flex items-center gap-2 mb-0.5 flex-wrap">
                  <span className="text-xs font-semibold text-gray-800">{s.step}. {s.name}</span>
                  <SourceTag source={s.source} />
                </div>
                <p className="text-xs text-gray-500 leading-relaxed">{s.detail}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </Card>
  )
}

function ModelSection({
  models,
  winner,
  importances,
  target,
  split,
  r2,
}: {
  models: ModelResult[]
  winner: string
  importances: FeatureImportance[]
  target: string
  split: string
  r2: number
}) {
  return (
    <div className="space-y-4">
      <Card className="p-5">
        <h3 className="text-sm font-semibold text-gray-800 mb-1">Modelo predictivo de viabilidad</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 mb-4">
          <div className="bg-gray-50 rounded-lg p-3">
            <p className="text-[10px] text-gray-400 uppercase tracking-wide mb-0.5">Variable objetivo</p>
            <p className="text-xs font-medium text-gray-700">{target}</p>
          </div>
          <div className="bg-gray-50 rounded-lg p-3">
            <p className="text-[10px] text-gray-400 uppercase tracking-wide mb-0.5">División datos</p>
            <p className="text-xs font-medium text-gray-700">{split}</p>
          </div>
        </div>

        <div className="grid md:grid-cols-2 gap-3">
          {models.map(m => (
            <div key={m.key} className={`rounded-xl border-2 p-4 transition-all ${m.selected ? 'border-green-400 bg-green-50/40' : 'border-gray-100 bg-white'}`}>
              <div className="flex items-start justify-between mb-2">
                <div>
                  <p className="text-sm font-semibold text-gray-800">{m.name}</p>
                  <p className="text-[10px] text-gray-400 font-mono mt-0.5">{m.params}</p>
                </div>
                {m.selected && (
                  <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-green-100 text-green-700">
                    Seleccionado
                  </span>
                )}
              </div>
              <div className="space-y-2 mb-3">
                <div>
                  <div className="flex justify-between text-[10px] text-gray-500 mb-0.5">
                    <span>Accuracy</span><span>{(m.accuracy * 100).toFixed(1)}%</span>
                  </div>
                  <Pct value={m.accuracy} color={m.selected ? '#10B981' : '#9CA3AF'} />
                </div>
                <div>
                  <div className="flex justify-between text-[10px] text-gray-500 mb-0.5">
                    <span>F1-score</span><span>{(m.f1 * 100).toFixed(1)}%</span>
                  </div>
                  <Pct value={m.f1} color={m.selected ? '#3B82F6' : '#9CA3AF'} />
                </div>
              </div>
              <div className="text-[10px] space-y-1">
                <p className="text-green-700"><span className="font-medium">+ </span>{m.pros}</p>
                <p className="text-amber-600"><span className="font-medium">- </span>{m.cons}</p>
              </div>
            </div>
          ))}
        </div>

        {r2 > 0 && (
          <div className="mt-3 bg-blue-50 rounded-lg p-3">
            <p className="text-xs text-blue-700">
              <span className="font-semibold">Regresión lineal (score continuo):</span>{' '}
              R² = {r2.toFixed(3)} — el modelo explica el {(r2 * 100).toFixed(1)}% de la varianza del score de aceptación.
            </p>
          </div>
        )}
      </Card>

      {importances.length > 0 && (
        <Card className="p-5">
          <h3 className="text-sm font-semibold text-gray-800 mb-3">Importancia de variables (Árbol de Decisión)</h3>
          <div className="space-y-2">
            {importances.map((fi, i) => (
              <div key={i}>
                <div className="flex justify-between text-[10px] text-gray-500 mb-0.5">
                  <span className="font-mono truncate max-w-[200px]">{fi.feature}</span>
                  <span>{(fi.importance * 100).toFixed(1)}%</span>
                </div>
                <Pct value={fi.importance / (importances[0]?.importance || 1)} color="#8B5CF6" />
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  )
}

// ─── Predicción en vivo ─────────────────────────────────────────────────────
interface PredictResult {
  viable: boolean
  probability_viable: number | null
  predicted_score: number
  acceptance_level: string
  model: string
}

function LivePredictor() {
  const [form, setForm] = useState({
    category: 'digital-transformation',
    sector: 'agro',
    author_profile: 'entrepreneur',
    evaluations_count: 12,
    team_size: 1,
    accepted_collaborators: 0,
    description_length: 180,
  })
  const [result, setResult] = useState<PredictResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [err, setErr] = useState(false)

  const handlePredict = async () => {
    setLoading(true)
    setErr(false)
    try {
      const r = await fetch(`${BASE}/mining/predictive/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      })
      if (!r.ok) throw new Error()
      setResult(await r.json())
    } catch {
      setErr(true)
    } finally {
      setLoading(false)
    }
  }

  const categories = [
    { v: 'digital-transformation', l: 'Transformación Digital' },
    { v: 'sustainability', l: 'Sostenibilidad' },
    { v: 'education', l: 'Educación' },
    { v: 'health', l: 'Salud' },
    { v: 'fintech', l: 'Fintech' },
    { v: 'agro', l: 'Agro' },
    { v: 'mobility', l: 'Movilidad' },
    { v: 'energy', l: 'Energía' },
  ]
  const sectors = ['agro', 'health', 'education', 'energy', 'mobility', 'fintech', 'government', 'environment']
  const profiles = [
    { v: 'entrepreneur', l: 'Emprendedor/a' },
    { v: 'company', l: 'Empresa' },
    { v: 'researcher', l: 'Investigador/a' },
    { v: 'citizen', l: 'Ciudadano/a' },
  ]

  const sel = 'w-full text-xs border border-gray-200 rounded-lg px-3 py-2 bg-white focus:outline-none focus:ring-2 focus:ring-brand-mid'
  const num = 'w-full text-xs border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-brand-mid'

  return (
    <Card className="p-5">
      <h3 className="text-sm font-semibold text-gray-800 mb-1">Predicción en vivo</h3>
      <p className="text-xs text-gray-400 mb-4">
        Ingresa las características de una propuesta y el modelo predice su viabilidad
      </p>
      <div className="grid sm:grid-cols-2 gap-3 mb-4">
        <div>
          <label className="block text-[10px] text-gray-500 font-medium uppercase tracking-wide mb-1">Categoría</label>
          <select className={sel} value={form.category} onChange={e => setForm(f => ({ ...f, category: e.target.value }))}>
            {categories.map(c => <option key={c.v} value={c.v}>{c.l}</option>)}
          </select>
        </div>
        <div>
          <label className="block text-[10px] text-gray-500 font-medium uppercase tracking-wide mb-1">Sector</label>
          <select className={sel} value={form.sector} onChange={e => setForm(f => ({ ...f, sector: e.target.value }))}>
            {sectors.map(s => <option key={s} value={s}>{s.charAt(0).toUpperCase() + s.slice(1)}</option>)}
          </select>
        </div>
        <div>
          <label className="block text-[10px] text-gray-500 font-medium uppercase tracking-wide mb-1">Perfil del autor</label>
          <select className={sel} value={form.author_profile} onChange={e => setForm(f => ({ ...f, author_profile: e.target.value }))}>
            {profiles.map(p => <option key={p.v} value={p.v}>{p.l}</option>)}
          </select>
        </div>
        <div>
          <label className="block text-[10px] text-gray-500 font-medium uppercase tracking-wide mb-1">Evaluaciones recibidas</label>
          <input type="number" min={0} max={100} className={num} value={form.evaluations_count}
            onChange={e => setForm(f => ({ ...f, evaluations_count: parseInt(e.target.value) || 0 }))} />
        </div>
        <div>
          <label className="block text-[10px] text-gray-500 font-medium uppercase tracking-wide mb-1">Tamaño del equipo</label>
          <input type="number" min={1} max={50} className={num} value={form.team_size}
            onChange={e => setForm(f => ({ ...f, team_size: parseInt(e.target.value) || 1 }))} />
        </div>
        <div>
          <label className="block text-[10px] text-gray-500 font-medium uppercase tracking-wide mb-1">Colaboradores aceptados</label>
          <input type="number" min={0} max={50} className={num} value={form.accepted_collaborators}
            onChange={e => setForm(f => ({ ...f, accepted_collaborators: parseInt(e.target.value) || 0 }))} />
        </div>
        <div className="sm:col-span-2">
          <label className="block text-[10px] text-gray-500 font-medium uppercase tracking-wide mb-1">
            Longitud de descripción (caracteres)
          </label>
          <input type="number" min={10} max={2000} className={num} value={form.description_length}
            onChange={e => setForm(f => ({ ...f, description_length: parseInt(e.target.value) || 180 }))} />
        </div>
      </div>

      <button
        onClick={handlePredict}
        disabled={loading}
        className="w-full py-2.5 rounded-xl text-sm font-semibold bg-brand-mid text-white disabled:opacity-50 transition-opacity hover:opacity-90"
      >
        {loading ? 'Calculando…' : 'Predecir viabilidad'}
      </button>

      {err && (
        <p className="mt-3 text-xs text-red-500 text-center">
          Error al conectar con el backend. Verifica que el servidor esté corriendo.
        </p>
      )}

      {result && !err && (
        <div className={`mt-4 rounded-xl border-2 p-4 ${result.viable ? 'border-green-400 bg-green-50/40' : 'border-red-300 bg-red-50/40'}`}>
          <div className="flex items-center justify-between mb-3">
            <div>
              <p className="text-base font-bold" style={{ color: result.viable ? '#059669' : '#DC2626' }}>
                {result.viable ? 'Propuesta VIABLE' : 'Propuesta NO viable'}
              </p>
              <p className="text-[10px] text-gray-400 mt-0.5">
                Modelo: {result.model} · Nivel: {result.acceptance_level}
              </p>
            </div>
            {result.probability_viable !== null && (
              <div className="text-right">
                <p className="text-2xl font-bold" style={{ color: result.viable ? '#059669' : '#DC2626' }}>
                  {(result.probability_viable * 100).toFixed(1)}%
                </p>
                <p className="text-[10px] text-gray-400">probabilidad</p>
              </div>
            )}
          </div>
          {result.probability_viable !== null && (
            <div className="mb-3">
              <div className="flex justify-between text-[10px] text-gray-500 mb-1">
                <span>Probabilidad de viabilidad</span>
                <span>{(result.probability_viable * 100).toFixed(1)}%</span>
              </div>
              <Pct value={result.probability_viable} color={result.viable ? '#059669' : '#DC2626'} />
            </div>
          )}
          <div className="bg-blue-50 rounded-lg px-3 py-2">
            <p className="text-xs text-blue-700">
              <span className="font-semibold">Score continuo (regresión lineal):</span>{' '}
              {result.predicted_score.toFixed(2)} / 5.0
            </p>
          </div>
        </div>
      )}
    </Card>
  )
}

function SegmentationSection({
  userClusters,
  propClusters,
  userSil,
  propSil,
}: {
  userClusters: Cluster[]
  propClusters: Cluster[]
  userSil: number
  propSil: number
}) {
  const total_u = userClusters.reduce((s, c) => s + c.count, 0)
  const total_p = propClusters.reduce((s, c) => s + c.count, 0)

  return (
    <div className="space-y-4">
      <Card className="p-5">
        <div className="flex items-start justify-between mb-3">
          <div>
            <h3 className="text-sm font-semibold text-gray-800">Segmentación de usuarios</h3>
            <p className="text-xs text-gray-400">K-Means · Silhouette Score: {userSil.toFixed(3)}</p>
          </div>
          <Badge text={`${userClusters.length} grupos`} color="#3B82F6" />
        </div>
        <div className="space-y-3">
          {userClusters.map(c => (
            <div key={c.segment} className="rounded-xl border border-gray-100 p-4">
              <div className="flex items-center gap-2 mb-1">
                <span className="text-lg">{c.icon}</span>
                <span className="text-sm font-semibold text-gray-800">{c.label}</span>
                <span className="ml-auto text-xs font-medium" style={{ color: c.color }}>
                  {c.count} usuarios ({total_u > 0 ? Math.round((c.count / total_u) * 100) : 0}%)
                </span>
              </div>
              <div className="h-1.5 bg-gray-100 rounded-full mb-2">
                <div className="h-1.5 rounded-full" style={{ width: `${total_u > 0 ? (c.count / total_u) * 100 : 0}%`, backgroundColor: c.color }} />
              </div>
              <p className="text-xs text-gray-600 mb-1.5">{c.description}</p>
              <div className="bg-gray-50 rounded-lg px-3 py-2">
                <p className="text-[10px] text-gray-400 font-medium mb-0.5">¿Qué puede hacer NexoTLab?</p>
                <p className="text-xs text-gray-700">{c.nexotlab_action}</p>
              </div>
            </div>
          ))}
        </div>
      </Card>

      <Card className="p-5">
        <div className="flex items-start justify-between mb-3">
          <div>
            <h3 className="text-sm font-semibold text-gray-800">Segmentación de propuestas</h3>
            <p className="text-xs text-gray-400">K-Means · Silhouette Score: {propSil.toFixed(3)}</p>
          </div>
          <Badge text={`${propClusters.length} tipos`} color="#8B5CF6" />
        </div>
        <div className="space-y-3">
          {propClusters.map(c => (
            <div key={c.segment} className="rounded-xl border border-gray-100 p-4">
              <div className="flex items-center gap-2 mb-1">
                <span className="text-lg">{c.icon}</span>
                <span className="text-sm font-semibold text-gray-800">{c.label}</span>
                <span className="ml-auto text-xs font-medium" style={{ color: c.color }}>
                  {c.count} propuestas ({total_p > 0 ? Math.round((c.count / total_p) * 100) : 0}%)
                </span>
              </div>
              <div className="h-1.5 bg-gray-100 rounded-full mb-2">
                <div className="h-1.5 rounded-full" style={{ width: `${total_p > 0 ? (c.count / total_p) * 100 : 0}%`, backgroundColor: c.color }} />
              </div>
              <p className="text-xs text-gray-600 mb-1.5">{c.description}</p>
              <div className="bg-gray-50 rounded-lg px-3 py-2">
                <p className="text-[10px] text-gray-400 font-medium mb-0.5">¿Qué puede hacer NexoTLab?</p>
                <p className="text-xs text-gray-700">{c.nexotlab_action}</p>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  )
}

function AssociationSection({ rules }: { rules: AssocRule[] }) {
  return (
    <Card className="p-5">
      <h3 className="text-sm font-semibold text-gray-800 mb-1">Reglas de asociación (Apriori)</h3>
      <p className="text-xs text-gray-400 mb-4">
        Reglas cuyo consecuente es el resultado de evaluación · min_support=0.08 · min_confidence=0.45
      </p>
      {rules.length === 0 ? (
        <p className="text-xs text-gray-400">No hay reglas disponibles. Ejecuta el backend para calcularlas.</p>
      ) : (
        <div className="space-y-3">
          {rules.map((r, i) => (
            <div key={i} className="rounded-xl border border-gray-100 p-4">
              <div className="flex flex-wrap gap-1 items-center mb-2 text-xs">
                <span className="text-gray-500 font-medium">SI</span>
                {r.antecedent.map(a => (
                  <span key={a} className="px-2 py-0.5 bg-blue-50 text-blue-700 rounded-md font-mono">{a}</span>
                ))}
                <span className="text-gray-400 mx-1">→</span>
                <span className="text-gray-500 font-medium">ENTONCES</span>
                {r.consequent.map(c => (
                  <span key={c} className={`px-2 py-0.5 rounded-md font-mono ${c.includes('alta') ? 'bg-green-50 text-green-700' : c.includes('baja') ? 'bg-red-50 text-red-600' : 'bg-amber-50 text-amber-700'}`}>{c}</span>
                ))}
              </div>
              <div className="flex gap-3 mb-2 flex-wrap">
                {[
                  { label: 'Soporte', val: (r.support * 100).toFixed(1) + '%' },
                  { label: 'Confianza', val: (r.confidence * 100).toFixed(1) + '%' },
                  { label: 'Lift', val: r.lift.toFixed(2) },
                ].map(m => (
                  <div key={m.label} className="bg-gray-50 rounded-lg px-2 py-1">
                    <p className="text-[9px] text-gray-400">{m.label}</p>
                    <p className="text-xs font-semibold text-gray-700">{m.val}</p>
                  </div>
                ))}
              </div>
              <p className="text-xs text-gray-600 mb-1">{r.interpretation}</p>
              <div className="bg-green-50 rounded-lg px-3 py-1.5">
                <p className="text-[10px] text-green-700 font-medium">Decisión accionable:</p>
                <p className="text-xs text-green-800">{r.decision}</p>
              </div>
            </div>
          ))}
        </div>
      )}
    </Card>
  )
}

function TrendSection({
  trend,
  bySector,
  byProfile,
}: {
  trend: MonthlyTrend[]
  bySector: { sector: string; mean_score: number; n: number }[]
  byProfile: { author_profile: string; mean_score: number; n: number }[]
}) {
  const maxN = Math.max(...(trend.map(t => t.propuestas)), 1)
  return (
    <div className="space-y-4">
      {trend.length > 0 && (
        <Card className="p-5">
          <h3 className="text-sm font-semibold text-gray-800 mb-4">Tendencia mensual de propuestas</h3>
          <div className="flex items-end gap-1 h-28">
            {trend.map(t => (
              <div key={t.month} className="flex-1 flex flex-col items-center gap-1">
                <div
                  className="w-full rounded-t bg-brand-mid/70 min-h-[4px]"
                  style={{ height: `${(t.propuestas / maxN) * 100}px` }}
                  title={`${t.propuestas} propuestas, score ${t.score_medio.toFixed(2)}`}
                />
                <span className="text-[8px] text-gray-400 text-center leading-none">{t.month.slice(5)}</span>
              </div>
            ))}
          </div>
        </Card>
      )}

      <div className="grid md:grid-cols-2 gap-4">
        <Card className="p-5">
          <h3 className="text-sm font-semibold text-gray-800 mb-3">Score promedio por sector</h3>
          <div className="space-y-2">
            {bySector.map(s => (
              <div key={s.sector}>
                <div className="flex justify-between text-xs text-gray-600 mb-0.5">
                  <span>{s.sector}</span>
                  <span className="text-gray-400">{s.n} prop · {s.mean_score.toFixed(2)}</span>
                </div>
                <Pct value={s.mean_score / 5} color="#639922" />
              </div>
            ))}
          </div>
        </Card>
        <Card className="p-5">
          <h3 className="text-sm font-semibold text-gray-800 mb-3">Score promedio por perfil de autor</h3>
          <div className="space-y-2">
            {byProfile.map(p => (
              <div key={p.author_profile}>
                <div className="flex justify-between text-xs text-gray-600 mb-0.5">
                  <span>{p.author_profile}</span>
                  <span className="text-gray-400">{p.n} prop · {p.mean_score.toFixed(2)}</span>
                </div>
                <Pct value={p.mean_score / 5} color="#3B82F6" />
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  )
}

function InsightsSection({ items }: { items: NewKnowledge[] }) {
  return (
    <Card className="p-5">
      <h3 className="text-sm font-semibold text-gray-800 mb-1">
        Conocimiento nuevo descubierto gracias a la minería
      </h3>
      <p className="text-xs text-gray-400 mb-4">
        Hallazgos que no eran evidentes mirando directamente la base de datos
      </p>
      <div className="space-y-4">
        {items.map((k, i) => (
          <div key={i} className="rounded-xl border border-gray-100 p-4">
            <div className="flex items-start gap-2 mb-2">
              <span className="text-base">•</span>
              <p className="text-sm font-semibold text-gray-800">{k.finding}</p>
            </div>
            <div className="space-y-2 pl-7">
              <div>
                <p className="text-[10px] text-gray-400 font-medium uppercase tracking-wide">Evidencia</p>
                <p className="text-xs text-gray-600">{k.evidence}</p>
              </div>
              <div>
                <p className="text-[10px] text-gray-400 font-medium uppercase tracking-wide">Implicación para NexoTLab</p>
                <p className="text-xs text-gray-700">{k.implication}</p>
              </div>
              <p className="text-[10px] text-gray-400">Fuente: {k.source}</p>
            </div>
          </div>
        ))}
      </div>
    </Card>
  )
}

function DataSourceNote({ note, nRecords, nUsers }: {
  note: Insights['data_source_note']
  nRecords: number
  nUsers: number
}) {
  return (
    <Card className="p-5 border-l-4 border-amber-400">
      <h3 className="text-sm font-semibold text-gray-800 mb-2">Fuente de los datos</h3>
      <div className="space-y-2">
        <div className="flex gap-2 text-xs">
          <Badge text="Datos reales de minería" color="#10B981" />
          <span className="text-gray-600">{note.real_prepared}</span>
        </div>
        <div className="flex gap-2 text-xs">
          <Badge text="Mock de interfaz" color="#F59E0B" />
          <span className="text-gray-600">{note.mock_ui}</span>
        </div>
        <div className="bg-amber-50 rounded-lg px-3 py-2 mt-2">
          <p className="text-xs text-amber-800 font-medium">{note.distinction}</p>
        </div>
        <div className="flex gap-4 mt-2">
          <div className="text-center">
            <p className="text-lg font-bold text-gray-800">{nRecords}</p>
            <p className="text-[10px] text-gray-400">registros analizados</p>
          </div>
          <div className="text-center">
            <p className="text-lg font-bold text-gray-800">{nUsers}</p>
            <p className="text-[10px] text-gray-400">usuarios en la base</p>
          </div>
        </div>
      </div>
    </Card>
  )
}

// ─── Componente principal ────────────────────────────────────────────────────
export default function MiningDashboard() {
  const [insights, setInsights] = useState<Insights | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(false)
  const [tab, setTab] = useState<'pipeline' | 'modelos' | 'segmentacion' | 'reglas' | 'tendencias' | 'hallazgos'>(
    'pipeline'
  )

  useEffect(() => {
    setLoading(true)
    fetch(`${BASE}/mining/insights`)
      .then(r => {
        if (!r.ok) throw new Error('Backend error')
        return r.json()
      })
      .then(data => {
        setInsights(data)
        setLoading(false)
      })
      .catch(() => {
        setError(true)
        setLoading(false)
      })
  }, [])

  const tabs = [
    { key: 'pipeline', label: 'Pipeline' },
    { key: 'modelos', label: 'Modelos' },
    { key: 'segmentacion', label: 'Segmentación' },
    { key: 'reglas', label: 'Reglas' },
    { key: 'tendencias', label: 'Tendencias' },
    { key: 'hallazgos', label: 'Hallazgos' },
  ] as const

  if (loading) {
    return (
      <div className="flex items-center justify-center py-16">
        <div className="text-center">
          <div className="w-8 h-8 border-2 border-brand-mid border-t-transparent rounded-full animate-spin mx-auto mb-3" />
          <p className="text-sm text-gray-500">Calculando modelos de minería…</p>
        </div>
      </div>
    )
  }

  if (error || !insights) {
    return (
      <Card className="p-8 text-center">
        <p className="text-sm font-medium text-gray-700 mb-1">Backend no disponible</p>
        <p className="text-xs text-gray-400">
          Inicia el servidor FastAPI en{' '}
          <span className="font-mono text-brand-mid">http://localhost:8000</span>{' '}
          para cargar los resultados de minería de datos.
        </p>
      </Card>
    )
  }

  return (
    <div className="space-y-5">
      {/* Header */}
      <div className="rounded-xl bg-gradient-to-r from-[#1a2e1a] to-[#2d4a2d] px-5 py-4">
        <div className="flex items-start justify-between flex-wrap gap-3">
          <div>
            <h2 className="text-sm font-semibold text-white mb-0.5">Panel de Minería de Datos</h2>
            <p className="text-xs text-white/60">
              Resultados calculados sobre {insights.n_records} registros · {insights.n_users} usuarios
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            {insights.model_comparison.map(m => (
              <div key={m.key} className={`px-3 py-1.5 rounded-lg ${m.selected ? 'bg-green-400/20' : 'bg-white/10'}`}>
                <p className="text-[10px] text-white/60">{m.name}</p>
                <p className="text-sm font-bold text-white">{(m.accuracy * 100).toFixed(1)}%</p>
                <p className="text-[9px] text-white/50">accuracy</p>
              </div>
            ))}
            <div className="px-3 py-1.5 rounded-lg bg-white/10">
              <p className="text-[10px] text-white/60">Silhouette</p>
              <p className="text-sm font-bold text-white">{insights.user_silhouette.toFixed(3)}</p>
              <p className="text-[9px] text-white/50">clustering</p>
            </div>
          </div>
        </div>
      </div>

      {/* Fuente de datos */}
      <DataSourceNote
        note={insights.data_source_note}
        nRecords={insights.n_records}
        nUsers={insights.n_users}
      />

      {/* Tabs */}
      <div className="flex overflow-x-auto rounded-xl bg-gray-50 p-1 gap-0.5">
        {tabs.map(t => (
          <button
            key={t.key}
            onClick={() => setTab(t.key)}
            className={`px-3 py-2 text-xs font-medium rounded-lg whitespace-nowrap transition-colors ${
              tab === t.key ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* Content */}
      {tab === 'pipeline' && <PipelineSection steps={insights.pipeline_steps} />}
      {tab === 'modelos' && (
        <div className="space-y-5">
          <ModelSection
            models={insights.model_comparison}
            winner={insights.selected_model}
            importances={insights.feature_importances}
            target={insights.target_variable}
            split={insights.train_test_split}
            r2={insights.r2_regression}
          />
          <LivePredictor />
        </div>
      )}
      {tab === 'segmentacion' && (
        <SegmentationSection
          userClusters={insights.user_clusters}
          propClusters={insights.proposal_clusters}
          userSil={insights.user_silhouette}
          propSil={insights.proposal_silhouette}
        />
      )}
      {tab === 'reglas' && <AssociationSection rules={insights.interpreted_rules} />}
      {tab === 'tendencias' && (
        <TrendSection
          trend={insights.monthly_trend}
          bySector={insights.by_sector}
          byProfile={insights.by_profile}
        />
      )}
      {tab === 'hallazgos' && <InsightsSection items={insights.new_knowledge} />}
    </div>
  )
}
