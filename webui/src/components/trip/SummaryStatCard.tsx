import Card from '../common/Card'

interface SummaryStatCardProps {
  label: string
  value: number | string
  className?: string
}

export default function SummaryStatCard({
  label,
  value,
  className = '',
}: SummaryStatCardProps) {
  return (
    <Card className={['p-5', className].filter(Boolean).join(' ')}>
      <p className="text-sm text-muted mb-1.5">{label}</p>
      <p className="font-display text-2xl font-semibold text-ink">{value}</p>
    </Card>
  )
}
