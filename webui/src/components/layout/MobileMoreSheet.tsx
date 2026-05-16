import { Link, useParams } from 'react-router-dom'

interface MobileMoreSheetProps {
  open: boolean
  onClose: () => void
}

export default function MobileMoreSheet({ open, onClose }: MobileMoreSheetProps) {
  const { tripId } = useParams<{ tripId: string }>()

  if (!open) return null

  return (
    <>
      <div
        className="fixed inset-0 bg-ink/30 z-40"
        onClick={onClose}
        aria-hidden="true"
      />
      <div
        role="dialog"
        aria-modal="true"
        className="fixed inset-x-0 bottom-0 z-50 bg-surface rounded-t-2xl shadow-[0_-4px_24px_0_rgba(28,25,23,0.10)]"
        style={{ paddingBottom: 'env(safe-area-inset-bottom)' }}
      >
        <div className="flex items-center justify-between px-5 py-4 border-b border-line">
          <span className="text-sm font-semibold text-ink">更多</span>
          <button
            onClick={onClose}
            className="w-8 h-8 flex items-center justify-center rounded-full text-muted hover:text-ink hover:bg-brand-soft transition-colors"
            aria-label="關閉選單"
          >
            ✕
          </button>
        </div>
        <ul className="p-3">
          {[
            { label: '成員', to: `/trips/${tripId}/members` },
            { label: '設定', to: `/trips/${tripId}/settings` },
          ].map(({ label, to }) => (
            <li key={to}>
              <Link
                to={to}
                onClick={onClose}
                className="block px-4 py-3 rounded-lg text-sm text-ink hover:bg-brand-soft transition-colors"
              >
                {label}
              </Link>
            </li>
          ))}
          <li>
            <button
              onClick={onClose}
              className="w-full text-left px-4 py-3 rounded-lg text-sm text-ink hover:bg-brand-soft transition-colors"
            >
              邀請朋友
            </button>
          </li>
        </ul>
      </div>
    </>
  )
}
