import { useRef, useState } from 'react'
import { QRCodeCanvas } from 'qrcode.react'
import Button from '../common/Button'
import Card from '../common/Card'
import { createInvite, revokeInvite, ApiError } from '../../api/index'

interface InvitePanelProps {
  tripId: string;
  isOwner: boolean;
}

export default function InvitePanel({ tripId, isOwner }: InvitePanelProps) {
  const [inviteUrl, setInviteUrl] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [copied, setCopied] = useState(false)
  const [revoking, setRevoking] = useState(false)
  const [revokeSuccess, setRevokeSuccess] = useState(false)
  const qrContainerRef = useRef<HTMLDivElement>(null)

  async function handleCreate() {
    setLoading(true)
    setError(null)
    setRevokeSuccess(false)
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

  function handleDownload() {
    const canvas = qrContainerRef.current?.querySelector('canvas')
    if (!canvas) return
    const url = canvas.toDataURL('image/png')
    const a = document.createElement('a')
    a.href = url
    a.download = 'cotrip-invite-qr.png'
    a.click()
  }

  async function handleRevoke() {
    setRevoking(true)
    setError(null)
    try {
      await revokeInvite(tripId)
      setInviteUrl(null)
      setRevokeSuccess(true)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : '停用邀請連結失敗，請稍後再試。')
    } finally {
      setRevoking(false)
    }
  }

  return (
    <Card className="p-5">
      <h3 className="font-display text-base font-semibold text-ink mb-2">邀請朋友</h3>
      <p className="text-sm text-muted mb-5 leading-relaxed">
        分享邀請連結或 QR Code，讓朋友加入這趟旅程，一起提案與投票。
      </p>
      {inviteUrl ? (
        <div className="flex flex-col gap-4">
          {/* QR Code */}
          <div className="flex flex-col items-center gap-2">
            <div ref={qrContainerRef}>
              <QRCodeCanvas
                value={inviteUrl}
                size={168}
                marginSize={2}
                bgColor="#ffffff"
                fgColor="#1c1917"
              />
            </div>
            <p className="text-xs text-muted">掃描 QR Code 加入旅程</p>
          </div>

          {/* Invite link */}
          <div className="bg-surface-soft border border-line rounded-xl px-3 py-2.5">
            <p className="text-xs text-muted break-all leading-relaxed">{inviteUrl}</p>
          </div>

          {/* Copy / download actions */}
          <div className="flex gap-2">
            <Button className="flex-1" onClick={handleCopy}>
              {copied ? '已複製！' : '複製連結'}
            </Button>
            <Button variant="secondary" onClick={handleDownload} aria-label="下載 QR Code">
              下載
            </Button>
          </div>

          {/* Revoke action — owner only */}
          {isOwner && (
            <div className="border-t border-line pt-4">
              <p className="text-xs text-muted mb-3 leading-relaxed">
                停用後，已分享的舊連結與 QR Code 將無法再加入此旅程。
              </p>
              <button
                type="button"
                onClick={handleRevoke}
                disabled={revoking}
                className="w-full text-sm text-red-600 hover:text-red-700 hover:underline disabled:opacity-50 disabled:no-underline transition-colors text-left"
              >
                {revoking ? '停用中…' : '停用邀請連結'}
              </button>
            </div>
          )}
        </div>
      ) : (
        <div className="flex flex-col gap-3">
          {revokeSuccess && (
            <p className="text-sm text-green-700 text-center">邀請連結已停用</p>
          )}
          <Button className="w-full" onClick={handleCreate} disabled={loading}>
            {loading ? '建立中…' : '建立邀請連結'}
          </Button>
        </div>
      )}
      {error && (
        <p className="text-sm text-red-600 mt-3 text-center">{error}</p>
      )}
    </Card>
  )
}
