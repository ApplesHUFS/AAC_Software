/**
 * 버튼 컴포넌트
 * - 다양한 variant와 size 지원
 * - 아이콘 및 로딩 상태 지원
 */

"use client";

import { forwardRef, ButtonHTMLAttributes, ReactNode } from "react";
import Image from "next/image";
import { cn } from "@/lib/utils";
import { Spinner } from "./spinner";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "outline" | "ghost" | "danger" | "success";
  size?: "sm" | "md" | "lg";
  leftIcon?: string | ReactNode;
  rightIcon?: string | ReactNode;
  isLoading?: boolean;
  fullWidth?: boolean;
}

// 아이콘 렌더링 헬퍼
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
      "rounded-xl font-semibold whitespace-nowrap",
      "transition-all duration-200",
      "focus:outline-none focus:ring-2 focus:ring-offset-2",
      "disabled:opacity-50 disabled:cursor-not-allowed",
      "active:scale-[0.98]"
    );

    const variants = {
      primary: cn(
        "bg-partner-600 text-white",
        "hover:bg-partner-700",
        "focus:ring-partner-500",
        "shadow-app-button hover:shadow-app-md"
      ),
      secondary: cn(
        "bg-gray-100 text-gray-900",
        "hover:bg-gray-200",
        "focus:ring-gray-500"
      ),
      outline: cn(
        "border-2 border-gray-200 bg-white text-gray-700",
        "hover:bg-gray-50 hover:border-gray-300",
        "focus:ring-gray-500"
      ),
      ghost: cn(
        "text-gray-700",
        "hover:bg-gray-100",
        "focus:ring-gray-500"
      ),
      danger: cn(
        "bg-red-600 text-white",
        "hover:bg-red-700",
        "focus:ring-red-500",
        "shadow-app-button hover:shadow-app-md"
      ),
      success: cn(
        "bg-green-600 text-white",
        "hover:bg-green-700",
        "focus:ring-green-500",
        "shadow-app-button hover:shadow-app-md"
      ),
    };

    const sizes = {
      sm: "h-9 px-3 text-sm",
      md: "h-11 px-4",
      lg: "h-13 px-6 text-lg",
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
          className
        )}
        disabled={isDisabled}
        {...props}
      >
        {isLoading ? (
          <>
            <Spinner size="sm" />
            <span>처리 중...</span>
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
