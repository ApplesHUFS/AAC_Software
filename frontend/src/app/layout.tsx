/**
 * 루트 레이아웃
 */

import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "AAC Interpreter - 개인화된 의사소통 지원",
  description: "페르소나 기반 AAC 카드 해석 시스템",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ko">
      <body
        className={`${inter.className} min-h-screen bg-slate-50 text-slate-700`}
      >
        {children}
      </body>
    </html>
  );
}
