import type { HTMLAttributes, ReactNode } from 'react'

import { cn } from '../../lib/cn'

type MetaRowProps = HTMLAttributes<HTMLDivElement> & {
  left?: ReactNode
  right?: ReactNode
}

export function MetaRow({ className, left, right, ...props }: MetaRowProps) {
  return (
    <div className={cn('meta-row', className)} {...props}>
      {left ? <div>{left}</div> : null}
      {right ? <div>{right}</div> : null}
    </div>
  )
}
