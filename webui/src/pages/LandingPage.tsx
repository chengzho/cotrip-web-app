import AvatarGroup from '../components/common/AvatarGroup'
import Badge from '../components/common/Badge'
import Button from '../components/common/Button'
import Card from '../components/common/Card'

const previewMembers = [
  { name: 'Sophie' },
  { name: 'Alex' },
  { name: 'Jordan' },
  { name: 'Riley' },
]

const previewPlaces = [
  { rank: 1, name: '伏見稻荷大社', category: '景點', votes: 4 },
  { rank: 2, name: '錦市場', category: '餐廳', votes: 3 },
  { rank: 3, name: '嵐山竹林小徑', category: '景點', votes: 2 },
]

const steps = [
  {
    num: '01',
    title: '建立旅遊群組',
    desc: '輸入旅程資訊，產生邀請連結，邀請所有朋友加入。',
  },
  {
    num: '02',
    title: '蒐集想去的地點並一起投票',
    desc: '每位成員提案想去的地點，全員投票決定優先順序。',
  },
  {
    num: '03',
    title: '產生共享行程表',
    desc: '根據投票結果一鍵產生行程，人人都能即時查看。',
  },
]

export default function LandingPage() {
  return (
    <div>
      {/* Hero */}
      <section className="max-w-5xl mx-auto px-5 pt-20 pb-16 text-center">
        <div className="inline-flex mb-6">
          <Badge variant="warm">多人旅遊規劃</Badge>
        </div>
        <h1 className="font-display text-4xl md:text-5xl font-semibold text-ink leading-[1.15] mb-6">
          一起規劃旅程，
          <br className="hidden sm:block" />
          不再被群組訊息淹沒。
        </h1>
        <p className="text-muted text-lg max-w-xl mx-auto mb-10 leading-relaxed">
          提案、投票、行程一氣呵成。
          <br className="hidden sm:block" />
          讓整個群組輕鬆完成旅遊規劃。
        </p>
        <div className="flex flex-col sm:flex-row gap-3 justify-center">
          <Button size="lg">開始規劃</Button>
          <Button variant="secondary" size="lg">
            查看運作方式
          </Button>
        </div>
      </section>

      {/* Product preview */}
      <section className="max-w-3xl mx-auto px-5 pb-20">
        <Card shadow className="overflow-hidden">
          {/* Mini workspace top bar */}
          <div className="bg-surface-soft/70 px-5 py-4 border-b border-line flex items-center justify-between gap-4">
            <div className="min-w-0">
              <p className="text-sm font-semibold text-ink truncate">
                京都與東京春季之旅
              </p>
              <p className="text-xs text-muted mt-0.5">日本 · 2024/3/25 – 4/5</p>
            </div>
            <div className="flex items-center gap-3 shrink-0">
              <AvatarGroup avatars={previewMembers} size="sm" />
              <Badge variant="warm">投票中</Badge>
            </div>
          </div>

          {/* Ranked place list */}
          <div className="p-5">
            <p className="text-xs font-semibold text-muted uppercase tracking-wider mb-4">
              群組投票 — 依票數排名
            </p>
            <div className="flex flex-col gap-2">
              {previewPlaces.map((place) => (
                <div
                  key={place.name}
                  className="flex items-center gap-3 px-4 py-3 bg-surface-soft rounded-xl"
                >
                  <span className="text-xs font-bold text-muted w-5 text-center shrink-0">
                    {place.rank}
                  </span>
                  <span className="flex-1 text-sm font-medium text-ink min-w-0 truncate">
                    {place.name}
                  </span>
                  <Badge variant="neutral">{place.category}</Badge>
                  <div className="flex items-center gap-1 shrink-0 ml-1">
                    <span className="text-sm font-semibold text-ink">
                      {place.votes}
                    </span>
                    <span className="text-xs text-muted">票</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </Card>
      </section>

      {/* How it works */}
      <section className="max-w-5xl mx-auto px-5 pb-24">
        <h2 className="font-display text-2xl md:text-3xl font-semibold text-ink text-center mb-12">
          三個步驟，輕鬆完成旅遊規劃
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          {steps.map((step) => (
            <Card key={step.num} className="p-6">
              <div className="inline-flex mb-4">
                <Badge variant="warm">{step.num}</Badge>
              </div>
              <h3 className="font-display text-base font-semibold text-ink mb-2">
                {step.title}
              </h3>
              <p className="text-sm text-muted leading-relaxed">{step.desc}</p>
            </Card>
          ))}
        </div>
      </section>
    </div>
  )
}
