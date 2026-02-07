/**
 * 회원가입 선택 필드 컴포넌트
 * - 아이콘 지원
 * - 포커스 상태 애니메이션
 * - 에러 상태 표시
 */

"use client";

import { useState, ReactNode, ChangeEvent } from "react";
import { ChevronDownIcon } from "@/components/ui/icons";

interface SelectOption {
  value: string;
  label: string;
}

interface SelectFieldProps {
  id: string;
  name: string;
  value: string;
  onChange: (e: ChangeEvent<HTMLSelectElement>) => void;
  options: readonly SelectOption[];
  placeholder: string;
  label: string;
  icon: ReactNode;
  required?: boolean;
  error?: boolean;
  errorId?: string;
}

export function SelectField({
  id,
  name,
  value,
  onChange,
  options,
  placeholder,
  label,
  icon,
  required = true,
  error,
  errorId,
}: SelectFieldProps) {
  const [isFocused, setIsFocused] = useState(false);

  return (
    <div className="relative">
      <label htmlFor={id} className="sr-only">
        {label}
      </label>
      <div
        className={`absolute left-4 top-1/2 -translate-y-1/2 transition-colors duration-200 pointer-events-none
                    ${isFocused ? "text-violet-600" : "text-gray-400"}`}
        aria-hidden="true"
      >
        {icon}
      </div>
      <select
        id={id}
        name={name}
        value={value}
        onChange={onChange}
        onFocus={() => setIsFocused(true)}
        onBlur={() => setIsFocused(false)}
        aria-label={label}
        aria-required={required}
        aria-invalid={error}
        aria-describedby={errorId}
        className={`w-full pl-12 pr-10 py-4 bg-gray-50/50 border-2 rounded-2xl text-gray-900
                   transition-all duration-200 outline-none appearance-none cursor-pointer
                   ${!value ? "text-gray-400" : ""}
                   ${
                     isFocused
                       ? "border-violet-500 ring-4 ring-violet-500/20 bg-white"
                       : "border-gray-200 hover:border-gray-300"
                   }`}
      >
        <option value="" disabled>
          {placeholder}
        </option>
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
      <div
        className={`absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none transition-colors
                    ${isFocused ? "text-violet-600" : "text-gray-400"}`}
        aria-hidden="true"
      >
        <ChevronDownIcon className="w-5 h-5" />
      </div>
    </div>
  );
}
