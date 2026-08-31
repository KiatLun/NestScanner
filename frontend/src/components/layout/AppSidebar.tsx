import { NavLink } from "react-router-dom"

import {
  Bot,
  LayoutDashboard,
  History,
  Database,
  Settings,
} from "lucide-react"

const navItems = [
  {
    label: "Dashboard",
    url: "/",
    icon: LayoutDashboard,
  },
  {
    label: "Models Database",
    url: "/database",
    icon: Database,
  },
  {
    label: "History",
    url: "/history",
    icon: History,
  },
  {
    label: "Settings",
    url: "/settings",
    icon: Settings,
  },
]

export default function AppSideBar() {
  return (
    <aside className="flex h-screen w-64 flex-col border-r bg-background">
      <div className="flex h-16 items-center gap-3 border-b px-6">
        <div className="flex size-9 items-center justify-center rounded-lg bg-primary text-primary-foreground">
          <Bot className="size-5" />
        </div>

        <div>
          <p className="font-semibold">NestScanner</p>
          <p className="text-xs text-muted-foreground">
            ASR Intelligence
          </p>
        </div>
      </div>

      <nav className="flex-1 space-y-1 p-3">
        {navItems.map((item) => {
          const Icon = item.icon

          return (
            <NavLink
              key={item.label}
              to={item.url}
              end={item.url === "/"}
              className={({ isActive }) =>
                `flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors ${
                  isActive
                    ? "bg-accent font-medium text-accent-foreground"
                    : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
                }`
              }
            >
              <Icon className="size-4" />
              {item.label}
            </NavLink>
          )
        })}
      </nav>
    </aside>
  )
}