import { useEffect, useState } from 'react'
import { useParams, useOutletContext } from 'react-router-dom'
import Button from '../../components/common/Button'
import LoadingState from '../../components/common/LoadingState'
import ErrorState from '../../components/common/ErrorState'
import EmptyState from '../../components/common/EmptyState'
import ItineraryDaySection from '../../components/itinerary/ItineraryDaySection'
import ItineraryItemForm from '../../components/itinerary/ItineraryItemForm'
import { getItinerary, generateItinerary, updateItineraryItem, deleteItineraryItem, ApiError } from '../../api/index'
import type { Itinerary, UpdateItineraryItemRequest } from '../../types/itinerary'
import type { ItineraryItem } from '../../components/itinerary/ItineraryItemRow'
import type { WorkspaceOutletContext } from '../../components/layout/TripWorkspaceLayout'

type EditTarget = { item: ItineraryItem; dayNumber: number } | null

export default function TripItineraryPage() {
  const { tripId } = useParams<{ tripId: string }>()
  const { trip } = useOutletContext<WorkspaceOutletContext>()
  const isOwner = trip?.current_user_role === 'owner'

  const [itinerary, setItinerary] = useState<Itinerary | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [generating, setGenerating] = useState(false)
  const [editTarget, setEditTarget] = useState<EditTarget>(null)
  const [isEditDirty, setIsEditDirty] = useState(false)

  useEffect(() => {
    if (!tripId) return
    getItinerary(tripId)
      .then(setItinerary)
      .catch((err: unknown) => {
        setError(err instanceof ApiError ? err.message : '無法載入行程表，請稍後再試。')
      })
      .finally(() => setLoading(false))
  }, [tripId])

  async function handleGenerate(overwrite: boolean) {
    if (overwrite && !window.confirm('確定要重新產生行程表嗎？現有行程將被覆蓋。')) return
    setGenerating(true)
    setError(null)
    try {
      const result = await generateItinerary(tripId!, { overwrite_existing: overwrite })
      setItinerary(result)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : '產生行程表失敗，請稍後再試。')
    } finally {
      setGenerating(false)
    }
  }

  function requestEditTarget(item: ItineraryItem, dayNumber: number) {
    if (editTarget && isEditDirty) {
      if (!window.confirm('目前的變更尚未儲存，確定要放棄並編輯另一個項目嗎？')) return
    }
    setIsEditDirty(false)
    setEditTarget({ item, dayNumber })
  }

  async function handleEditItem(data: UpdateItineraryItemRequest) {
    if (!editTarget) return
    await updateItineraryItem(tripId!, editTarget.item.item_id, data)
    const refreshed = await getItinerary(tripId!)
    setItinerary(refreshed)
    setIsEditDirty(false)
    setEditTarget(null)
  }

  async function handleDeleteItem(item: ItineraryItem) {
    if (!window.confirm('確定要刪除此行程項目嗎？')) return
    try {
      await deleteItineraryItem(tripId!, item.item_id)
      const refreshed = await getItinerary(tripId!)
      setItinerary(refreshed)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : '刪除失敗，請稍後再試。')
    }
  }

  const days = itinerary?.days ?? []
  const totalItems = days.reduce((sum, d) => sum + d.items.length, 0)

  return (
    <div className="p-6 max-w-5xl">
      {/* Header row */}
      <div className="flex items-start justify-between gap-4 mb-2">
        <h2 className="font-display text-xl font-semibold text-ink">行程表</h2>
        {isOwner && (
          <Button
            variant="primary"
            size="sm"
            onClick={() => handleGenerate(true)}
            disabled={generating || days.length === 0}
          >
            {generating ? '產生中…' : '重新產生行程'}
          </Button>
        )}
      </div>

      {/* Summary — only shown when data is available */}
      {!loading && !error && days.length > 0 && (
        <p className="text-sm text-muted mb-6">
          {days.length} 天 · {totalItems} 個地點 · 由群組投票結果產生
        </p>
      )}

      {/* Edit form — owner only */}
      {isOwner && editTarget && (
        <div className="mb-6">
          <ItineraryItemForm
            key={editTarget.item.item_id}
            item={editTarget.item}
            dayNumber={editTarget.dayNumber}
            onSave={handleEditItem}
            onCancel={() => { setIsEditDirty(false); setEditTarget(null) }}
            onDirtyChange={setIsEditDirty}
          />
        </div>
      )}

      {/* States */}
      {loading && <LoadingState message="載入行程表中…" />}

      {!loading && error && (
        <ErrorState title="無法載入行程表" message={error} />
      )}

      {/* Empty state */}
      {!loading && !error && days.length === 0 && (
        isOwner ? (
          <EmptyState
            title="尚未產生行程表"
            description="前往投票頁面，為候選地點投票，再回來產生共享行程表。"
            action={
              <Button onClick={() => handleGenerate(false)} disabled={generating}>
                {generating ? '產生中…' : '產生行程表'}
              </Button>
            }
          />
        ) : (
          <EmptyState
            title="行程表尚未建立"
            description="旅程擁有者建立行程表後，你就可以在這裡查看完整安排。"
          />
        )
      )}

      {/* Itinerary content */}
      {!loading && !error && days.length > 0 && (
        <div className="flex flex-col gap-5">
          {!isOwner && (
            <p className="text-sm text-muted leading-relaxed">
              這份行程表由旅程擁有者管理。你可以透過提名地點與投票參與規劃。
            </p>
          )}
          {days.map((day) => (
            <ItineraryDaySection
              key={day.day_number}
              day_number={day.day_number}
              date={day.date}
              items={day.items}
              onEditItem={isOwner ? requestEditTarget : undefined}
              onDeleteItem={isOwner ? handleDeleteItem : undefined}
            />
          ))}
        </div>
      )}
    </div>
  )
}
