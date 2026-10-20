import { useState } from 'react'
import { Button, Input, Textarea, Select, Card, PageHeader } from '../components/ui'
import type { User, NavigateFn, Proposal, ProposalCategory } from '../types'

interface CreateProposalPageProps {
  user: User
  navigate: NavigateFn
  onSubmit: (data: Omit<Proposal, 'id' | 'status' | 'weeklyScores' | 'currentScore' | 'collaborators' | 'evaluationsCount'>) => void
  editingProposal?: Proposal | null
}

const categoryOptions = [
  { value: 'digital-transformation', label: 'Transformación digital e inteligencia organizacional' },
  { value: 'digital-economy', label: 'Economía digital, emprendimiento e innovación' },
]

export default function CreateProposalPage({ user, navigate, onSubmit, editingProposal }: CreateProposalPageProps) {
  const [title, setTitle] = useState(editingProposal?.title || '')
  const [category, setCategory] = useState<ProposalCategory>(editingProposal?.category || 'digital-transformation')
  const [description, setDescription] = useState(editingProposal?.description || '')
  const [deliverable, setDeliverable] = useState(editingProposal?.deliverable || '')
  const [fileName, setFileName] = useState<string | null>(null)
  const [errors, setErrors] = useState<Record<string, string>>({})

  const validate = () => {
    const e: Record<string, string> = {}
    if (!title.trim()) e.title = 'El título es requerido'
    if (title.trim().length < 10) e.title = 'El título debe ser más descriptivo (mín. 10 caracteres)'
    if (!description.trim()) e.description = 'La descripción es requerida'
    if (description.trim().length < 50) e.description = 'Agrega más detalle (mínimo 50 caracteres)'
    if (!deliverable.trim()) e.deliverable = 'El entregable es requerido'
    setErrors(e)
    return Object.keys(e).length === 0
  }

  const handleSubmit = () => {
    if (!validate()) return
    onSubmit({
      title: title.trim(),
      category,
      description: description.trim(),
      deliverable: deliverable.trim(),
      authorId: user.id,
      authorName: user.name,
      authorProfile: user.profileType,
      createdAt: new Date().toISOString().split('T')[0],
    })
    navigate('dashboard')
  }

  const isEditing = !!editingProposal

  return (
    <div className="max-w-2xl mx-auto px-4 py-6">
      <PageHeader
        title={isEditing ? 'Editar propuesta' : 'Nueva propuesta'}
        subtitle={isEditing ? 'Actualiza la información de tu propuesta' : 'Comparte tu idea con la comunidad NexotLab'}
        action={
          <Button variant="ghost" size="sm" onClick={() => navigate('dashboard')}>
            Cancelar
          </Button>
        }
      />

      <Card className="p-6">
        <div className="space-y-5">
          <Input
            label="Título de la propuesta"
            id="title"
            type="text"
            placeholder="Ej: Sistema de trazabilidad con blockchain para el sector cafetero"
            value={title}
            onChange={e => setTitle(e.target.value)}
            error={errors.title}
          />

          <Select
            label="Categoría"
            id="category"
            options={categoryOptions}
            value={category}
            onChange={e => setCategory(e.target.value as ProposalCategory)}
          />

          <Textarea
            label="Descripción"
            id="description"
            placeholder="Describe el problema que resuelves, tu enfoque de solución y por qué es relevante para la comunidad..."
            value={description}
            onChange={e => setDescription(e.target.value)}
            rows={5}
            error={errors.description}
          />

          <Textarea
            label="Producto a entregar"
            id="deliverable"
            placeholder="Describe específicamente qué entregarás al finalizar: prototipo, app, informe, guía metodológica, etc."
            value={deliverable}
            onChange={e => setDeliverable(e.target.value)}
            rows={3}
            error={errors.deliverable}
          />

          {/* File attachment */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1.5">
              Documentos adjuntos <span className="text-gray-400 font-normal">(opcional)</span>
            </label>
            <label className="flex items-center gap-3 border border-dashed border-gray-200 rounded-xl px-4 py-4 cursor-pointer hover:border-brand-mid hover:bg-brand-light/30 transition-colors group">
              <div className="w-9 h-9 rounded-xl bg-gray-50 group-hover:bg-brand-light flex items-center justify-center transition-colors shrink-0">
                <svg width="18" height="18" viewBox="0 0 18 18" fill="none" aria-hidden="true">
                  <path d="M9 2.5v8M6 7L9 4l3 3" stroke="#639922" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round" />
                  <path d="M3 13v1.5A1.5 1.5 0 004.5 16h9a1.5 1.5 0 001.5-1.5V13" stroke="#639922" strokeWidth="1.4" strokeLinecap="round" />
                </svg>
              </div>
              <div>
                <p className="text-sm text-gray-600 font-medium">{fileName || 'Subir documento'}</p>
                <p className="text-xs text-gray-400">PDF, DOCX, PPTX · máximo 10 MB</p>
              </div>
              <input
                type="file"
                className="sr-only"
                accept=".pdf,.docx,.pptx"
                onChange={e => setFileName(e.target.files?.[0]?.name || null)}
              />
            </label>
          </div>

          <div className="flex gap-3 pt-2">
            <Button variant="primary" size="lg" className="flex-1" onClick={handleSubmit}>
              {isEditing ? 'Guardar cambios' : 'Publicar propuesta'}
            </Button>
            <Button variant="secondary" size="lg" onClick={() => navigate('dashboard')}>
              Cancelar
            </Button>
          </div>
        </div>
      </Card>
    </div>
  )
}
