import type { HTMLAttributes, ReactNode } from 'react'

import { cn } from '../../lib/cn'

type SectionBlockProps = HTMLAttributes<HTMLDivElement> & {
  title?: ReactNode
  titleClassName?: string
  children: ReactNode
}

export function SectionBlock({
  children,
  className,
  title,
  titleClassName,
  ...props
}: SectionBlockProps) {
  return (
    <div className={cn('stack-md', className)} {...props}>
      {title ? <div className={titleClassName}>{title}</div> : null}
      {children}
    </div>
  )
}
