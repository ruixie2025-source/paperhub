import { BookOpenText, Library, MessageSquareText } from "lucide-react"
import type { ReactNode } from "react"
import { NavLink } from "react-router-dom"

import { cn } from "@/lib/utils"

type AppShellProps = {
  children: ReactNode
}

const navigation = [
  { label: "论文库", to: "/", icon: Library },
  { label: "AI 问答", to: "/ai-chat", icon: MessageSquareText },
]

export function AppShell({ children }: AppShellProps) {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <header className="sticky top-0 z-40 border-b bg-background/95 backdrop-blur">
        <div className="mx-auto flex h-14 max-w-7xl items-center gap-4 px-4 sm:px-6">
          <NavLink className="flex min-w-0 items-center gap-2" to="/">
            <span className="flex size-8 shrink-0 items-center justify-center rounded-md bg-primary text-primary-foreground">
              <BookOpenText className="size-4" />
            </span>
            <span className="min-w-0">
              <span className="block text-sm font-semibold leading-none">PaperHub</span>
              <span className="mt-1 hidden text-xs text-muted-foreground sm:block">
                论文研究工作台
              </span>
            </span>
          </NavLink>

          <nav aria-label="主导航" className="ml-auto flex items-center gap-1">
            {navigation.map(({ icon: Icon, label, to }) => (
              <NavLink
                aria-label={label}
                className={({ isActive }) =>
                  cn(
                    "inline-flex h-9 items-center gap-2 rounded-md px-3 text-sm font-medium transition-colors",
                    isActive
                      ? "bg-accent text-accent-foreground"
                      : "text-muted-foreground hover:bg-muted hover:text-foreground",
                  )
                }
                end={to === "/"}
                key={to}
                title={label}
                to={to}
              >
                <Icon className="size-4" />
                <span className="hidden sm:inline">{label}</span>
              </NavLink>
            ))}
          </nav>
        </div>
      </header>

      <main className="mx-auto w-full max-w-7xl px-4 py-6 sm:px-6 sm:py-8">
        {children}
      </main>
    </div>
  )
}
