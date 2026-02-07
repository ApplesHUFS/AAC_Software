/**
 * 회원가입 Step 2: 개인 정보 (이름, 나이, 성별, 장애유형)
 */

"use client";

import { PersonIcon, CalendarIcon, UserIcon, ShieldIcon } from "@/components/ui/icons";
import { Input } from "@/components/ui/input";
import { SelectField } from "../select-field";
import { DISABILITY_TYPES, GENDER_OPTIONS } from "@/lib/constants";
import { StepProps } from "./types";

export function Step2Profile({
  formData,
  setFormData,
  error,
  onNext,
  onPrev,
}: StepProps) {
  return (
    <fieldset className="space-y-4">
      <legend className="sr-only">개인 정보</legend>

      <Input
        variant="minimal"
        id="register-name"
        name="name"
        type="text"
        value={formData.name}
        onChange={(e) => setFormData({ ...formData, name: e.target.value })}
        placeholder="이름"
        label="이름"
        srOnlyLabel
        leftIcon={<PersonIcon className="w-5 h-5" />}
        autoComplete="name"
        aria-invalid={!!error}
        errorId={error ? "register-error" : undefined}
      />

      <Input
        variant="minimal"
        id="register-age"
        name="age"
        type="number"
        value={formData.age}
        onChange={(e) => setFormData({ ...formData, age: e.target.value })}
        placeholder="나이"
        label="나이"
        srOnlyLabel
        leftIcon={<CalendarIcon className="w-5 h-5" />}
        aria-invalid={!!error}
        errorId={error ? "register-error" : undefined}
      />

      <SelectField
        id="register-gender"
        name="gender"
        value={formData.gender}
        onChange={(e) => setFormData({ ...formData, gender: e.target.value })}
        options={GENDER_OPTIONS}
        placeholder="성별 선택"
        label="성별"
        icon={<UserIcon className="w-5 h-5" />}
        error={!!error}
        errorId={error ? "register-error" : undefined}
      />

      <SelectField
        id="register-disabilityType"
        name="disabilityType"
        value={formData.disabilityType}
        onChange={(e) => setFormData({ ...formData, disabilityType: e.target.value })}
        options={DISABILITY_TYPES}
        placeholder="장애 유형 선택"
        label="장애 유형"
        icon={<ShieldIcon className="w-5 h-5" />}
        error={!!error}
        errorId={error ? "register-error" : undefined}
      />

      <div className="flex gap-3">
        <button
          type="button"
          onClick={onPrev}
          className="flex-1 py-4 bg-gray-100 text-gray-700 font-semibold rounded-2xl
                     hover:bg-gray-200 active:scale-[0.98] transition-all duration-200"
        >
          이전
        </button>
        <button
          type="button"
          onClick={onNext}
          className="flex-[2] py-4 bg-violet-600 text-white font-semibold rounded-2xl
                     shadow-lg shadow-violet-500/30 hover:bg-violet-700
                     hover:shadow-xl hover:shadow-violet-500/40 hover:scale-[1.02]
                     active:scale-[0.98] transition-all duration-200"
        >
          다음
        </button>
      </div>
    </fieldset>
  );
}
