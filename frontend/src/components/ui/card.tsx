/**
 * Card Component
 * - Glassmorphism effect with backdrop blur
 * - Smooth hover lift animation
 * - Multiple variants for different use cases
 */

import { HTMLAttributes, forwardRef } from "react";
import { cn } from "@/lib/utils";

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "elevated" | "outlined";
  interactive?: boolean;
}

const cardVariants = {
  default: cn(
    "bg-white/80 backdrop-blur-xl",
    "border border-white/20",
    "shadow-lg shadow-black/5"
  ),
  elevated: cn(
    "bg-white/90 backdrop-blur-xl",
    "border border-white/30",
    "shadow-xl shadow-black/10"
  ),
  outlined: cn(
    "bg-white/60 backdrop-blur-lg",
    "border-2 border-violet-200/50"
  ),
};

export const Card = forwardRef<HTMLDivElement, CardProps>(
  ({ className, variant = "default", interactive = false, children, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          "rounded-3xl",
          cardVariants[variant],
          interactive && cn(
            "transition-all duration-300 ease-out cursor-pointer",
            "hover:-translate-y-1 hover:shadow-2xl hover:shadow-violet-500/10",
            "hover:border-violet-200/40"
          ),
          className
        )}
        {...props}
      >
        {children}
      </div>
    );
  }
);

Card.displayName = "Card";

interface CardHeaderProps extends HTMLAttributes<HTMLDivElement> {}

export const CardHeader = forwardRef<HTMLDivElement, CardHeaderProps>(
  ({ className, children, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn("px-6 py-5 border-b border-white/20", className)}
        {...props}
      >
        {children}
      </div>
    );
  }
);

CardHeader.displayName = "CardHeader";

interface CardContentProps extends HTMLAttributes<HTMLDivElement> {}

export const CardContent = forwardRef<HTMLDivElement, CardContentProps>(
  ({ className, children, ...props }, ref) => {
    return (
      <div ref={ref} className={cn("px-6 py-5", className)} {...props}>
        {children}
      </div>
    );
  }
);

CardContent.displayName = "CardContent";

interface CardFooterProps extends HTMLAttributes<HTMLDivElement> {}

export const CardFooter = forwardRef<HTMLDivElement, CardFooterProps>(
  ({ className, children, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn("px-6 py-5 border-t border-white/20", className)}
        {...props}
      >
        {children}
      </div>
    );
  }
);

CardFooter.displayName = "CardFooter";
