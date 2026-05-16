import Button from '../common/Button'
import Card from '../common/Card'

export default function InvitePanel() {
  return (
    <Card className="p-5">
      <h3 className="font-display text-base font-semibold text-ink mb-2">
        邀請朋友
      </h3>
      <p className="text-sm text-muted mb-5 leading-relaxed">
        分享邀請連結，讓朋友加入這趟旅程，一起提案與投票。
      </p>
      <Button className="w-full mb-4">建立邀請連結</Button>
      <div className="flex items-center gap-2 border border-line rounded-xl px-4 py-3 bg-surface-soft">
        <span className="text-sm text-muted flex-1 min-w-0 truncate">
          cotrip.app/join/abc123xyzABC
        </span>
        <button
          type="button"
          className="text-sm font-medium text-ink hover:bg-brand-soft px-3 py-1.5 rounded-lg transition-colors shrink-0"
        >
          複製
        </button>
      </div>
      <p className="text-sm text-muted mt-2.5">連結有效期限：7 天</p>
    </Card>
  )
}
