export default function MobileWorkspaceHeader() {
  return (
    <header className="h-14 bg-surface border-b border-line px-4 flex items-center justify-between shrink-0">
      <div className="flex flex-col min-w-0">
        <span className="text-base font-semibold text-ink truncate">京都與東京春季之旅</span>
        <span className="text-sm text-muted truncate">日本 · 2024/3/25 – 4/5</span>
      </div>
      <button className="text-sm text-muted hover:text-ink px-3 py-1.5 rounded-full border border-line hover:bg-brand-soft transition-colors">
        邀請
      </button>
    </header>
  )
}
