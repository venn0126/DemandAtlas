import type { ReactNode } from 'react'

type KeyValueProps = {
  label: ReactNode
  value: ReactNode
}

export function KeyValue({ label, value }: KeyValueProps) {
  return (
    <p className="key-value">
      <span className="key-value-label">{label}:</span> <span>{value}</span>
    </p>
  )
}
