import * as React from "react"
import { cn } from "../../lib/utils"

export interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "success" | "warning" | "danger" | "outline";
}

function Badge({ className, variant = "default", ...props }: BadgeProps) {
  return (
    <div
      className={cn(
        "inline-flex items-center rounded-badge border px-3 py-1 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
        {
          "border-transparent bg-primary text-white": variant === "default",
          "border-transparent bg-success text-white": variant === "success",
          "border-transparent bg-warning text-white": variant === "warning",
          "border-transparent bg-danger text-white": variant === "danger",
          "text-text": variant === "outline",
        },
        className
      )}
      {...props}
    />
  )
}

export { Badge }
