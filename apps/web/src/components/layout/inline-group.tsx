import type { HTMLAttributes, ReactNode } from 'react'

import { cn } from '../../lib/cn'

type InlineGroupVariant = 'actions' | 'badges'

type InlineGroupProps = HTMLAttributes<HTMLDivElement> & {
  children: ReactNode
  variant?: InlineGroupVariant
}

export function InlineGroup({
  children,
  className,
  variant = 'actions',
  ...props
}: InlineGroupProps) {
  return (
    <div className={cn(`inline-group-${variant}`, className)} {...props}>
      {children}
    </div>
  )
}
