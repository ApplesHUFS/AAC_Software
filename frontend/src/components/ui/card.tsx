/**
 * 카드 레이아웃 컴포넌트
 * - 다양한 variant 지원
 * - 인터랙티브 모드 지원
 */

import { HTMLAttributes, forwardRef } from "react";
import { cn } from "@/lib/utils";

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "elevated" | "outlined";
  interactive?: boolean;
}

const cardVariants = {
  default: "bg-white shadow-app-card border border-gray-100",
  elevated: "bg-white shadow-app-lg",
  outlined: "bg-white border-2 border-gray-200",
};

export const Card = forwardRef<HTMLDivElement, CardProps>(
  ({ className, variant = "default", interactive = false, children, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          "rounded-2xl",
          cardVariants[variant],
          interactive && "card-interactive",
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

// CardHeader Props
interface CardHeaderProps extends HTMLAttributes<HTMLDivElement> {}

export const CardHeader = forwardRef<HTMLDivElement, CardHeaderProps>(
  ({ className, children, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn("px-5 py-4 border-b border-gray-100", className)}
        {...props}
      >
        {children}
      </div>
    );
  }
);

CardHeader.displayName = "CardHeader";

// CardContent Props
interface CardContentProps extends HTMLAttributes<HTMLDivElement> {}

export const CardContent = forwardRef<HTMLDivElement, CardContentProps>(
  ({ className, children, ...props }, ref) => {
    return (
      <div ref={ref} className={cn("px-5 py-4", className)} {...props}>
        {children}
      </div>
    );
  }
);

CardContent.displayName = "CardContent";

// CardFooter Props
interface CardFooterProps extends HTMLAttributes<HTMLDivElement> {}

export const CardFooter = forwardRef<HTMLDivElement, CardFooterProps>(
  ({ className, children, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn("px-5 py-4 border-t border-gray-100", className)}
        {...props}
      >
        {children}
      </div>
    );
  }
);

CardFooter.displayName = "CardFooter";
