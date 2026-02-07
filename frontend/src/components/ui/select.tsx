/**
 * Select Component
 * - Glassmorphism styling
 * - Custom dropdown arrow with gradient
 * - Smooth focus transitions
 */

import { forwardRef, SelectHTMLAttributes } from "react";
import { cn } from "@/lib/utils";

interface SelectOption {
  value: string;
  label: string;
}

interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  error?: string;
  options: SelectOption[];
  placeholder?: string;
}

export const Select = forwardRef<HTMLSelectElement, SelectProps>(
  ({ className, label, error, options, placeholder, id, ...props }, ref) => {
    const selectId = id || label?.replace(/\s+/g, "-").toLowerCase();

    return (
      <div className="w-full">
        {label && (
          <label
            htmlFor={selectId}
            className="block text-sm font-medium text-gray-700 mb-2"
          >
            {label}
          </label>
        )}
        <div className={cn(
          "relative rounded-2xl",
          error && "ring-2 ring-red-400/50 shadow-lg shadow-red-500/20"
        )}>
          <select
            ref={ref}
            id={selectId}
            className={cn(
              "w-full px-4 py-3.5 rounded-2xl appearance-none",
              "bg-white/60 backdrop-blur-lg",
              "border border-white/30",
              "text-gray-900",
              "transition-all duration-300 ease-out",
              "focus:outline-none focus:bg-white/80",
              "focus:border-transparent focus:ring-2",
              error
                ? "focus:ring-red-400/50"
                : "focus:ring-violet-500/50 focus:shadow-lg focus:shadow-violet-500/10",
              "disabled:bg-gray-100/50 disabled:cursor-not-allowed disabled:opacity-60",
              "pr-12",
              className
            )}
            {...props}
          >
            {placeholder && (
              <option value="" disabled className="text-gray-400">
                {placeholder}
              </option>
            )}
            {options.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
          <div className="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none">
            <svg
              className="w-5 h-5 text-violet-500"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M19 9l-7 7-7-7"
              />
            </svg>
          </div>
        </div>
        {error && (
          <p className="mt-2 text-sm text-red-500 flex items-center gap-1.5">
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
            {error}
          </p>
        )}
      </div>
    );
  }
);

Select.displayName = "Select";
