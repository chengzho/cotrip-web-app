import Button from '../common/Button'

interface PublicHeaderProps {
  onSignIn?: () => void
}

export default function PublicHeader({ onSignIn }: PublicHeaderProps) {
  return (
    <header className="sticky top-0 z-30 bg-surface/90 backdrop-blur-sm border-b border-line">
      <div className="max-w-5xl mx-auto px-5 h-14 flex items-center justify-between">
        <span className="font-display text-lg font-semibold tracking-tight text-ink">
          CoTrip
        </span>
        <Button variant="secondary" size="sm" onClick={onSignIn}>
          登入
        </Button>
      </div>
    </header>
  )
}
