import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Primary: 보라-핑크 그라데이션 계열
        primary: {
          50: "#faf5ff",
          100: "#f3e8ff",
          200: "#e9d5ff",
          300: "#d8b4fe",
          400: "#c084fc",
          500: "#a855f7",
          600: "#9333ea",
          700: "#7c3aed",
          800: "#6b21a8",
          900: "#581c87",
          950: "#3b0764",
        },
        // Secondary: 시안-블루 계열
        secondary: {
          50: "#ecfeff",
          100: "#cffafe",
          200: "#a5f3fc",
          300: "#67e8f9",
          400: "#22d3ee",
          500: "#06b6d4",
          600: "#0891b2",
          700: "#0e7490",
          800: "#155e75",
          900: "#164e63",
          950: "#083344",
        },
        // Accent: 핑크 계열
        accent: {
          50: "#fdf2f8",
          100: "#fce7f3",
          200: "#fbcfe8",
          300: "#f9a8d4",
          400: "#f472b6",
          500: "#ec4899",
          600: "#db2777",
          700: "#be185d",
          800: "#9d174d",
          900: "#831843",
          950: "#500724",
        },
        // 파트너 테마 (기존 호환)
        partner: {
          50: "#faf5ff",
          100: "#f3e8ff",
          200: "#e9d5ff",
          300: "#d8b4fe",
          400: "#c084fc",
          500: "#a855f7",
          600: "#9333ea",
          700: "#7c3aed",
          800: "#6b21a8",
          900: "#581c87",
        },
        // 커뮤니케이터 테마 (기존 호환)
        communicator: {
          50: "#ecfeff",
          100: "#cffafe",
          200: "#a5f3fc",
          300: "#67e8f9",
          400: "#22d3ee",
          500: "#06b6d4",
          600: "#0891b2",
          700: "#0e7490",
          800: "#155e75",
          900: "#164e63",
        },
        // 시맨틱 배경 색상
        background: "#f8fafc",
        surface: "#ffffff",
        "surface-secondary": "#f1f5f9",
        "surface-tertiary": "#e2e8f0",
      },
      fontFamily: {
        sans: [
          "Pretendard",
          "-apple-system",
          "BlinkMacSystemFont",
          "system-ui",
          "Segoe UI",
          "Roboto",
          "Helvetica Neue",
          "Arial",
          "Noto Sans KR",
          "sans-serif",
        ],
      },
      // 레이어드 쉐도우 시스템
      boxShadow: {
        // 기본 쉐도우
        "soft-xs": "0 1px 2px rgba(0, 0, 0, 0.02), 0 1px 3px rgba(0, 0, 0, 0.03)",
        "soft-sm": "0 2px 4px rgba(0, 0, 0, 0.02), 0 2px 8px rgba(0, 0, 0, 0.04)",
        "soft-md": "0 4px 8px rgba(0, 0, 0, 0.03), 0 6px 20px rgba(0, 0, 0, 0.06)",
        "soft-lg": "0 8px 16px rgba(0, 0, 0, 0.04), 0 12px 32px rgba(0, 0, 0, 0.08)",
        "soft-xl": "0 16px 32px rgba(0, 0, 0, 0.06), 0 24px 48px rgba(0, 0, 0, 0.1)",
        "soft-2xl": "0 24px 48px rgba(0, 0, 0, 0.08), 0 32px 64px rgba(0, 0, 0, 0.12)",
        // 컬러 쉐도우
        "glow-primary": "0 4px 20px rgba(124, 58, 237, 0.25), 0 8px 32px rgba(124, 58, 237, 0.15)",
        "glow-accent": "0 4px 20px rgba(236, 72, 153, 0.25), 0 8px 32px rgba(236, 72, 153, 0.15)",
        "glow-secondary": "0 4px 20px rgba(6, 182, 212, 0.25), 0 8px 32px rgba(6, 182, 212, 0.15)",
        // 글래스 쉐도우
        glass: "0 8px 32px rgba(0, 0, 0, 0.08), inset 0 0 0 1px rgba(255, 255, 255, 0.1)",
        "glass-lg": "0 16px 48px rgba(0, 0, 0, 0.12), inset 0 0 0 1px rgba(255, 255, 255, 0.15)",
        // 기존 호환
        "app-xs": "0 1px 2px rgba(0, 0, 0, 0.04)",
        "app-sm": "0 1px 3px rgba(0, 0, 0, 0.08)",
        "app-md": "0 4px 12px rgba(0, 0, 0, 0.08)",
        "app-lg": "0 8px 24px rgba(0, 0, 0, 0.12)",
        "app-card": "0 2px 8px rgba(0, 0, 0, 0.06), 0 1px 2px rgba(0, 0, 0, 0.04)",
        "app-button": "0 2px 4px rgba(0, 0, 0, 0.1)",
        "app-elevated": "0 12px 32px rgba(0, 0, 0, 0.15)",
      },
      // Spring 기반 애니메이션
      animation: {
        // 기본 애니메이션
        "fade-in": "fadeIn 300ms cubic-bezier(0.16, 1, 0.3, 1)",
        "fade-out": "fadeOut 200ms cubic-bezier(0.16, 1, 0.3, 1)",
        "fade-in-up": "fadeInUp 400ms cubic-bezier(0.16, 1, 0.3, 1)",
        "fade-in-down": "fadeInDown 400ms cubic-bezier(0.16, 1, 0.3, 1)",
        // 슬라이드 애니메이션
        "slide-up": "slideUp 400ms cubic-bezier(0.16, 1, 0.3, 1)",
        "slide-down": "slideDown 400ms cubic-bezier(0.16, 1, 0.3, 1)",
        "slide-left": "slideLeft 400ms cubic-bezier(0.16, 1, 0.3, 1)",
        "slide-right": "slideRight 400ms cubic-bezier(0.16, 1, 0.3, 1)",
        // 스케일 애니메이션
        "scale-in": "scaleIn 300ms cubic-bezier(0.34, 1.56, 0.64, 1)",
        "scale-out": "scaleOut 200ms cubic-bezier(0.16, 1, 0.3, 1)",
        // 바운스 & 스프링
        "bounce-in": "bounceIn 500ms cubic-bezier(0.34, 1.56, 0.64, 1)",
        "spring-in": "springIn 600ms cubic-bezier(0.34, 1.56, 0.64, 1)",
        "wobble": "wobble 800ms cubic-bezier(0.34, 1.56, 0.64, 1)",
        // 연속 애니메이션
        "pulse-soft": "pulseSoft 2s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        "float": "float 3s ease-in-out infinite",
        "shimmer": "shimmer 2s linear infinite",
        "gradient-shift": "gradientShift 8s ease infinite",
        // 스피너
        "spin-slow": "spin 3s linear infinite",
      },
      keyframes: {
        fadeIn: {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        fadeOut: {
          "0%": { opacity: "1" },
          "100%": { opacity: "0" },
        },
        fadeInUp: {
          "0%": { opacity: "0", transform: "translateY(16px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        fadeInDown: {
          "0%": { opacity: "0", transform: "translateY(-16px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        slideUp: {
          "0%": { transform: "translateY(100%)", opacity: "0" },
          "100%": { transform: "translateY(0)", opacity: "1" },
        },
        slideDown: {
          "0%": { transform: "translateY(-100%)", opacity: "0" },
          "100%": { transform: "translateY(0)", opacity: "1" },
        },
        slideLeft: {
          "0%": { transform: "translateX(100%)", opacity: "0" },
          "100%": { transform: "translateX(0)", opacity: "1" },
        },
        slideRight: {
          "0%": { transform: "translateX(-100%)", opacity: "0" },
          "100%": { transform: "translateX(0)", opacity: "1" },
        },
        scaleIn: {
          "0%": { transform: "scale(0.9)", opacity: "0" },
          "100%": { transform: "scale(1)", opacity: "1" },
        },
        scaleOut: {
          "0%": { transform: "scale(1)", opacity: "1" },
          "100%": { transform: "scale(0.9)", opacity: "0" },
        },
        bounceIn: {
          "0%": { transform: "scale(0.3)", opacity: "0" },
          "50%": { transform: "scale(1.05)" },
          "70%": { transform: "scale(0.95)" },
          "100%": { transform: "scale(1)", opacity: "1" },
        },
        springIn: {
          "0%": { transform: "scale(0.5) rotate(-10deg)", opacity: "0" },
          "50%": { transform: "scale(1.1) rotate(3deg)" },
          "75%": { transform: "scale(0.95) rotate(-2deg)" },
          "100%": { transform: "scale(1) rotate(0deg)", opacity: "1" },
        },
        wobble: {
          "0%": { transform: "translateX(0)" },
          "15%": { transform: "translateX(-8px) rotate(-5deg)" },
          "30%": { transform: "translateX(6px) rotate(3deg)" },
          "45%": { transform: "translateX(-4px) rotate(-3deg)" },
          "60%": { transform: "translateX(2px) rotate(2deg)" },
          "75%": { transform: "translateX(-1px) rotate(-1deg)" },
          "100%": { transform: "translateX(0)" },
        },
        pulseSoft: {
          "0%, 100%": { opacity: "1" },
          "50%": { opacity: "0.6" },
        },
        float: {
          "0%, 100%": { transform: "translateY(0)" },
          "50%": { transform: "translateY(-8px)" },
        },
        shimmer: {
          "0%": { backgroundPosition: "-200% 0" },
          "100%": { backgroundPosition: "200% 0" },
        },
        gradientShift: {
          "0%, 100%": { backgroundPosition: "0% 50%" },
          "50%": { backgroundPosition: "100% 50%" },
        },
      },
      // 확장된 border-radius
      borderRadius: {
        "xl": "12px",
        "2xl": "16px",
        "3xl": "20px",
        "4xl": "24px",
        "5xl": "32px",
      },
      // 8px 그리드 기반 spacing
      spacing: {
        "4.5": "18px",
        "5.5": "22px",
        "6.5": "26px",
        "7.5": "30px",
        "13": "52px",
        "15": "60px",
        "17": "68px",
        "18": "72px",
        "22": "88px",
        "26": "104px",
        "30": "120px",
        "safe-top": "env(safe-area-inset-top)",
        "safe-bottom": "env(safe-area-inset-bottom)",
        "safe-left": "env(safe-area-inset-left)",
        "safe-right": "env(safe-area-inset-right)",
      },
      // 배경 그라데이션
      backgroundImage: {
        // 주요 그라데이션
        "gradient-primary": "linear-gradient(135deg, #7c3aed 0%, #ec4899 100%)",
        "gradient-secondary": "linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%)",
        "gradient-accent": "linear-gradient(135deg, #ec4899 0%, #f97316 100%)",
        // 소프트 그라데이션
        "gradient-soft-purple": "linear-gradient(135deg, #e9d5ff 0%, #fbcfe8 100%)",
        "gradient-soft-blue": "linear-gradient(135deg, #cffafe 0%, #ddd6fe 100%)",
        "gradient-soft-pink": "linear-gradient(135deg, #fce7f3 0%, #fef3c7 100%)",
        // 메시 그라데이션
        "gradient-mesh": "radial-gradient(at 40% 20%, #e9d5ff 0px, transparent 50%), radial-gradient(at 80% 0%, #cffafe 0px, transparent 50%), radial-gradient(at 0% 50%, #fbcfe8 0px, transparent 50%)",
        // 글래스 배경
        "gradient-glass": "linear-gradient(135deg, rgba(255, 255, 255, 0.4) 0%, rgba(255, 255, 255, 0.1) 100%)",
        // 오버레이
        "gradient-overlay": "linear-gradient(180deg, rgba(0, 0, 0, 0) 0%, rgba(0, 0, 0, 0.6) 100%)",
        // 시머 효과
        "shimmer": "linear-gradient(90deg, transparent 0%, rgba(255, 255, 255, 0.5) 50%, transparent 100%)",
      },
      // 배경 크기
      backgroundSize: {
        "200%": "200% 200%",
        "300%": "300% 300%",
        "400%": "400% 100%",
      },
      // 트랜지션 타이밍
      transitionTimingFunction: {
        "spring": "cubic-bezier(0.34, 1.56, 0.64, 1)",
        "smooth": "cubic-bezier(0.16, 1, 0.3, 1)",
        "bounce": "cubic-bezier(0.68, -0.55, 0.265, 1.55)",
      },
      // 백드롭 블러
      backdropBlur: {
        xs: "2px",
        "2xl": "40px",
        "3xl": "64px",
      },
    },
  },
  plugins: [],
};

export default config;
