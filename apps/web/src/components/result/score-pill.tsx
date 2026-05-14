type ScorePillProps = {
  label: string
  value: number
}

export function ScorePill({ label, value }: ScorePillProps) {
  return (
    <div className="score-pill">
      <span className="score-pill-label">{label}</span>
      <strong>{value.toFixed(1)}</strong>
    </div>
  )
}
