import Button from '../../components/common/Button'
import Card from '../../components/common/Card'

const inputClass = [
  'w-full border border-line rounded-xl px-4 py-3 text-sm text-ink bg-surface',
  'focus:outline-none focus:ring-1 focus:ring-ink/20',
  'transition-colors',
].join(' ')

const labelClass = 'block text-sm font-medium text-ink mb-1.5'

export default function TripSettingsPage() {
  return (
    <div className="p-6 max-w-3xl">
      {/* Page title */}
      <div className="mb-8">
        <h2 className="font-display text-xl font-semibold text-ink">旅程設定</h2>
        <p className="text-sm text-muted mt-1">修改旅程的基本資訊。</p>
      </div>

      {/* Settings form card */}
      <Card shadow className="p-6">
        <form className="flex flex-col gap-6" onSubmit={(e) => e.preventDefault()}>
          {/* 旅程名稱 */}
          <div>
            <label className={labelClass}>旅程名稱</label>
            <input
              type="text"
              defaultValue="京都與東京春季之旅"
              className={inputClass}
            />
          </div>

          {/* 目的地 */}
          <div>
            <label className={labelClass}>目的地</label>
            <input
              type="text"
              defaultValue="日本"
              className={inputClass}
            />
          </div>

          {/* 日期 */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className={labelClass}>開始日期</label>
              <input
                type="date"
                defaultValue="2024-03-25"
                className={inputClass}
              />
            </div>
            <div>
              <label className={labelClass}>結束日期</label>
              <input
                type="date"
                defaultValue="2024-04-05"
                className={inputClass}
              />
            </div>
          </div>

          {/* 描述 */}
          <div>
            <label className={labelClass}>描述</label>
            <textarea
              rows={4}
              defaultValue="春天賞花季節，探索京都與東京的文化與美食。"
              className={[inputClass, 'resize-none'].join(' ')}
            />
          </div>

          {/* Actions */}
          <div className="flex gap-3 justify-end pt-2 border-t border-line mt-1">
            <Button type="button" variant="secondary">
              放棄變更
            </Button>
            <Button type="submit">儲存變更</Button>
          </div>
        </form>
      </Card>
    </div>
  )
}
