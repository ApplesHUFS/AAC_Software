/**
 * 회원가입 폼 관련 타입 정의
 */

export interface RegisterFormData {
  userId: string;
  password: string;
  passwordConfirm: string;
  name: string;
  age: string;
  gender: string;
  disabilityType: string;
  communicationCharacteristics: string;
  interestingTopics: string[];
}

export interface StepProps {
  formData: RegisterFormData;
  setFormData: React.Dispatch<React.SetStateAction<RegisterFormData>>;
  error: string;
  setError: (error: string) => void;
  onNext: () => void;
  onPrev?: () => void;
}

export interface Step1Props extends StepProps {
  idChecked: boolean;
  idAvailable: boolean;
  checkingId: boolean;
  onCheckId: () => void;
  setIdChecked: (checked: boolean) => void;
  setIdAvailable: (available: boolean) => void;
}

export interface Step3Props extends StepProps {
  isLoading: boolean;
  topicInput: string;
  setTopicInput: (value: string) => void;
  onAddTopic: () => void;
  onRemoveTopic: (topic: string) => void;
  onSubmit: (e: React.FormEvent) => void;
}
