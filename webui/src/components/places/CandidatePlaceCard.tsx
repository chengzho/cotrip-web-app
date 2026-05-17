import Badge from '../common/Badge'
import Card from '../common/Card'

const CATEGORY_LABEL: Record<string, string> = { attraction: '景點', restaurant: '餐廳' }

export interface CandidatePlaceCardProps {
  candidate_id: string;
  category: string;
  name: string;
  note: string | null;
  created_by: { display_name: string };
  vote_count: number;
  current_user_voted: boolean;
  onEdit?: () => void;
  onDelete?: () => void;
  onVote?: () => void;
  voting?: boolean;
}

export default function CandidatePlaceCard({
  category,
  name,
  note,
  created_by,
  vote_count,
  current_user_voted,
  onEdit,
  onDelete,
  onVote,
  voting = false,
}: CandidatePlaceCardProps) {
  return (
    <Card className="p-6">
      <div className="flex items-start justify-between gap-3 mb-3">
        <div className="flex-1 min-w-0">
          <div className="mb-2">
            <Badge variant="neutral">{CATEGORY_LABEL[category] ?? category}</Badge>
          </div>
          <h3 className="text-base font-semibold text-ink">{name}</h3>
          {note && (
            <p className="text-sm text-muted mt-1.5 leading-relaxed">{note}</p>
          )}
        </div>
        <div className="flex items-center gap-0.5 shrink-0">
          <button
            type="button"
            className="text-sm text-muted hover:text-ink px-2 py-1.5 rounded-lg hover:bg-brand-soft transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
            onClick={onEdit}
            disabled={!onEdit}
          >
            編輯
          </button>
          <button
            type="button"
            className="text-sm text-muted hover:text-red-600 px-2 py-1.5 rounded-lg hover:bg-red-50 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
            onClick={onDelete}
            disabled={!onDelete}
          >
            刪除
          </button>
        </div>
      </div>

      <div className="flex items-center justify-between pt-4 border-t border-line">
        <p className="text-sm text-muted">由 {created_by.display_name} 提案</p>
        <div className="flex items-center gap-3">
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
    </Card>
  )
}
