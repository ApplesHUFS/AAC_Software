/**
 * Input Component
 * - Glassmorphism background
 * - Gradient border effect on focus
 * - Error state with red glow
 */

"use client";

import { forwardRef, InputHTMLAttributes, ReactNode } from "react";
import Image from "next/image";
import { cn } from "@/lib/utils";

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
  leftIcon?: string | ReactNode;
  rightIcon?: string | ReactNode;
  success?: boolean;
}

function renderIcon(icon: string | ReactNode): ReactNode {
  if (typeof icon === "string") {
    return (
      <Image
        src={icon}
        alt=""
        width={20}
        height={20}
        className="opacity-60"
      />
    );
  }
  return icon;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  (
    { className, label, error, helperText, leftIcon, rightIcon, success, id, ...props },
    ref
  ) => {
    const inputId = id || label?.replace(/\s+/g, "-").toLowerCase();

    const getWrapperStyles = () => {
      if (error) {
        return "ring-2 ring-red-400/50 shadow-lg shadow-red-500/20";
      }
      if (success) {
        return "ring-2 ring-green-400/50";
      }
      return "";
    };

    const getInputStyles = () => {
      const base = cn(
        "w-full px-4 py-3.5 rounded-2xl",
        "bg-white/60 backdrop-blur-lg",
        "border border-white/30",
        "text-gray-900 placeholder-gray-400",
        "transition-all duration-300 ease-out",
        "disabled:bg-gray-100/50 disabled:cursor-not-allowed disabled:opacity-60"
      );

      const focusStyles = cn(
        "focus:outline-none focus:bg-white/80",
        "focus:border-transparent focus:ring-2",
        error
          ? "focus:ring-red-400/50"
          : success
          ? "focus:ring-green-400/50"
          : "focus:ring-violet-500/50 focus:shadow-lg focus:shadow-violet-500/10"
      );

      return cn(base, focusStyles);
    };

    return (
      <div className="w-full">
        {label && (
          <label
            htmlFor={inputId}
            className="block text-sm font-medium text-gray-700 mb-2"
          >
            {label}
          </label>
        )}
        <div className={cn("relative rounded-2xl", getWrapperStyles())}>
          {leftIcon && (
            <div className="absolute left-4 top-1/2 -translate-y-1/2 pointer-events-none text-gray-500">
              {renderIcon(leftIcon)}
            </div>
          )}
          <input
            ref={ref}
            id={inputId}
            className={cn(
              getInputStyles(),
              !!leftIcon && "pl-12",
              !!rightIcon && "pr-12",
              className
            )}
            {...props}
          />
          {rightIcon && (
            <div className="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-gray-500">
              {renderIcon(rightIcon)}
            </div>
          )}
        </div>
        {error && (
          <p className="mt-2 text-sm text-red-500 flex items-center gap-1.5">
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
            {error}
          </p>
        )}
        {helperText && !error && (
          <p className="mt-2 text-sm text-gray-500">{helperText}</p>
        )}
      </div>
    );
  }
);

Input.displayName = "Input";
