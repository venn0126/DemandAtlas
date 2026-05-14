import type { HTMLAttributes, ReactNode } from 'react'

type PageHeaderProps = HTMLAttributes<HTMLDivElement> & {
  eyebrow?: ReactNode
  title: ReactNode
  description?: ReactNode
}

export function PageHeader({
  className,
  description,
  eyebrow,
  title,
  ...props
}: PageHeaderProps) {
  const classes = ['page-header', className].filter(Boolean).join(' ')

  return (
    <div className={classes} {...props}>
      {eyebrow ? <span className="eyebrow">{eyebrow}</span> : null}
      <h1>{title}</h1>
      {description ? <p className="page-description">{description}</p> : null}
    </div>
  )
}
