import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"

import { cn } from "@/lib/utils"

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-lg font-medium ring-offset-white transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 [&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0",
  {
    variants: {
      variant: {
        default: "bg-black text-white hover:bg-black/90 focus-visible:ring-black",
        outline: "border border-gray-300 bg-white hover:bg-gray-50 focus-visible:ring-black",
        secondary: "bg-gray-100 text-black hover:bg-gray-200 focus-visible:ring-black",
        ghost: "hover:bg-gray-100 focus-visible:ring-black",
        destructive: "bg-red-600 text-white hover:bg-red-700 focus-visible:ring-red-600",
      },
      size: {
        default: "h-10 px-4 py-2",
        sm: "h-9 rounded-md px-3 text-sm",
        lg: "h-11 rounded-md px-8",
        icon: "h-10 w-10",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, ...props }, ref) => (
    <button
      className={cn(buttonVariants({ variant, size, className }))}
      ref={ref}
      {...props}
    />
  )
)
Button.displayName = "Button"

export { Button, buttonVariants }
