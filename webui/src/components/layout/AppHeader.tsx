import { useEffect, useRef, useState } from 'react'
import { useAuth } from '../../context/AuthContext'
import NicknameModal from '../profile/NicknameModal'

interface AppHeaderProps {
  className?: string
}

export default function AppHeader({ className = '' }: AppHeaderProps) {
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
      <header
        className={[
          'sticky top-0 z-30 bg-surface border-b border-line',
          className,
        ].join(' ')}
      >
        <div className="max-w-5xl mx-auto px-5 h-14 flex items-center justify-between">
          <span className="font-display text-lg font-semibold tracking-tight text-ink">
            CoTrip
          </span>
          <div className="flex items-center gap-3">
            {user && (
              <span className="text-sm text-muted hidden sm:block">
                {displayName}
              </span>
            )}
            {user ? (
              <div className="relative" ref={menuRef}>
                <button
                  type="button"
                  onClick={() => setMenuOpen(v => !v)}
                  className="w-8 h-8 rounded-full bg-brand-soft border border-line flex items-center justify-center hover:opacity-80 transition-opacity"
                  aria-label="使用者選單"
                >
                  <span className="text-sm font-medium text-ink select-none">
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
            ) : (
              <div className="w-8 h-8 rounded-full bg-brand-soft border border-line flex items-center justify-center">
                <span className="text-sm font-medium text-ink select-none">旅</span>
              </div>
            )}
          </div>
        </div>
      </header>
      {nicknameOpen && (
        <NicknameModal
          initialDisplayName={profile?.display_name ?? user?.displayName ?? ''}
          onClose={() => setNicknameOpen(false)}
        />
      )}
    </>
  )
}
