import { KeyValue } from '../common/key-value'
import { Stack } from '../layout/stack'

type TaskSummaryCardProps = {
  title: string
  rows: Array<{
    label: string
    value: string | undefined
  }>
}

export function TaskSummaryCard({ rows, title }: TaskSummaryCardProps) {
  return (
    <Stack gap="md">
      <h2>{title}</h2>
      {rows.map((row) => (
        <KeyValue key={row.label} label={row.label} value={row.value ?? '-'} />
      ))}
    </Stack>
  )
}
