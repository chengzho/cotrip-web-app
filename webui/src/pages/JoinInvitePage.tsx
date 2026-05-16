import Badge from '../components/common/Badge'
import Button from '../components/common/Button'
import Card from '../components/common/Card'

export default function JoinInvitePage() {
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
              「京都與東京春季之旅」
            </p>
          </div>

          {/* Trip details */}
          <div className="bg-surface-soft rounded-xl px-5 py-4 mb-5 flex flex-col gap-3">
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted">目的地</span>
              <span className="font-medium text-ink">日本</span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted">旅遊日期</span>
              <span className="font-medium text-ink">2024/3/25 – 4/5</span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted">群組成員</span>
              <span className="font-medium text-ink">4 人</span>
            </div>
          </div>

          {/* Inviter */}
          <div className="flex items-center gap-3 px-4 py-3 border border-line rounded-xl mb-5">
            <div className="w-9 h-9 rounded-full bg-brand-soft border border-line flex items-center justify-center shrink-0">
              <span className="text-sm font-semibold text-ink select-none">S</span>
            </div>
            <div className="min-w-0">
              <p className="text-sm font-medium text-ink">Sophie 邀請你</p>
              <p className="text-xs text-muted mt-0.5">加入這趟旅程一起規劃</p>
            </div>
          </div>

          {/* Supporting note */}
          <p className="text-sm text-muted text-center mb-6 leading-relaxed">
            加入後可新增想去的地點、參與投票，
            <br className="hidden sm:block" />
            一起完成共享行程表。
          </p>

          {/* Actions */}
          <div className="flex flex-col gap-3">
            <Button className="w-full" size="lg">
              加入這趟旅程
            </Button>
            <Button variant="secondary" className="w-full" size="lg">
              稍後再說
            </Button>
          </div>
        </Card>
      </div>
    </div>
  )
}
