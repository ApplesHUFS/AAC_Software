/**
 * 회원가입 Step 1: 계정 정보 (아이디, 비밀번호)
 */

"use client";

import { UserIcon, LockIcon } from "@/components/ui/icons";
import { Input } from "@/components/ui/input";
import { Step1Props } from "./types";

export function Step1Account({
  formData,
  setFormData,
  error,
  onNext,
  idChecked,
  idAvailable,
  checkingId,
  onCheckId,
  setIdChecked,
  setIdAvailable,
}: Step1Props) {
  return (
    <fieldset className="space-y-4">
      <legend className="sr-only">계정 정보</legend>

      {/* 아이디 + 중복확인 버튼 */}
      <div className="flex gap-2">
        <div className="flex-1">
          <Input
            variant="minimal"
            id="register-userId"
            name="userId"
            type="text"
            value={formData.userId}
            onChange={(e) => {
              setFormData({ ...formData, userId: e.target.value });
              setIdChecked(false);
              setIdAvailable(false);
            }}
            placeholder="아이디"
            label="아이디"
            srOnlyLabel
            leftIcon={<UserIcon className="w-5 h-5" />}
            autoComplete="username"
            aria-invalid={!!error && !idAvailable}
            errorId={error ? "register-error" : undefined}
          />
        </div>
        <button
          type="button"
          onClick={onCheckId}
          disabled={checkingId || !formData.userId.trim()}
          className={`px-4 py-4 font-medium rounded-2xl transition-all duration-200 whitespace-nowrap
                     ${
                       idChecked && idAvailable
                         ? "bg-green-500 text-white"
                         : "bg-violet-100 text-violet-600 hover:bg-violet-200"
                     }
                     disabled:opacity-50 disabled:cursor-not-allowed`}
        >
          {checkingId ? "확인중..." : idChecked && idAvailable ? "확인됨" : "중복확인"}
        </button>
      </div>

      <Input
        variant="minimal"
        id="register-password"
        name="password"
        type="password"
        value={formData.password}
        onChange={(e) => setFormData({ ...formData, password: e.target.value })}
        placeholder="비밀번호"
        label="비밀번호"
        srOnlyLabel
        leftIcon={<LockIcon className="w-5 h-5" />}
        autoComplete="new-password"
        aria-invalid={!!error}
        errorId={error ? "register-error" : undefined}
      />

      <Input
        variant="minimal"
        id="register-passwordConfirm"
        name="passwordConfirm"
        type="password"
        value={formData.passwordConfirm}
        onChange={(e) => setFormData({ ...formData, passwordConfirm: e.target.value })}
        placeholder="비밀번호 확인"
        label="비밀번호 확인"
        srOnlyLabel
        leftIcon={<LockIcon className="w-5 h-5" />}
        autoComplete="new-password"
        aria-invalid={!!error}
        errorId={error ? "register-error" : undefined}
      />

      <button
        type="button"
        onClick={onNext}
        className="w-full py-4 bg-violet-600 text-white font-semibold rounded-2xl
                   shadow-lg shadow-violet-500/30 hover:bg-violet-700
                   hover:shadow-xl hover:shadow-violet-500/40 hover:scale-[1.02]
                   active:scale-[0.98] transition-all duration-200"
      >
        다음
      </button>
    </fieldset>
  );
}
