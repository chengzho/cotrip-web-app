interface FormErrorProps {
  message: string | null;
  className?: string;
}

export default function FormError({ message, className = '' }: FormErrorProps) {
  if (!message) return null;
  return (
    <p
      className={[
        'text-sm text-red-600 rounded-lg bg-red-50 px-4 py-2.5 border border-red-200',
        className,
      ].join(' ')}
    >
      {message}
    </p>
  )
}
