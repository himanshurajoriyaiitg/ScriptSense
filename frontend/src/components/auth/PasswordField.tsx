import { useState } from 'react'
import { Eye, EyeOff, LockKeyhole } from 'lucide-react'
import { TextField } from './TextField'

type PasswordFieldProps = {
  value: string
  onChange: (value: string) => void
  autoComplete: string
}

export function PasswordField({ value, onChange, autoComplete }: PasswordFieldProps) {
  const [isVisible, setIsVisible] = useState(false)

  return (
    <TextField
      autoComplete={autoComplete}
      icon={LockKeyhole}
      id="password"
      label="Password"
      minLength={6}
      onChange={(event) => onChange(event.target.value)}
      placeholder="Enter your password"
      required
      rightSlot={
        <button
          aria-label={isVisible ? 'Hide password' : 'Show password'}
          className="rounded-md p-1 text-slate-500 transition hover:bg-white/10 hover:text-cyan-100 focus:outline-none focus:ring-2 focus:ring-cyan-300/60"
          onClick={() => setIsVisible((current) => !current)}
          type="button"
        >
          {isVisible ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
        </button>
      }
      type={isVisible ? 'text' : 'password'}
      value={value}
    />
  )
}
