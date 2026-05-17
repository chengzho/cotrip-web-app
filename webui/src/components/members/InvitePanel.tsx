import { useState } from 'react'
import Button from '../common/Button'
import Card from '../common/Card'
import { createInvite, ApiError } from '../../api/index'

interface InvitePanelProps {
  tripId: string;
}

export default function InvitePanel({ tripId }: InvitePanelProps) {
  const [inviteUrl, setInviteUrl] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [copied, setCopied] = useState(false)

  async function handleCreate() {
    setLoading(true)
    setError(null)
    try {
      const invite = await createInvite(tripId)
      setInviteUrl(invite.invite_url)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : '建立邀請連結失敗，請稍後再試。')
    } finally {
      setLoading(false)
    }
  }

  async function handleCopy() {
    if (!inviteUrl) return
    try {
      await navigator.clipboard.writeText(inviteUrl)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch {
      setError('無法複製連結，請手動複製。')
    }
  }

  return (
    <Card className="p-5">
      <h3 className="font-display text-base font-semibold text-ink mb-2">邀請朋友</h3>
      <p className="text-sm text-muted mb-5 leading-relaxed">
        分享邀請連結，讓朋友加入這趟旅程，一起提案與投票。
      </p>
      {inviteUrl ? (
        <div className="flex flex-col gap-3">
          <div className="bg-surface-soft border border-line rounded-xl px-3 py-2.5">
            <p className="text-xs text-muted break-all leading-relaxed">{inviteUrl}</p>
          </div>
          <Button className="w-full" onClick={handleCopy}>
            {copied ? '已複製！' : '複製連結'}
          </Button>
        </div>
      ) : (
        <Button className="w-full" onClick={handleCreate} disabled={loading}>
          {loading ? '建立中…' : '建立邀請連結'}
        </Button>
      )}
      {error && (
        <p className="text-sm text-red-600 mt-3 text-center">{error}</p>
      )}
    </Card>
  )
}
