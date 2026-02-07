/**
 * Textarea Component
 * - Glassmorphism styling with backdrop blur
 * - Focus state with violet ring
 * - Error state with red glow
 */

import { forwardRef, TextareaHTMLAttributes } from "react";
import { cn } from "@/lib/utils";

interface TextareaProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  error?: string;
  helperText?: string;
}

export const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ className, label, error, helperText, id, ...props }, ref) => {
    const textareaId = id || label?.replace(/\s+/g, "-").toLowerCase();

    return (
      <div className="w-full">
        {label && (
          <label
            htmlFor={textareaId}
            className="block text-sm font-medium text-gray-700 mb-2"
          >
            {label}
          </label>
        )}
        <div className={cn(
          "relative rounded-2xl",
          error && "ring-2 ring-red-400/50 shadow-lg shadow-red-500/20"
        )}>
          <textarea
            ref={ref}
            id={textareaId}
            className={cn(
              "w-full px-4 py-3.5 rounded-2xl resize-none min-h-[120px]",
              "bg-white/60 backdrop-blur-lg",
              "border border-white/30",
              "text-gray-900 placeholder-gray-400",
              "transition-all duration-300 ease-out",
              "focus:outline-none focus:bg-white/80",
              "focus:border-transparent focus:ring-2",
              error
                ? "focus:ring-red-400/50"
                : "focus:ring-violet-500/50 focus:shadow-lg focus:shadow-violet-500/10",
              "disabled:bg-gray-100/50 disabled:cursor-not-allowed disabled:opacity-60",
              className
            )}
            {...props}
          />
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

Textarea.displayName = "Textarea";
