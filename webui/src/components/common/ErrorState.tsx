import { type ReactNode } from 'react'

interface ErrorStateProps {
  title?: string;
  message?: string;
  action?: ReactNode;
  className?: string;
}

export default function ErrorState({
  title = '發生錯誤',
  message,
  action,
  className = '',
}: ErrorStateProps) {
  return (
    <div
      className={[
        'flex flex-col items-center justify-center text-center py-16 px-6',
        className,
      ].join(' ')}
    >
      <div className="w-10 h-10 rounded-full bg-surface-soft border border-line flex items-center justify-center mb-4">
        <span className="text-muted text-lg leading-none">!</span>
      </div>
      <h3 className="text-sm font-medium text-ink mb-1">{title}</h3>
      {message && (
        <p className="text-sm text-muted max-w-xs mt-1">{message}</p>
      )}
      {action && <div className="mt-5">{action}</div>}
    </div>
  )
}
