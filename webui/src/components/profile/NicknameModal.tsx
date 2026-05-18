import { useEffect, useRef, useState } from 'react'
import { useAuth } from '../../context/AuthContext'
import FormError from '../common/FormError'

const MAX_LEN = 50

interface NicknameModalProps {
  /** Current display name to pre-fill — caller must only render this when the modal should be open. */
  initialDisplayName: string
  onClose: () => void
}

export default function NicknameModal({ initialDisplayName, onClose }: NicknameModalProps) {
  const { updateProfile } = useAuth()
  const [value, setValue] = useState(initialDisplayName)
  const [error, setError] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    const t = setTimeout(() => inputRef.current?.focus(), 50)
    return () => clearTimeout(t)
  }, [])

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    const trimmed = value.trim()
    if (!trimmed) {
      setError('顯示名稱不能為空白')
      return
    }
    if (trimmed.length > MAX_LEN) {
      setError(`顯示名稱不能超過 ${MAX_LEN} 個字元`)
      return
    }
    setError(null)
    setSaving(true)
    try {
      await updateProfile(trimmed)
      setSaved(true)
      setTimeout(onClose, 900)
    } catch {
      setError('儲存失敗，請稍後再試。')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40"
      onMouseDown={onClose}
    >
      <div
        className="bg-surface rounded-xl border border-line shadow-lg w-full max-w-sm mx-4 p-6"
        onMouseDown={e => e.stopPropagation()}
      >
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-base font-semibold text-ink">設定顯示名稱</h2>
          <button
            type="button"
            onClick={onClose}
            className="text-lg leading-none text-muted hover:text-ink transition-colors"
            aria-label="關閉"
          >
            ✕
          </button>
        </div>
        <p className="text-sm text-muted mb-4">
          這個名稱會顯示在旅程成員、提案與邀請資訊中。
        </p>
        <form onSubmit={handleSubmit} className="flex flex-col gap-3">
          <div className="flex flex-col gap-1.5">
            <label
              htmlFor="nickname-input"
              className="text-sm font-medium text-ink"
            >
              顯示名稱
            </label>
            <input
              id="nickname-input"
              ref={inputRef}
              type="text"
              value={value}
              onChange={e => {
                setValue(e.target.value)
                setError(null)
                setSaved(false)
              }}
              disabled={saving}
              placeholder="輸入顯示名稱"
              className="w-full px-3 py-2 rounded-lg border border-line bg-background text-sm text-ink placeholder:text-muted focus:outline-none focus:ring-2 focus:ring-brand focus:ring-opacity-20 focus:border-brand disabled:opacity-50"
            />
          </div>
          {error && <FormError message={error} />}
          {saved && !error && (
            <p className="text-sm text-green-700 rounded-lg bg-green-50 px-4 py-2.5 border border-green-200">
              顯示名稱已更新
            </p>
          )}
          <div className="flex justify-end gap-2 mt-1">
            <button
              type="button"
              onClick={onClose}
              disabled={saving}
              className="px-4 py-2 text-sm text-muted hover:text-ink rounded-lg border border-line transition-colors disabled:opacity-50"
            >
              取消
            </button>
            <button
              type="submit"
              disabled={saving}
              className="px-4 py-2 text-sm font-medium rounded-lg bg-brand text-brand-fg hover:opacity-90 transition-opacity disabled:opacity-50"
            >
              {saving ? '儲存中…' : '儲存'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
