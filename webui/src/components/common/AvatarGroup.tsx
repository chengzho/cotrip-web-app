interface AvatarItem {
  name: string
}

interface AvatarGroupProps {
  avatars: AvatarItem[]
  max?: number
  size?: 'sm' | 'md'
  className?: string
}

const colorPool = [
  'bg-[#C2A98B]',
  'bg-[#8BA8C2]',
  'bg-[#B2C28B]',
  'bg-[#C28BB2]',
  'bg-[#8BC2C2]',
]

function initial(name: string) {
  return name.trim()[0]?.toUpperCase() ?? '?'
}

export default function AvatarGroup({
  avatars,
  max = 4,
  size = 'md',
  className = '',
}: AvatarGroupProps) {
  const visible = avatars.slice(0, max)
  const overflow = avatars.length - visible.length
  const dim = size === 'sm' ? 'w-6 h-6 text-xs' : 'w-8 h-8 text-sm'

  return (
    <div className={['flex items-center', className].join(' ')}>
      {visible.map((avatar, i) => (
        <div
          key={i}
          title={avatar.name}
          className={[
            dim,
            colorPool[i % colorPool.length],
            'rounded-full flex items-center justify-center font-medium text-white',
            'ring-2 ring-surface',
            i > 0 ? '-ml-2' : '',
          ]
            .filter(Boolean)
            .join(' ')}
        >
          {initial(avatar.name)}
        </div>
      ))}
      {overflow > 0 && (
        <div
          className={[
            dim,
            'rounded-full flex items-center justify-center font-medium',
            'bg-surface-soft text-muted -ml-2 ring-2 ring-surface',
          ].join(' ')}
        >
          +{overflow}
        </div>
      )}
    </div>
  )
}
