import type { ReactNode, SelectHTMLAttributes } from 'react'

type SelectOption = {
  value: string
  label: ReactNode
}

type SelectFieldProps = SelectHTMLAttributes<HTMLSelectElement> & {
  label?: ReactNode
  options: SelectOption[]
}

export function SelectField({ className, label, options, ...props }: SelectFieldProps) {
  const classes = ['ui-input', className].filter(Boolean).join(' ')

  return (
    <label className="ui-field">
      {label ? <span className="ui-field-label">{label}</span> : null}
      <select className={classes} {...props}>
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </label>
  )
}
