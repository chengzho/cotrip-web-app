import Badge from '../common/Badge'

export interface RankingRowProps {
  rank: number
  title: string
  category: '景點' | '餐廳'
  proposedBy: string
  votes: number
  voted?: boolean
}

export default function RankingRow({
  rank,
  title,
  category,
  proposedBy,
  votes,
  voted = false,
}: RankingRowProps) {
  return (
    <div className="flex items-center gap-4 px-5 py-4 bg-surface rounded-xl border border-line">
      <span
        className={[
          'text-sm font-bold w-6 text-center shrink-0',
          rank <= 3 ? 'text-ink' : 'text-muted',
        ].join(' ')}
      >
        {rank}
      </span>

      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 flex-wrap mb-1">
          <span className="text-base font-semibold text-ink">{title}</span>
          <Badge variant="neutral">{category}</Badge>
        </div>
        <p className="text-sm text-muted">由 {proposedBy} 提案</p>
      </div>

      <div className="flex items-center gap-3 shrink-0">
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
  )
}
