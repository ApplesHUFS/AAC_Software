/**
 * Spinner Component
 * - Gradient color from violet to pink
 * - Smooth rotation animation
 */

import { cn } from "@/lib/utils";

interface SpinnerProps {
  size?: "sm" | "md" | "lg";
  className?: string;
}

export function Spinner({ size = "md", className }: SpinnerProps) {
  const sizes = {
    sm: "w-4 h-4",
    md: "w-8 h-8",
    lg: "w-12 h-12",
  };

  const borderSizes = {
    sm: "border-2",
    md: "border-[3px]",
    lg: "border-4",
  };

  return (
    <div
      className={cn(
        "relative mx-auto",
        sizes[size],
        className
      )}
      role="status"
      aria-label="Loading"
    >
      <div
        className={cn(
          "absolute inset-0 rounded-full",
          "bg-gradient-to-r from-violet-600 to-pink-500",
          "animate-spin"
        )}
        style={{
          mask: "conic-gradient(transparent 70deg, black)",
          WebkitMask: "conic-gradient(transparent 70deg, black)",
        }}
      />
      <div
        className={cn(
          "absolute rounded-full bg-white/80",
          sizes[size]
        )}
        style={{
          inset: size === "sm" ? "2px" : size === "md" ? "3px" : "4px",
        }}
      />
      <span className="sr-only">Loading...</span>
    </div>
  );
}
