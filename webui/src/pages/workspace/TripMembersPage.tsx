import Badge from '../../components/common/Badge'
import Card from '../../components/common/Card'
import InvitePanel from '../../components/members/InvitePanel'

const members = [
  { name: 'Sophie Müller', email: 'sophie@example.com', role: '擁有者' as const },
  { name: 'Marcus Chen', email: 'marcus@example.com', role: '成員' as const },
  { name: 'Yuki Tanaka', email: 'yuki@example.com', role: '成員' as const },
  { name: 'Aiko Watanabe', email: 'aiko@example.com', role: '成員' as const },
]

type MemberRole = '擁有者' | '成員'

export default function TripMembersPage() {
  return (
    <div className="p-6 max-w-4xl">
      {/* Page title */}
      <div className="mb-6">
        <h2 className="font-display text-xl font-semibold text-ink">成員管理</h2>
        <p className="text-sm text-muted mt-1">4 位成員參與此旅程</p>
      </div>

      {/* Two-column on lg: member list (wider) + invite panel (narrower) */}
      <div className="grid grid-cols-1 lg:grid-cols-[1fr_300px] gap-5">
        {/* Member list */}
        <Card className="overflow-hidden">
          <div className="px-5 py-4 border-b border-line">
            <h3 className="text-base font-semibold text-ink">旅程成員</h3>
          </div>
          <div className="px-5">
            {members.map((member) => (
              <div
                key={member.email}
                className="flex items-center gap-4 py-5 border-b border-line last:border-0"
              >
                <div className="w-10 h-10 rounded-full bg-brand-soft border border-line flex items-center justify-center shrink-0">
                  <span className="text-sm font-semibold text-ink select-none">
                    {member.name[0]}
                  </span>
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-base font-medium text-ink truncate">
                    {member.name}
                  </p>
                  <p className="text-sm text-muted mt-0.5 truncate">{member.email}</p>
                </div>
                <Badge
                  variant={
                    (member.role as MemberRole) === '擁有者' ? 'warm' : 'neutral'
                  }
                  className="shrink-0"
                >
                  {member.role}
                </Badge>
              </div>
            ))}
          </div>
        </Card>

        {/* Invite panel */}
        <InvitePanel />
      </div>
    </div>
  )
}
