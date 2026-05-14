import type { ReactNode } from 'react'

type MetricCardProps = {
  label: ReactNode
  value: ReactNode
}

export function MetricCard({ label, value }: MetricCardProps) {
  return (
    <div className="metric-card">
      <span className="metric-card-label">{label}</span>
      <strong>{value}</strong>
    </div>
  )
}
