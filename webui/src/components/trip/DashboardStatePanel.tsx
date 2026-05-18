import { Link } from 'react-router-dom'

interface DashboardStatePanelProps {
  variant: 'service-not-configured' | 'empty' | 'error'
  onRetry?: () => void
}

const CONTENT = {
  'service-not-configured': {
    icon: '◎',
    title: '旅程服務尚未連線',
    description:
      '前端登入已就緒，但旅程資料服務尚未部署。行程建立與載入功能將在後端上線後可用。',
  },
  empty: {
    icon: '○',
    title: '還沒有旅程',
    description: '建立第一趟旅程，邀請朋友一起規劃行程吧！',
  },
  error: {
    icon: '!',
    title: '暫時無法載入旅程',
    description: '連線旅程服務時發生問題，請確認網路連線後重試。',
  },
}

export default function DashboardStatePanel({
  variant,
  onRetry,
}: DashboardStatePanelProps) {
  const { icon, title, description } = CONTENT[variant]

  return (
    <div className="rounded-2xl border border-line bg-surface-soft px-8 py-16 flex flex-col items-center text-center">
      <div className="w-12 h-12 rounded-full bg-surface border border-line flex items-center justify-center mb-5">
        <span className="text-xl leading-none text-muted select-none">{icon}</span>
      </div>

      <h2 className="font-display text-lg font-semibold text-ink mb-2">{title}</h2>

      <p className="text-sm text-muted max-w-sm leading-relaxed">{description}</p>

      <div className="mt-7">
        {variant === 'empty' && (
          <Link
            to="/trips/new"
            className="inline-flex items-center justify-center px-5 py-2 text-sm font-medium rounded-full bg-brand text-brand-fg hover:opacity-90 transition-colors"
          >
            建立第一趟旅程
          </Link>
        )}
        {variant === 'error' && onRetry && (
          <button
            type="button"
            onClick={onRetry}
            className="inline-flex items-center justify-center px-5 py-2 text-sm font-medium rounded-full border border-line text-ink hover:bg-brand-soft transition-colors"
          >
            重新整理
          </button>
        )}
      </div>
    </div>
  )
}
