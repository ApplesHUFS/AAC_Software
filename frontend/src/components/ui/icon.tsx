/**
 * 아이콘 컴포넌트
 * - 이미지 기반 아이콘 래퍼
 * - 타입 안전한 이미지 키 지원
 */

import Image from "next/image";
import { IMAGES, ImageKey } from "@/lib/images";
import { cn } from "@/lib/utils";

interface IconProps {
  name: ImageKey;
  size?: "xs" | "sm" | "md" | "lg" | "xl";
  className?: string;
}

const sizes = {
  xs: 14,
  sm: 16,
  md: 20,
  lg: 24,
  xl: 32,
};

export function Icon({ name, size = "md", className }: IconProps) {
  const pixelSize = sizes[size];

  return (
    <Image
      src={IMAGES[name]}
      alt=""
      width={pixelSize}
      height={pixelSize}
      className={cn("flex-shrink-0", className)}
    />
  );
}

// 아이콘 컨테이너 컴포넌트
interface IconContainerProps {
  name: ImageKey;
  size?: "sm" | "md" | "lg";
  variant?: "default" | "partner" | "communicator";
  className?: string;
}

const containerSizes = {
  sm: { container: "w-10 h-10", icon: "md" as const },
  md: { container: "w-12 h-12", icon: "lg" as const },
  lg: { container: "w-14 h-14", icon: "xl" as const },
};

const containerVariants = {
  default: "bg-gray-100",
  partner: "bg-partner-50",
  communicator: "bg-communicator-50",
};

export function IconContainer({
  name,
  size = "md",
  variant = "default",
  className,
}: IconContainerProps) {
  const { container, icon } = containerSizes[size];

  return (
    <div
      className={cn(
        "flex items-center justify-center rounded-xl",
        container,
        containerVariants[variant],
        className
      )}
    >
      <Icon name={name} size={icon} />
    </div>
  );
}
