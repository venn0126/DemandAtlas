import type { HTMLAttributes, ReactNode } from 'react'

type StackGap = 'sm' | 'md' | 'lg'

type StackProps = HTMLAttributes<HTMLDivElement> & {
  children: ReactNode
  gap?: StackGap
}

export function Stack({ children, className, gap = 'md', ...props }: StackProps) {
  const classes = [`stack-${gap}`, className].filter(Boolean).join(' ')

  return (
    <div className={classes} {...props}>
      {children}
    </div>
  )
}
