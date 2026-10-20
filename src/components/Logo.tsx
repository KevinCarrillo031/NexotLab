interface LogoProps {
  size?: 'sm' | 'md' | 'lg'
  className?: string
}

export default function Logo({ size = 'md', className = '' }: LogoProps) {
  const iconW = size === 'sm' ? 36 : size === 'lg' ? 52 : 44
  const iconH = iconW * 0.65
  const textCls = size === 'sm' ? 'text-sm' : size === 'lg' ? 'text-xl' : 'text-[17px]'
  const subCls = size === 'sm' ? 'text-[9px]' : 'text-[10px]'

  return (
    <div className={`flex items-center gap-2.5 ${className}`}>
      <svg width={iconW} height={iconH} viewBox="0 0 44 28" fill="none" aria-hidden="true">
        {/* Chat bubble 1 — brand-mid green */}
        <rect x="0" y="2" width="19" height="14" rx="3" fill="#639922" />
        <rect x="3.5" y="6" width="12" height="1.5" rx="0.75" fill="#EAF3DE" />
        <rect x="3.5" y="9.5" width="8" height="1.5" rx="0.75" fill="#EAF3DE" />
        <path d="M3.5 16 L8 16 L5 21 Z" fill="#639922" />
        {/* Chat bubble 2 — brand-dark green, offset */}
        <rect x="23" y="0" width="21" height="16" rx="3" fill="#27500A" />
        <rect x="26.5" y="4.5" width="14" height="1.5" rx="0.75" fill="#EAF3DE" />
        <rect x="26.5" y="8.5" width="9" height="1.5" rx="0.75" fill="#EAF3DE" />
        <path d="M39 16 L44 16 L44 22 Z" fill="#27500A" />
      </svg>
      <div className="flex flex-col leading-none">
        <span className={`${textCls} font-medium text-brand-dark tracking-wide`}>NEXOTLAB</span>
        <span className={`${subCls} text-brand-mid mt-0.5`}>Since 2026</span>
      </div>
    </div>
  )
}
