import type { InputHTMLAttributes } from 'react'

type InputProps = InputHTMLAttributes<HTMLInputElement> & {
  label?: string
  hint?: string
}

export function Input({ className, hint, id, label, ...props }: InputProps) {
  const inputId = id ?? props.name
  const classes = ['ui-input', className].filter(Boolean).join(' ')

  return (
    <label className="ui-field">
      {label ? <span className="ui-field-label">{label}</span> : null}
      <input id={inputId} className={classes} {...props} />
      {hint ? <span className="ui-field-hint">{hint}</span> : null}
    </label>
  )
}
