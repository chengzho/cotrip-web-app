import { type ReactNode } from 'react'

type BadgeVariant = 'neutral' | 'warm' | 'active'

interface BadgeProps {
  variant?: BadgeVariant
  children: ReactNode
  className?: string
}

const variantClasses: Record<BadgeVariant, string> = {
  neutral: 'bg-surface-soft text-muted border border-line',
  warm: 'bg-brand-soft text-ink border border-line',
  active: 'bg-ink text-brand-fg border border-transparent',
}

export default function Badge({
  variant = 'neutral',
  children,
  className = '',
}: BadgeProps) {
  return (
    <span
      className={[
        'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
        variantClasses[variant],
        className,
      ]
        .filter(Boolean)
        .join(' ')}
    >
      {children}
    </span>
  )
}
