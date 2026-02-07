/**
 * 회원가입 입력 필드 컴포넌트
 * - 아이콘 지원
 * - 포커스 상태 애니메이션
 * - 에러 상태 표시
 */

"use client";

import { useState, ReactNode, ChangeEvent } from "react";

interface InputFieldProps {
  id: string;
  name: string;
  type: string;
  value: string;
  onChange: (e: ChangeEvent<HTMLInputElement>) => void;
  placeholder: string;
  label: string;
  icon: ReactNode;
  disabled?: boolean;
  autoComplete?: string;
  required?: boolean;
  error?: boolean;
  errorId?: string;
}

export function InputField({
  id,
  name,
  type,
  value,
  onChange,
  placeholder,
  label,
  icon,
  disabled,
  autoComplete,
  required = true,
  error,
  errorId,
}: InputFieldProps) {
  const [isFocused, setIsFocused] = useState(false);

  return (
    <div className="relative">
      <label htmlFor={id} className="sr-only">
        {label}
      </label>
      <div
        className={`absolute left-4 top-1/2 -translate-y-1/2 transition-colors duration-200
                    ${isFocused ? "text-violet-600" : "text-gray-400"}`}
        aria-hidden="true"
      >
        {icon}
      </div>
      <input
        id={id}
        name={name}
        type={type}
        value={value}
        onChange={onChange}
        onFocus={() => setIsFocused(true)}
        onBlur={() => setIsFocused(false)}
        placeholder={placeholder}
        disabled={disabled}
        autoComplete={autoComplete}
        aria-label={label}
        aria-required={required}
        aria-invalid={error}
        aria-describedby={errorId}
        className={`w-full pl-12 pr-4 py-4 bg-gray-50/50 border-2 rounded-2xl text-gray-900
                   placeholder:text-gray-400 transition-all duration-200 outline-none
                   ${
                     isFocused
                       ? "border-violet-500 ring-4 ring-violet-500/20 bg-white"
                       : "border-gray-200 hover:border-gray-300"
                   }
                   disabled:opacity-50 disabled:cursor-not-allowed`}
      />
    </div>
  );
}
