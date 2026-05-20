import { GraduationCap, UserRoundCog } from 'lucide-react'
import type { UserRole } from '../../types/auth'

const roles: Array<{
  value: UserRole
  label: string
  description: string
  icon: typeof GraduationCap
}> = [
  {
    value: 'PROFESSOR',
    label: 'Professor',
    description: 'Course control',
    icon: GraduationCap,
  },
  {
    value: 'TA',
    label: 'TA',
    description: 'Review queue',
    icon: UserRoundCog,
  },
]

type RoleSelectorProps = {
  value: UserRole
  onChange: (role: UserRole) => void
}

export function RoleSelector({ value, onChange }: RoleSelectorProps) {
  return (
    <fieldset className="grid gap-2">
      <legend className="text-sm font-semibold text-slate-200">Role</legend>
      <div className="grid grid-cols-2 gap-2 rounded-lg border border-white/10 bg-black/20 p-1">
        {roles.map(({ value: roleValue, label, description, icon: Icon }) => {
          const isActive = value === roleValue

          return (
            <button
              aria-pressed={isActive}
              className={`rounded-md px-3 py-3 text-left transition duration-300 ${
                isActive
                  ? 'bg-cyan-300 text-slate-950 shadow-[0_0_24px_rgba(34,211,238,0.28)]'
                  : 'text-slate-300 hover:bg-white/10 hover:text-white'
              }`}
              key={roleValue}
              onClick={() => onChange(roleValue)}
              type="button"
            >
              <span className="flex items-center gap-2 text-sm font-black">
                <Icon className="h-4 w-4" />
                {label}
              </span>
              <span className={`mt-1 block text-xs ${isActive ? 'text-slate-800' : 'text-slate-500'}`}>
                {description}
              </span>
            </button>
          )
        })}
      </div>
    </fieldset>
  )
}
