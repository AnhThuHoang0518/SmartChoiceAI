import * as React from "react"
import { motion, HTMLMotionProps } from "framer-motion"
import { cn } from "../../lib/utils"

export interface ButtonProps extends HTMLMotionProps<"button"> {
  variant?: "default" | "secondary" | "outline" | "ghost";
  size?: "default" | "sm" | "lg" | "icon";
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "default", size = "default", ...props }, ref) => {
    return (
      <motion.button
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        ref={ref}
        className={cn(
          "inline-flex items-center justify-center rounded-button font-semibold transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50",
          {
            "bg-primary text-white shadow-button hover:bg-primary/90": variant === "default",
            "bg-secondary text-text shadow-button hover:bg-secondary/90": variant === "secondary",
            "border-2 border-border bg-transparent hover:bg-background": variant === "outline",
            "hover:bg-border/50": variant === "ghost",
            "h-12 px-6 py-2 text-base": size === "default",
            "h-9 px-4 text-sm": size === "sm",
            "h-14 px-8 text-lg": size === "lg",
            "h-10 w-10": size === "icon",
          },
          className
        )}
        {...props}
      />
    )
  }
)
Button.displayName = "Button"

export { Button }
