import { type HTMLAttributes } from 'react'

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  shadow?: boolean
}

export default function Card({
  shadow = false,
  className = '',
  children,
  ...props
}: CardProps) {
  return (
    <div
      {...props}
      className={[
        'bg-surface rounded-xl border border-line',
        shadow ? 'shadow-[0_1px_4px_0_rgba(28,25,23,0.06)]' : '',
        className,
      ]
        .filter(Boolean)
        .join(' ')}
    >
      {children}
    </div>
  )
}
