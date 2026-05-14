type ProgressBarProps = {
  percent: number
}

export function ProgressBar({ percent }: ProgressBarProps) {
  return (
    <div className="progress-track" aria-label={`Progress ${percent}%`}>
      <div className="progress-fill" style={{ width: `${percent}%` }} />
    </div>
  )
}
