interface LoadingStateProps {
  message?: string;
  className?: string;
}

export default function LoadingState({
  message = '載入中…',
  className = '',
}: LoadingStateProps) {
  return (
    <div
      className={[
        'flex flex-col items-center justify-center text-center py-16 px-6',
        className,
      ].join(' ')}
    >
      <div className="w-6 h-6 rounded-full border-2 border-line border-t-brand animate-spin mb-4" />
      <p className="text-sm text-muted">{message}</p>
    </div>
  )
}
