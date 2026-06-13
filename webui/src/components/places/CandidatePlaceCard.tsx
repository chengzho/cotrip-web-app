import Card from '../common/Card'
import { CATEGORY_LABEL, MEAL_TIME_LABEL } from '../../constants/candidateCategories'
import type { CandidateCategory, RestaurantMealTime } from '../../constants/candidateCategories'

export interface CandidatePlaceCardProps {
  candidate_id: string;
  category: CandidateCategory;
  name: string;
  note: string | null;
  created_by: { display_name: string };
  vote_count: number;
  current_user_voted: boolean;
  restaurant_meal_times?: RestaurantMealTime[] | null;
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
  restaurant_meal_times,
  onEdit,
  onDelete,
  onVote,
  voting = false,
}: CandidatePlaceCardProps) {
  const mealTimeText =
    category === 'restaurant' && restaurant_meal_times && restaurant_meal_times.length > 0
      ? restaurant_meal_times.map((t) => MEAL_TIME_LABEL[t]).join('・')
      : null

  return (
    <Card className="px-4 py-3.5">
      {/* Row 1: name + vote button */}
      <div className="flex items-start gap-3">
        <div className="flex-1 min-w-0">
          <h3 className="text-sm font-semibold text-ink leading-snug">{name}</h3>
          {note && (
            <p className="text-xs text-muted mt-1 leading-relaxed">{note}</p>
          )}
        </div>
        <button
          type="button"
          className={[
            'inline-flex items-center justify-center px-3 py-1 text-sm font-medium rounded-md transition-colors disabled:opacity-50 shrink-0',
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

      {/* Row 2: category · meal times · proposer + vote count + actions */}
      <div className="flex items-center justify-between mt-2.5">
        <p className="text-xs text-muted">
          {CATEGORY_LABEL[category] ?? category}
          {mealTimeText && <span className="text-muted/70"> · {mealTimeText}</span>}
          {' · '}由 {created_by.display_name} 提案
        </p>
        <div className="flex items-center gap-2">
          <span className="text-xs text-muted">
            <span className="font-medium text-ink">{vote_count}</span> 票
          </span>
          <div className="flex items-center gap-0.5">
            <button
              type="button"
              className="text-xs text-muted hover:text-ink px-2 py-1 rounded hover:bg-brand-soft transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
              onClick={onEdit}
              disabled={!onEdit}
            >
              編輯
            </button>
            <button
              type="button"
              className="text-xs text-muted hover:text-red-600 px-2 py-1 rounded hover:bg-red-50 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
              onClick={onDelete}
              disabled={!onDelete}
            >
              刪除
            </button>
          </div>
        </div>
      </div>
    </Card>
  )
}
