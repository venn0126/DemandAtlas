import type { HTMLAttributes, ReactNode } from 'react'

type GridVariant = 'panel' | 'template' | 'metric' | 'score' | 'result'

type GridProps = HTMLAttributes<HTMLDivElement> & {
  children: ReactNode
  variant?: GridVariant
}

export function Grid({ children, className, variant = 'panel', ...props }: GridProps) {
  const classes = [`grid-${variant}`, className].filter(Boolean).join(' ')

  return (
    <div className={classes} {...props}>
      {children}
    </div>
  )
}
