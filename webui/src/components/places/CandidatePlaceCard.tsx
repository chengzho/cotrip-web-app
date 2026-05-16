import Badge from '../common/Badge'
import Card from '../common/Card'

export interface CandidatePlaceCardProps {
  category: '景點' | '餐廳'
  title: string
  description: string
  proposedBy: string
  votes: number
  voted?: boolean
}

export default function CandidatePlaceCard({
  category,
  title,
  description,
  proposedBy,
  votes,
  voted = false,
}: CandidatePlaceCardProps) {
  return (
    <Card className="p-6">
      <div className="flex items-start justify-between gap-3 mb-3">
        <div className="flex-1 min-w-0">
          <div className="mb-2">
            <Badge variant="neutral">{category}</Badge>
          </div>
          <h3 className="text-base font-semibold text-ink">{title}</h3>
          <p className="text-sm text-muted mt-1.5 leading-relaxed">{description}</p>
        </div>
        <div className="flex items-center gap-0.5 shrink-0">
          <button
            type="button"
            className="text-sm text-muted hover:text-ink px-2 py-1.5 rounded-lg hover:bg-brand-soft transition-colors"
          >
            編輯
          </button>
          <button
            type="button"
            className="text-sm text-muted hover:text-ink px-2 py-1.5 rounded-lg hover:bg-brand-soft transition-colors"
          >
            刪除
          </button>
        </div>
      </div>

      <div className="flex items-center justify-between pt-4 border-t border-line">
        <p className="text-sm text-muted">由 {proposedBy} 提案</p>
        <div className="flex items-center gap-3">
          <span className="text-sm">
            <span className="font-semibold text-ink">{votes}</span>
            <span className="text-muted ml-1">票</span>
          </span>
          <button
            type="button"
            className={[
              'inline-flex items-center justify-center px-4 py-1.5 text-sm font-medium rounded-full transition-colors',
              voted
                ? 'bg-ink text-brand-fg'
                : 'border border-line text-ink hover:bg-brand-soft',
            ].join(' ')}
          >
            {voted ? '已投票' : '投票'}
          </button>
        </div>
      </div>
    </Card>
  )
}
