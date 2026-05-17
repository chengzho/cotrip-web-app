import Badge from '../common/Badge'

const CATEGORY_LABEL: Record<string, string> = { attraction: '景點', restaurant: '餐廳' }

export interface RankingRowProps {
  rank: number;
  candidate_id: string;
  category: string;
  name: string;
  created_by: { display_name: string };
  vote_count: number;
  current_user_voted: boolean;
  onVote?: () => void;
  voting?: boolean;
}

export default function RankingRow({
  rank,
  category,
  name,
  created_by,
  vote_count,
  current_user_voted,
  onVote,
  voting = false,
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
          <span className="text-base font-semibold text-ink">{name}</span>
          <Badge variant="neutral">{CATEGORY_LABEL[category] ?? category}</Badge>
        </div>
        <p className="text-sm text-muted">由 {created_by.display_name} 提案</p>
      </div>

      <div className="flex items-center gap-3 shrink-0">
        <span className="text-sm">
          <span className="font-semibold text-ink">{vote_count}</span>
          <span className="text-muted ml-1">票</span>
        </span>
        <button
          type="button"
          className={[
            'inline-flex items-center justify-center px-4 py-1.5 text-sm font-medium rounded-full transition-colors disabled:opacity-50',
            current_user_voted
              ? 'bg-ink text-brand-fg'
              : 'border border-line text-ink hover:bg-brand-soft',
          ].join(' ')}
          onClick={onVote}
          disabled={!onVote || voting}
        >
          {voting ? '…' : current_user_voted ? '已投票' : '投票'}
        </button>
      </div>
    </div>
  )
}
