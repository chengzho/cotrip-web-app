import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import Badge from '../components/common/Badge'
import Button from '../components/common/Button'
import Card from '../components/common/Card'
import LoadingState from '../components/common/LoadingState'
import ErrorState from '../components/common/ErrorState'
import FormError from '../components/common/FormError'
import { previewInvite, joinInvite, ApiError } from '../api/index'
import { useAuth } from '../context/AuthContext'
import type { InvitePreview } from '../types/invite'

function formatDate(d: string): string {
  const [y, m, day] = d.split('-')
  return `${y}/${parseInt(m)}/${parseInt(day)}`
}

function previewErrorMessage(err: unknown): string {
  if (err instanceof ApiError) {
    if (err.errorCode === 'INVITE_EXPIRED') return '此邀請連結已過期。'
    if (err.errorCode === 'INVITE_REVOKED') return '此邀請連結已被撤銷。'
    if (err.errorCode === 'INVITE_USAGE_LIMIT_REACHED') return '此邀請連結已達使用上限。'
    if (err.isNotFound) return '找不到此邀請連結，請確認網址是否正確。'
    return err.message
  }
  return '無法載入邀請資訊，請稍後再試。'
}

function joinErrorMessage(err: unknown): string {
  if (err instanceof ApiError) {
    if (err.isConflict || err.errorCode === 'ALREADY_EXISTS') return '你已是這趟旅程的成員。'
    if (err.isUnauthorized) return '請先登入後再加入旅程。'
    if (err.errorCode === 'INVITE_EXPIRED') return '此邀請連結已過期，無法加入。'
    if (err.errorCode === 'INVITE_REVOKED') return '此邀請連結已被撤銷，無法加入。'
    if (err.errorCode === 'INVITE_USAGE_LIMIT_REACHED') return '此邀請連結已達使用上限，無法加入。'
    return err.message
  }
  return '加入旅程失敗，請稍後再試。'
}

export default function JoinInvitePage() {
  const { inviteToken } = useParams<{ inviteToken: string }>()
  const navigate = useNavigate()
  const { isAuthenticated, signIn } = useAuth()

  const [preview, setPreview] = useState<InvitePreview | null>(null)
  const [previewLoading, setPreviewLoading] = useState(!!inviteToken)
  const [previewError, setPreviewError] = useState<string | null>(
    inviteToken ? null : '邀請連結無效。'
  )
  const [joining, setJoining] = useState(false)
  const [joinError, setJoinError] = useState<string | null>(null)

  useEffect(() => {
    if (!inviteToken) return
    previewInvite(inviteToken)
      .then(setPreview)
      .catch((err: unknown) => {
        setPreviewError(previewErrorMessage(err))
      })
      .finally(() => setPreviewLoading(false))
  }, [inviteToken])

  async function handleJoin() {
    if (!inviteToken) return
    if (!isAuthenticated) {
      void signIn(window.location.pathname)
      return
    }
    setJoinError(null)
    setJoining(true)
    try {
      const trip = await joinInvite(inviteToken)
      navigate(`/trips/${trip.id}`)
    } catch (err: unknown) {
      setJoinError(joinErrorMessage(err))
    } finally {
      setJoining(false)
    }
  }

  if (previewLoading) {
    return (
      <div className="flex-1 flex items-center justify-center px-5 py-12">
        <LoadingState message="載入邀請資訊…" />
      </div>
    )
  }

  if (previewError) {
    return (
      <div className="flex-1 flex items-center justify-center px-5 py-12">
        <div className="w-full max-w-md">
          <ErrorState
            title="無法載入邀請"
            message={previewError}
            action={
              <Button variant="secondary" onClick={() => navigate('/')}>
                返回首頁
              </Button>
            }
          />
        </div>
      </div>
    )
  }

  if (!preview) return null

  const inviterInitial = preview.invited_by_display_name.charAt(0).toUpperCase()

  return (
    <div className="flex-1 flex items-center justify-center px-5 py-12">
      <div className="w-full max-w-md">
        <Card shadow className="p-8">
          {/* Invite header */}
          <div className="text-center mb-6">
            <div className="inline-flex mb-4">
              <Badge variant="warm">邀請</Badge>
            </div>
            <h1 className="font-display text-xl font-semibold text-ink leading-snug">
              你受邀加入
            </h1>
            <p className="font-display text-xl font-semibold text-ink mt-1">
              「{preview.trip_title}」
            </p>
          </div>

          {/* Trip details */}
          <div className="bg-surface-soft rounded-xl px-5 py-4 mb-5 flex flex-col gap-3">
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted">目的地</span>
              <span className="font-medium text-ink">{preview.destination}</span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted">旅遊日期</span>
              <span className="font-medium text-ink">
                {formatDate(preview.start_date)} – {formatDate(preview.end_date)}
              </span>
            </div>
          </div>

          {/* Inviter */}
          <div className="flex items-center gap-3 px-4 py-3 border border-line rounded-xl mb-5">
            <div className="w-9 h-9 rounded-full bg-brand-soft border border-line flex items-center justify-center shrink-0">
              <span className="text-sm font-semibold text-ink select-none">
                {inviterInitial}
              </span>
            </div>
            <div className="min-w-0">
              <p className="text-sm font-medium text-ink">
                {preview.invited_by_display_name} 邀請你
              </p>
              <p className="text-xs text-muted mt-0.5">加入這趟旅程一起規劃</p>
            </div>
          </div>

          {/* Supporting note */}
          <p className="text-sm text-muted text-center mb-6 leading-relaxed">
            加入後可新增想去的地點、參與投票，
            <br className="hidden sm:block" />
            一起完成共享行程表。
          </p>

          {/* Join error */}
          {joinError && <FormError message={joinError} className="mb-4" />}

          {/* Actions */}
          <div className="flex flex-col gap-3">
            <Button className="w-full" size="lg" onClick={handleJoin} disabled={joining}>
              {joining ? '加入中…' : '加入這趟旅程'}
            </Button>
            <Button
              variant="secondary"
              className="w-full"
              size="lg"
              disabled={joining}
              onClick={() => navigate('/')}
            >
              稍後再說
            </Button>
          </div>
        </Card>
      </div>
    </div>
  )
}
