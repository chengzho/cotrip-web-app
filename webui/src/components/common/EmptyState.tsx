import { type ReactNode } from 'react'

interface EmptyStateProps {
  title: string
  description?: string
  action?: ReactNode
  className?: string
}

export default function EmptyState({
  title,
  description,
  action,
  className = '',
}: EmptyStateProps) {
  return (
    <div
      className={[
        'flex flex-col items-center justify-center text-center py-16 px-6',
        className,
      ].join(' ')}
    >
      <div className="w-10 h-10 rounded-full bg-surface-soft border border-line flex items-center justify-center mb-4">
        <span className="text-muted text-lg leading-none">○</span>
      </div>
      <h3 className="text-sm font-medium text-ink mb-1">{title}</h3>
      {description && (
        <p className="text-sm text-muted max-w-xs mt-1">{description}</p>
      )}
      {action && <div className="mt-5">{action}</div>}
    </div>
  )
}
