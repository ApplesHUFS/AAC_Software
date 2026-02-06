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
        // 파트너 테마 (보라색)
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
        // 커뮤니케이터 테마 (청록색)
        communicator: {
          50: "#f0fdfa",
          100: "#ccfbf1",
          200: "#99f6e4",
          300: "#5eead4",
          400: "#2dd4bf",
          500: "#14b8a6",
          600: "#0d9488",
          700: "#0f766e",
          800: "#115e59",
          900: "#134e4a",
        },
        // 시맨틱 배경 색상
        background: "#fafafa",
        surface: "#ffffff",
        "surface-secondary": "#f5f5f5",
      },
      fontFamily: {
        sans: [
          "-apple-system",
          "BlinkMacSystemFont",
          "Segoe UI",
          "Roboto",
          "Helvetica Neue",
          "Arial",
          "sans-serif",
        ],
      },
      // 앱 스타일 그림자
      boxShadow: {
        "app-xs": "0 1px 2px rgba(0, 0, 0, 0.04)",
        "app-sm": "0 1px 3px rgba(0, 0, 0, 0.08)",
        "app-md": "0 4px 12px rgba(0, 0, 0, 0.08)",
        "app-lg": "0 8px 24px rgba(0, 0, 0, 0.12)",
        "app-card": "0 2px 8px rgba(0, 0, 0, 0.06), 0 1px 2px rgba(0, 0, 0, 0.04)",
        "app-button": "0 2px 4px rgba(0, 0, 0, 0.1)",
        "app-elevated": "0 12px 32px rgba(0, 0, 0, 0.15)",
      },
      // 앱 스타일 애니메이션
      animation: {
        "fade-in": "fadeIn 200ms ease-out",
        "fade-in-up": "fadeInUp 300ms ease-out forwards",
        "slide-up": "slideUp 300ms ease-out",
        "slide-down": "slideDown 300ms ease-out",
        "scale-in": "scaleIn 200ms ease-out",
        "bounce-in": "bounceIn 400ms cubic-bezier(0.175, 0.885, 0.32, 1.275)",
        "pulse-soft": "pulseSoft 2s ease-in-out infinite",
      },
      keyframes: {
        fadeIn: {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        fadeInUp: {
          "0%": { opacity: "0", transform: "translateY(10px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        slideUp: {
          "0%": { transform: "translateY(100%)" },
          "100%": { transform: "translateY(0)" },
        },
        slideDown: {
          "0%": { transform: "translateY(-100%)" },
          "100%": { transform: "translateY(0)" },
        },
        scaleIn: {
          "0%": { transform: "scale(0.95)", opacity: "0" },
          "100%": { transform: "scale(1)", opacity: "1" },
        },
        bounceIn: {
          "0%": { transform: "scale(0.5)", opacity: "0" },
          "50%": { transform: "scale(1.05)" },
          "100%": { transform: "scale(1)", opacity: "1" },
        },
        pulseSoft: {
          "0%, 100%": { opacity: "1" },
          "50%": { opacity: "0.7" },
        },
      },
      // 확장된 border-radius
      borderRadius: {
        "2xl": "16px",
        "3xl": "24px",
        "4xl": "32px",
      },
      // Safe area spacing
      spacing: {
        "safe-top": "env(safe-area-inset-top)",
        "safe-bottom": "env(safe-area-inset-bottom)",
        "safe-left": "env(safe-area-inset-left)",
        "safe-right": "env(safe-area-inset-right)",
      },
    },
  },
  plugins: [],
};

export default config;
