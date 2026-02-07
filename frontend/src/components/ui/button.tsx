/**
 * Button Component
 * - Solid color backgrounds with hover/active effects
 * - Multiple variants: primary, secondary, ghost, danger
 * - Loading state with pulse animation
 */

"use client";

import { forwardRef, ButtonHTMLAttributes, ReactNode } from "react";
import Image from "next/image";
import { cn } from "@/lib/utils";
import { Spinner } from "./spinner";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "ghost" | "danger";
  size?: "sm" | "md" | "lg";
  leftIcon?: string | ReactNode;
  rightIcon?: string | ReactNode;
  isLoading?: boolean;
  fullWidth?: boolean;
}

function renderIcon(icon: string | ReactNode, size: number): ReactNode {
  if (typeof icon === "string") {
    return (
      <Image
        src={icon}
        alt=""
        width={size}
        height={size}
        className="flex-shrink-0"
      />
    );
  }
  return icon;
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      className,
      variant = "primary",
      size = "md",
      leftIcon,
      rightIcon,
      isLoading = false,
      fullWidth = false,
      disabled,
      children,
      ...props
    },
    ref
  ) => {
    const baseStyles = cn(
      "inline-flex items-center justify-center gap-2",
      "rounded-2xl font-semibold whitespace-nowrap",
      "transition-all duration-300 ease-out",
      "focus:outline-none focus:ring-2 focus:ring-offset-2",
      "disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none",
      "active:scale-[0.97]"
    );

    const variants = {
      primary: cn(
        "bg-violet-600 text-white",
        "hover:bg-violet-700 hover:shadow-lg hover:-translate-y-0.5",
        "focus:ring-violet-500",
        "shadow-md"
      ),
      secondary: cn(
        "border-2 border-violet-300 bg-white/80 backdrop-blur-sm text-violet-700",
        "hover:bg-violet-50 hover:border-violet-400 hover:shadow-lg hover:-translate-y-0.5",
        "focus:ring-violet-500"
      ),
      ghost: cn(
        "text-gray-700 bg-transparent",
        "hover:bg-white/60 hover:backdrop-blur-sm",
        "focus:ring-gray-400"
      ),
      danger: cn(
        "bg-red-500 text-white",
        "hover:bg-red-600 hover:shadow-lg hover:-translate-y-0.5",
        "focus:ring-red-500",
        "shadow-md"
      ),
    };

    const sizes = {
      sm: "h-9 px-4 text-sm",
      md: "h-11 px-5",
      lg: "h-13 px-7 text-lg",
    };

    const iconSizes = {
      sm: 16,
      md: 18,
      lg: 20,
    };

    const isDisabled = disabled || isLoading;

    return (
      <button
        ref={ref}
        className={cn(
          baseStyles,
          variants[variant],
          sizes[size],
          fullWidth && "w-full",
          isLoading && "animate-pulse",
          className
        )}
        disabled={isDisabled}
        {...props}
      >
        {isLoading ? (
          <>
            <Spinner size="sm" />
            <span>Loading...</span>
          </>
        ) : (
          <>
            {leftIcon && renderIcon(leftIcon, iconSizes[size])}
            {children}
            {rightIcon && renderIcon(rightIcon, iconSizes[size])}
          </>
        )}
      </button>
    );
  }
);

Button.displayName = "Button";
