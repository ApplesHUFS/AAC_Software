/**
 * 인증 관련 타입 정의
 */

export interface User {
  userId: string;
  name: string;
  age: number;
  gender: string;
  disabilityType: string;
  communicationCharacteristics: string;
  interestingTopics: string[];
  createdAt?: string;
  updatedAt?: string;
}

export interface RegisterRequest {
  userId: string;
  name: string;
  age: number;
  gender: string;
  disabilityType: string;
  communicationCharacteristics: string;
  interestingTopics: string[];
  password: string;
}

export interface LoginRequest {
  userId: string;
  password: string;
}

export interface LoginResponse {
  userId: string;
  authenticated: boolean;
  user: Omit<User, "userId">;
}

export interface ProfileUpdateRequest {
  name?: string;
  age?: number;
  gender?: string;
  disabilityType?: string;
  communicationCharacteristics?: string;
  interestingTopics?: string[];
}

export interface ProfileUpdateResponse {
  updatedFields: string[];
}
