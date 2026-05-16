export default function MobileWorkspaceHeader() {
  return (
    <header className="h-14 bg-surface border-b border-line px-4 flex items-center justify-between shrink-0">
      <div className="flex flex-col min-w-0">
        <span className="text-sm font-semibold text-ink truncate">旅程名稱</span>
        <span className="text-xs text-muted truncate">目的地</span>
      </div>
      <button className="text-sm text-muted hover:text-ink px-3 py-1.5 rounded-full border border-line hover:bg-brand-soft transition-colors">
        邀請
      </button>
    </header>
  )
}
