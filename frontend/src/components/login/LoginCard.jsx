import { useState } from "react";
import {
  Eye,
  EyeOff,
  LockKeyhole,
  Mail,
  ScanLine,
  ShieldCheck,
  UserRoundCog,
} from "lucide-react";
import { Button } from "../ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../ui/card";
import { Checkbox } from "../ui/checkbox";
import { Input } from "../ui/input";
import { Label } from "../ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../ui/select";

export function LoginCard() {
  const [showPassword, setShowPassword] = useState(false);
  const [role, setRole] = useState("instructor");
  const [rememberMe, setRememberMe] = useState(true);
  const [authState, setAuthState] = useState("idle");

  function handleSubmit(event) {
    event.preventDefault();
    setAuthState("loading");
    window.setTimeout(() => {
      setAuthState("success");
    }, 650);
  }

  return (
    <Card className="glass-panel relative overflow-hidden rounded-lg">
      <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-cyan-300/80 to-transparent" />
      <div className="absolute -right-16 -top-16 h-40 w-40 rounded-full bg-cyan-300/10 blur-3xl" />

      <CardHeader className="relative p-6 pb-4 sm:p-8 sm:pb-5">
        <div className="mb-6 flex items-center justify-between gap-4">
          <div className="grid h-12 w-12 place-items-center rounded-lg border border-cyan-300/25 bg-cyan-300/10">
            <ScanLine className="h-6 w-6 text-cyan-200" />
          </div>
          <div className="inline-flex items-center gap-2 rounded-md border border-emerald-300/20 bg-emerald-300/10 px-3 py-1.5 text-xs font-medium text-emerald-100">
            <ShieldCheck className="h-3.5 w-3.5" />
            Secure access
          </div>
        </div>
        <CardTitle className="text-2xl font-black tracking-normal text-white sm:text-3xl">
          Welcome back
        </CardTitle>
        <CardDescription className="mt-2 text-slate-400">
          Sign in to evaluate scripts, review AI decisions, and monitor grading quality.
        </CardDescription>
      </CardHeader>

      <CardContent className="relative p-6 pt-0 sm:p-8 sm:pt-0">
        <form className="grid gap-5" onSubmit={handleSubmit}>
          <div className="grid gap-2">
            <Label htmlFor="email">Email</Label>
            <div className="field-shell flex items-center gap-3 rounded-md px-3">
              <Mail className="h-4 w-4 text-slate-500" />
              <Input
                id="email"
                name="email"
                type="text"
                inputMode="email"
                autoComplete="email"
                placeholder="instructor@scriptsense.ai"
                className="border-0 px-0 focus-visible:ring-0 focus-visible:ring-offset-0"
                required
              />
            </div>
          </div>

          <div className="grid gap-2">
            <Label htmlFor="password">Password</Label>
            <div className="field-shell flex items-center gap-3 rounded-md px-3">
              <LockKeyhole className="h-4 w-4 text-slate-500" />
              <Input
                id="password"
                name="password"
                type={showPassword ? "text" : "password"}
                autoComplete="current-password"
                placeholder="Enter your password"
                className="border-0 px-0 focus-visible:ring-0 focus-visible:ring-offset-0"
                required
              />
              <button
                type="button"
                className="text-slate-500 transition hover:text-cyan-200"
                onClick={() => setShowPassword((value) => !value)}
                aria-label={showPassword ? "Hide password" : "Show password"}
              >
                {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </button>
            </div>
          </div>

          <div className="grid gap-2">
            <Label>Role</Label>
            <div className="field-shell flex items-center gap-3 rounded-md px-3">
              <UserRoundCog className="h-4 w-4 text-slate-500" />
              <Select value={role} onValueChange={setRole}>
                <SelectTrigger className="border-0 px-0 focus:ring-0 focus:ring-offset-0">
                  <SelectValue placeholder="Select role" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="instructor">Instructor</SelectItem>
                  <SelectItem value="ta">TA</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="flex items-center gap-2">
              <Checkbox id="remember" checked={rememberMe} onCheckedChange={setRememberMe} />
              <Label htmlFor="remember" className="cursor-pointer text-sm text-slate-300">
                Remember me
              </Label>
            </div>
            <Button type="button" variant="link" className="h-auto p-0 text-sm">
              Forgot password?
            </Button>
          </div>

          <Button type="submit" size="lg" className="mt-1 w-full">
            {authState === "loading" ? "Authenticating..." : "Login"}
          </Button>

          {authState === "success" && (
            <p className="rounded-md border border-emerald-300/20 bg-emerald-300/10 px-3 py-2 text-sm text-emerald-100">
              Mock authentication successful for {role === "instructor" ? "Instructor" : "TA"}.
            </p>
          )}

          <div className="flex items-center gap-4 py-1">
            <div className="h-px flex-1 bg-white/10" />
            <span className="text-xs font-semibold uppercase text-slate-500">OR</span>
            <div className="h-px flex-1 bg-white/10" />
          </div>

          <Button type="button" variant="secondary" size="lg" className="w-full">
            <span className="grid h-5 w-5 place-items-center rounded-full bg-white text-xs font-black text-slate-950">
              G
            </span>
            Continue with Google
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
