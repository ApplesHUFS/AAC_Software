/**
 * 홈 페이지 - 로그인으로 리다이렉트
 */

import { redirect } from "next/navigation";

export default function HomePage() {
  redirect("/auth/login");
}
