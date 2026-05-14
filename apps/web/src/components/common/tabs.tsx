import type { ReactNode } from 'react'

type TabItem = {
  key: string
  label: ReactNode
}

type TabsProps = {
  items: TabItem[]
  value: string
  onChange: (value: string) => void
}

export function Tabs({ items, onChange, value }: TabsProps) {
  return (
    <div className="ui-tabs" role="tablist" aria-label="Tabs">
      {items.map((item) => {
        const active = item.key === value

        return (
          <button
            key={item.key}
            type="button"
            role="tab"
            aria-selected={active}
            className={active ? 'ui-tab ui-tab-active' : 'ui-tab'}
            onClick={() => onChange(item.key)}
          >
            {item.label}
          </button>
        )
      })}
    </div>
  )
}
