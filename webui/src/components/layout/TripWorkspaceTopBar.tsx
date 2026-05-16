import AvatarGroup from '../common/AvatarGroup'
import Button from '../common/Button'

const placeholderMembers = [
  { name: '旅行者' },
  { name: '好友' },
  { name: '夥伴' },
]

export default function TripWorkspaceTopBar() {
  return (
    <div className="h-16 border-b border-line bg-surface px-6 flex items-center justify-between shrink-0">
      <div className="flex flex-col min-w-0">
        <span className="text-base font-semibold text-ink truncate">京都與東京春季之旅</span>
        <span className="text-sm text-muted truncate">日本 · 2024/3/25 – 4/5</span>
      </div>
      <div className="flex items-center gap-4 ml-4 shrink-0">
        <AvatarGroup avatars={placeholderMembers} size="sm" />
        <Button variant="secondary" size="sm">邀請朋友</Button>
      </div>
    </div>
  )
}
