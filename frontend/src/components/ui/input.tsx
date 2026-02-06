/**
 * 입력 컴포넌트
 * - 아이콘 지원
 * - 앱 스타일 디자인
 */

"use client";

import { forwardRef, InputHTMLAttributes } from "react";
import Image from "next/image";
import { cn } from "@/lib/utils";

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
  leftIcon?: string;
  rightIcon?: string;
  success?: boolean;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  (
    { className, label, error, helperText, leftIcon, rightIcon, success, id, ...props },
    ref
  ) => {
    const inputId = id || label?.replace(/\s+/g, "-").toLowerCase();

    // 상태에 따른 스타일
    const getInputStyles = () => {
      if (error) {
        return "border-red-300 focus:ring-red-500 focus:border-red-500";
      }
      if (success) {
        return "border-green-300 focus:ring-green-500 focus:border-green-500";
      }
      return "border-gray-200 focus:ring-partner-500 focus:border-partner-500";
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
        <div className="relative">
          {leftIcon && (
            <div className="absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none">
              <Image
                src={leftIcon}
                alt=""
                width={20}
                height={20}
                className="opacity-60"
              />
            </div>
          )}
          <input
            ref={ref}
            id={inputId}
            className={cn(
              "w-full px-4 py-3 bg-gray-50 border rounded-xl",
              "text-gray-900 placeholder-gray-400",
              "focus:outline-none focus:ring-2 focus:bg-white",
              "disabled:bg-gray-100 disabled:cursor-not-allowed disabled:opacity-60",
              "transition-all duration-200",
              getInputStyles(),
              leftIcon && "pl-11",
              rightIcon && "pr-11",
              className
            )}
            {...props}
          />
          {rightIcon && (
            <div className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none">
              <Image
                src={rightIcon}
                alt=""
                width={20}
                height={20}
                className="opacity-60"
              />
            </div>
          )}
        </div>
        {error && (
          <p className="mt-1.5 text-sm text-red-600 flex items-center gap-1">
            {error}
          </p>
        )}
        {helperText && !error && (
          <p className="mt-1.5 text-sm text-gray-500">{helperText}</p>
        )}
      </div>
    );
  }
);

Input.displayName = "Input";
