import { CATEGORY_LABEL } from '../../constants/candidateCategories'
import type { CandidateCategory } from '../../constants/candidateCategories'

export interface RankingRowProps {
  rank: number;
  candidate_id: string;
  category: CandidateCategory;
  name: string;
  created_by: { display_name: string };
  vote_count: number;
  current_user_voted: boolean;
  showCategory?: boolean;
  variant?: 'card' | 'list';
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
  showCategory = true,
  variant = 'card',
  onVote,
  voting = false,
}: RankingRowProps) {
  const wrapperClass = variant === 'list'
    ? 'flex items-center gap-4 px-4 py-3'
    : 'flex items-center gap-4 px-5 py-4 bg-surface rounded-xl border border-line'

  return (
    <div className={wrapperClass}>
      <span
        className={[
          'text-sm font-bold w-6 text-center shrink-0',
          rank <= 3 ? 'text-ink' : 'text-muted',
        ].join(' ')}
      >
        {rank}
      </span>

      <div className="flex-1 min-w-0">
        <p className="text-base font-semibold text-ink mb-0.5 truncate">{name}</p>
        <p className="text-xs text-muted">
          {showCategory && `${CATEGORY_LABEL[category] ?? category} · `}
          由 {created_by.display_name} 提案
        </p>
      </div>

      <div className="flex items-center gap-3 shrink-0">
        <span className="text-sm">
          <span className="font-semibold text-ink">{vote_count}</span>
          <span className="text-muted ml-1">票</span>
        </span>
        <button
          type="button"
          className={[
            'inline-flex items-center justify-center px-3 py-1.5 text-sm font-medium rounded-md transition-colors disabled:opacity-50',
            current_user_voted
              ? 'bg-ink text-brand-fg'
              : 'bg-surface-soft border border-line text-ink hover:bg-brand-soft',
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
