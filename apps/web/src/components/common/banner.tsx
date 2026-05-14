import type { HTMLAttributes, ReactNode } from 'react'

type BannerTone = 'info' | 'success' | 'warning' | 'danger'

type BannerProps = HTMLAttributes<HTMLDivElement> & {
  title?: string
  children: ReactNode
  tone?: BannerTone
}

export function Banner({
  children,
  className,
  title,
  tone = 'info',
  ...props
}: BannerProps) {
  const classes = ['ui-banner', `ui-banner-${tone}`, className].filter(Boolean).join(' ')

  return (
    <div className={classes} {...props}>
      <div className="ui-banner-icon" aria-hidden="true">
        {tone === 'danger' ? '!' : 'i'}
      </div>
      <div className="ui-banner-body">
        {title ? <p className="ui-banner-title">{title}</p> : null}
        <div className="ui-banner-content">{children}</div>
      </div>
    </div>
  )
}
