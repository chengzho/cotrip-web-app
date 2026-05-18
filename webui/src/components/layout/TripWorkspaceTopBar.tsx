import { useEffect, useRef, useState } from 'react'
import { useAuth } from '../../context/AuthContext'
import NicknameModal from '../profile/NicknameModal'
import type { TripDetail } from '../../types/trip'

interface TripWorkspaceTopBarProps {
  trip: TripDetail | null;
}

function formatDate(d: string): string {
  const [y, m, day] = d.split('-')
  return `${y}/${parseInt(m)}/${parseInt(day)}`
}

export default function TripWorkspaceTopBar({ trip }: TripWorkspaceTopBarProps) {
  const { user, profile, signOut } = useAuth()
  const [menuOpen, setMenuOpen] = useState(false)
  const [nicknameOpen, setNicknameOpen] = useState(false)
  const menuRef = useRef<HTMLDivElement>(null)

  // Prefer backend profile name; fall back to JWT-derived name while loading.
  const displayName = profile?.display_name ?? user?.displayName ?? ''
  const initial = displayName.charAt(0).toUpperCase() || '旅'

  useEffect(() => {
    if (!menuOpen) return
    function handleOutsideClick(e: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setMenuOpen(false)
      }
    }
    document.addEventListener('mousedown', handleOutsideClick)
    return () => document.removeEventListener('mousedown', handleOutsideClick)
  }, [menuOpen])

  return (
    <>
      <div className="h-16 border-b border-line bg-surface px-6 flex items-center justify-between shrink-0">
        <div className="flex flex-col min-w-0">
          {trip ? (
            <>
              <span className="text-base font-semibold text-ink truncate">{trip.title}</span>
              <span className="text-sm text-muted truncate">
                {trip.destination} · {formatDate(trip.start_date)} – {formatDate(trip.end_date)}
              </span>
            </>
          ) : (
            <>
              <span className="text-base font-semibold text-muted truncate">載入中…</span>
              <span className="text-sm text-muted truncate">—</span>
            </>
          )}
        </div>
        <div className="flex items-center gap-4 ml-4 shrink-0">
          {trip && (
            <span className="text-sm text-muted">{trip.summary.member_count} 位成員</span>
          )}
          <button
            type="button"
            className="inline-flex items-center justify-center px-4 py-1.5 text-sm font-medium rounded-full border border-line text-ink hover:bg-brand-soft transition-colors disabled:opacity-50"
            disabled
          >
            邀請朋友
          </button>
          {user && (
            <div className="relative" ref={menuRef}>
              <button
                type="button"
                onClick={() => setMenuOpen(v => !v)}
                className="w-7 h-7 rounded-full bg-brand-soft border border-line flex items-center justify-center hover:opacity-80 transition-opacity"
                aria-label="使用者選單"
              >
                <span className="text-xs font-medium text-ink select-none">
                  {initial}
                </span>
              </button>
              {menuOpen && (
                <div className="absolute right-0 top-full mt-1.5 w-40 bg-surface border border-line rounded-lg shadow-lg py-1 z-20">
                  <button
                    type="button"
                    onClick={() => { setMenuOpen(false); setNicknameOpen(true) }}
                    className="w-full text-left px-4 py-2 text-sm text-ink hover:bg-brand-soft transition-colors"
                  >
                    設定顯示名稱
                  </button>
                  <button
                    type="button"
                    onClick={signOut}
                    className="w-full text-left px-4 py-2 text-sm text-muted hover:bg-brand-soft hover:text-ink transition-colors"
                  >
                    登出
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
      {nicknameOpen && (
        <NicknameModal
          initialDisplayName={profile?.display_name ?? user?.displayName ?? ''}
          onClose={() => setNicknameOpen(false)}
        />
      )}
    </>
  )
}
