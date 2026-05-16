import Button from '../components/common/Button'
import Card from '../components/common/Card'

const inputClass = [
  'w-full border border-line rounded-xl px-4 py-2.5 text-sm text-ink bg-surface',
  'placeholder:text-muted/60',
  'focus:outline-none focus:ring-1 focus:ring-ink/20',
  'transition-colors',
].join(' ')

const labelClass = 'block text-sm font-medium text-ink mb-1.5'

export default function CreateTripPage() {
  return (
    <div className="max-w-5xl mx-auto px-5 py-10">
      <div className="max-w-lg mx-auto">
        {/* Page header */}
        <div className="mb-8">
          <h1 className="font-display text-2xl font-semibold text-ink">
            建立旅程
          </h1>
          <p className="text-sm text-muted mt-2">
            填寫基本資訊，開始邀請朋友協作規劃。
          </p>
        </div>

        {/* Form card */}
        <Card shadow className="p-6">
          <form className="flex flex-col gap-5" onSubmit={(e) => e.preventDefault()}>
            {/* 旅程名稱 */}
            <div>
              <label className={labelClass}>旅程名稱</label>
              <input
                type="text"
                placeholder="例：京都與東京春季之旅"
                className={inputClass}
              />
            </div>

            {/* 目的地 */}
            <div>
              <label className={labelClass}>目的地</label>
              <input
                type="text"
                placeholder="例：日本"
                className={inputClass}
              />
            </div>

            {/* 日期 — side by side */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className={labelClass}>開始日期</label>
                <input type="date" className={inputClass} />
              </div>
              <div>
                <label className={labelClass}>結束日期</label>
                <input type="date" className={inputClass} />
              </div>
            </div>

            {/* 描述 */}
            <div>
              <label className={labelClass}>描述</label>
              <textarea
                rows={4}
                placeholder="簡短說明這趟旅程的主題或目標（選填）"
                className={[inputClass, 'resize-none'].join(' ')}
              />
            </div>

            {/* Actions */}
            <div className="flex gap-3 justify-end pt-2 border-t border-line mt-1">
              <Button type="button" variant="secondary">
                取消
              </Button>
              <Button type="submit">建立旅程</Button>
            </div>
          </form>
        </Card>
      </div>
    </div>
  )
}
