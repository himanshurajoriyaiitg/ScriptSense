import type { InputHTMLAttributes, ReactNode } from 'react'
import type { LucideIcon } from 'lucide-react'

type TextFieldProps = InputHTMLAttributes<HTMLInputElement> & {
  label: string
  icon: LucideIcon
  rightSlot?: ReactNode
}

export function TextField({ label, icon: Icon, id, rightSlot, className = '', ...props }: TextFieldProps) {
  return (
    <label className="grid gap-2" htmlFor={id}>
      <span className="text-sm font-semibold text-slate-200">{label}</span>
      <span className="glass-control flex h-12 items-center gap-3 px-3">
        <Icon className="h-4 w-4 text-slate-500" />
        <input
          className={`h-full min-w-0 flex-1 bg-transparent text-sm text-white outline-none placeholder:text-slate-600 ${className}`}
          id={id}
          {...props}
        />
        {rightSlot}
      </span>
    </label>
  )
}
