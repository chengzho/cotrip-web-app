interface SuccessMessageProps {
  message: string;
  className?: string;
}

export default function SuccessMessage({ message, className = '' }: SuccessMessageProps) {
  return (
    <p
      className={[
        'text-sm text-green-700 rounded-lg bg-green-50 px-4 py-2.5 border border-green-200',
        className,
      ].join(' ')}
    >
      {message}
    </p>
  )
}
